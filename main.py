import httpx
import streamlit as st
from fastapi import HTTPException

def call_api(input_text: str, context: str) -> str:
    """เรียกใช้งาน API และส่งข้อความสนทนา"""
    url = "https://model.abdul.in.th/bajie/chat/completions"
    headers = {"Content-Type": "application/json"}
    full_input = {f"""{context}\n
                    User: {input_text}\n
                    Assistant:"""}
    payload = {"messages": [{"role": "user", "content": full_input}]}
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json().get("choices")[0].get("message").get("content")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
def get_context() -> str:
    """สร้าง context string จากข้อความสนทนา"""
    return "\n".join(
        f"{'User' if msg['role'] == 'user' else 'Bot'}: {msg['content']}"
        for msg in st.session_state["messages"][-5:]
    )

def new_chat():
    """เริ่มต้นการสนทนาใหม่"""
    st.session_state["messages"] = []
    st.session_state["waiting_for_response"] = False

# ตั้งค่าหน้าของ Streamlit
st.set_page_config(page_title="Educational Chatbot", layout="wide")

# ตรวจสอบและกำหนดค่าเริ่มต้นใน session_state
for key in ["messages", "waiting_for_response"]:
    if key not in st.session_state:
        st.session_state[key] = [] if key == "messages" else False

# สร้าง Sidebar
with st.sidebar:
    if st.button("New Chat"):
        new_chat()

# ส่วนติดต่อหลักของแชทบอท
st.title("🤖 Educational Chatbot")
for message in st.session_state["messages"]:
    with st.chat_message("user" if message["role"] == "user" else "assistant", avatar="😀" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

# รับอินพุตจากผู้ใช้
user_input = st.chat_input("ถามอะไรสักอย่าง...", disabled=st.session_state["waiting_for_response"])
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="😀"):
        st.markdown(user_input)
    
    st.session_state["waiting_for_response"] = True
    st.rerun()

# ส่งข้อความไปยัง API และแสดงผลลัพธ์
if st.session_state["waiting_for_response"]:
    response = call_api(st.session_state["messages"][-1]["content"], get_context())
    
    st.session_state["messages"].append({"role": "assistant", "content": response})
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(response)
    
    st.session_state["waiting_for_response"] = False
    st.rerun()
