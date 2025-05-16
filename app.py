import streamlit as st
from transformers import pipeline
import datetime

st.set_page_config(page_title="💬 SmartBot", layout="wide")
st.title("💬 Chat with SmartBot (Fast & Free)")

@st.cache_resource
def load_pipeline():
    return pipeline("text2text-generation", model="google/flan-t5-small", device=-1)

pipe = load_pipeline()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("You:", key="user_input")

if user_input:
    st.session_state.chat_history.append(f"You: {user_input}")
    response = pipe(f"Instruction: {user_input}", max_new_tokens=100)[0]['generated_text']
    st.session_state.chat_history.append(f"Bot: {response.strip()}")

# Display chat history
st.subheader("🧾 Chat History")
for line in st.session_state.chat_history:
    st.markdown(line)

# Download chat
if st.button("📥 Download Full Chat"):
    full_chat = "\n".join(st.session_state.chat_history)
    st.download_button(
        label="Download Chat",
        data=full_chat,
        file_name=f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )
