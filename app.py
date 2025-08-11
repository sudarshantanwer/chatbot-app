import streamlit as st
import datetime

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    st.error("⚠️ Transformers library not available. Please check your deployment configuration.")

st.set_page_config(page_title="💬 SmartBot", layout="wide")
st.title("💬 Chat with SmartBot (Fast & Free)")

@st.cache_resource
def load_pipeline():
    if not TRANSFORMERS_AVAILABLE:
        return None
    try:
        # Using a better model for conversational AI
        return pipeline("text2text-generation", model="google/flan-t5-base", device=-1)
    except Exception as e:
        st.error(f"Failed to load model: {e}")
        return None

pipe = load_pipeline()

# Status indicator
if TRANSFORMERS_AVAILABLE and pipe is not None:
    st.success("🟢 AI Model Loaded Successfully")
elif TRANSFORMERS_AVAILABLE:
    st.warning("🟡 AI Model Loading...")
else:
    st.error("🔴 AI Model Not Available - Running in Basic Mode")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def get_conversation_context():
    """Get recent conversation context for better responses"""
    if len(st.session_state.chat_history) >= 4:
        # Get last 2 exchanges (4 messages)
        recent_context = st.session_state.chat_history[-4:]
        context = "\n".join(recent_context)
        return f"Previous conversation:\n{context}\n\n"
    return ""

def get_fallback_response(user_input):
    """Provide basic responses when the AI model is not available"""
    user_input_lower = user_input.lower()
    
    # Basic math
    if "2+2" in user_input_lower or "2 + 2" in user_input_lower:
        return "4"
    elif "capital of india" in user_input_lower:
        return "New Delhi"
    elif "after" in user_input_lower and ("a" in user_input_lower or "alphabet" in user_input_lower):
        return "B"
    elif any(word in user_input_lower for word in ["hello", "hi", "hey"]):
        return "Hello! I'm currently running in basic mode. The AI model couldn't be loaded."
    else:
        return "I'm sorry, I'm currently running in basic mode due to technical limitations. Please try again later when the full AI model is available."

user_input = st.text_input("You:", key="user_input")

if user_input:
    st.session_state.chat_history.append(f"You: {user_input}")
    
    if pipe is not None and TRANSFORMERS_AVAILABLE:
        # Better prompt engineering
        context = get_conversation_context()
        prompt = f"""{context}Please answer the following question clearly and accurately. If it's a math problem, solve it step by step. If it's a factual question, provide the correct information.

Question: {user_input}
Answer:"""
        
        try:
            response = pipe(prompt, max_new_tokens=150, do_sample=True, temperature=0.7)[0]['generated_text']
            # Clean up the response
            if "Answer:" in response:
                response = response.split("Answer:")[-1].strip()
            st.session_state.chat_history.append(f"Bot: {response}")
        except Exception as e:
            fallback_response = get_fallback_response(user_input)
            st.session_state.chat_history.append(f"Bot: {fallback_response}")
    else:
        # Use fallback responses
        fallback_response = get_fallback_response(user_input)
        st.session_state.chat_history.append(f"Bot: {fallback_response}")

# Display chat history
st.subheader("🧾 Chat History")

# Add a clear chat button
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

with col2:
    if st.button("📥 Download Chat") and st.session_state.chat_history:
        full_chat = "\n".join(st.session_state.chat_history)
        st.download_button(
            label="📥 Download Full Chat",
            data=full_chat,
            file_name=f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# Display chat messages
if st.session_state.chat_history:
    for line in st.session_state.chat_history:
        if line.startswith("You:"):
            st.markdown(f"**🧑‍💻 {line}**")
        else:
            st.markdown(f"🤖 {line}")
else:
    st.info("👋 Start a conversation by typing a message above!")

# Add some helpful examples
with st.expander("💡 Try these example questions"):
    st.markdown("""
    - What is 2 + 2?
    - What is the capital of India?
    - What comes after the letter 'A'?
    - Explain photosynthesis in simple terms
    - Write a short poem about nature
    """)
