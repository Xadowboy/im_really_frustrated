#!/usr/bin/env python3
"""
Family Wellness Web App using Streamlit
Now supports Gemini 1.5 API Keys (v1 model)
Includes journaling, feedback, and image input
"""

import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Family Wellness AI Platform",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# AI Personalities
PERSONALITIES = {
    'sage': {
        'name': '🧠 Sage',
        'role': 'Youth Mental Health Counselor',
        'description': 'For teenagers and young adults (mental health, academics)',
        'prompt': """You are Sage, a supportive AI counselor for Indian youth aged 13-25. You understand academic pressure, family expectations, and cultural challenges. Always:
- Provide empathetic, non-judgmental support
- Recognize signs of serious mental health concerns
- Offer practical coping strategies rooted in Indian context
- Bridge communication gaps between youth and families
- Use encouraging, culturally sensitive language"""
    },
    'nurture': {
        'name': '🧱 Nurture',
        'role': 'Parenting Guide',
        'description': 'For parents and guardians (parenting strategies)',
        'prompt': """You are Nurture, an experienced parenting guide for Indian families. You understand diverse family structures, cultural values, and developmental science. Always:
- Provide evidence-based parenting strategies
- Respect cultural traditions while promoting healthy development
- Adapt advice for different socioeconomic contexts
- Support parents' mental health and well-being
- Offer practical, actionable guidance"""
    },
    'spark': {
        'name': '✨ Spark',
        'role': 'Child Development Specialist',
        'description': 'For child development activities and learning',
        'prompt': """You are Spark, a child development specialist creating engaging, age-appropriate activities. You understand Indian cultural contexts and diverse learning needs. Always:
- Design inclusive activities for all abilities
- Incorporate cultural elements and local resources
- Provide clear, step-by-step instructions
- Suggest modifications for special needs
- Make learning fun and engaging"""
    },
    'bridge': {
        'name': '🌉 Bridge',
        'role': 'Family Communication Mediator',
        'description': 'For family communication and conflict resolution',
        'prompt': """You are Bridge, a family communication specialist helping resolve conflicts and improve understanding. Always:
- Remain neutral and understanding
- Suggest practical communication strategies
- Help different generations understand each other
- Provide conflict resolution techniques
- Support healthy family dynamics"""
    }
}

# Session state defaults
for key in ["messages", "personality", "chat_session", "api_key_valid", "model", "journal", "feedback"]:
    if key not in st.session_state:
        st.session_state[key] = None if key not in ["messages", "journal", "feedback"] else []
if st.session_state.personality is None:
    st.session_state.personality = "sage"

# Validate API key using Gemini 1.5 Flash (v1 endpoint)
def validate_api_key(api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        _ = model.generate_content("Hello")
        return True, model
    except Exception as e:
        return False, str(e)

def initialize_chat_session(personality_key):
    if not st.session_state.model:
        return False
    personality = PERSONALITIES[personality_key]
    st.session_state.chat_session = st.session_state.model.start_chat(history=[
        {"role": "user", "parts": ["Hello, I need help with family wellness and development."]},
        {"role": "model", "parts": [f"{personality['prompt']}\n\nHello! I'm {personality['name']}, your {personality['role']}. How can I support you today?"]}
    ])
    return True

def check_crisis_keywords(text):
    return any(k in text.lower() for k in ['suicide', 'kill myself', 'end it all', 'hurt myself', 'die', 'worthless'])

def get_crisis_response():
    return """🚨 I'm concerned about what you've shared. Your feelings are valid, but help is available.

**Please reach out immediately:**
- **India - Suicide Prevention**: 104 (24/7)
- **KIRAN Mental Health**: 1800-599-0019
- **Vandrevala Foundation**: 9999666555
- **iCall Psychosocial Helpline**: 9152987821

You don't have to face this alone. Would you like to talk about what's making you feel this way?"""

# Title and API key setup
st.title("🏠 Family Wellness AI Platform")
st.markdown("*Powered by Gemini 1.5 API - Bring Your Own Key*")

if not st.session_state.api_key_valid:
    st.header("🔑 Setup Your API Key")
    with st.expander("📝 How to Get Your Google API Key", expanded=True):
        st.markdown("""
        1. Visit [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
        2. Sign in with your Google account
        3. Click "Create API Key"
        4. Paste the key below
        """)
    api_key = st.text_input("Enter your Google API Key:", type="password")
    if st.button("🚀 Validate & Start"):
        valid, result = validate_api_key(api_key)
        if valid:
            st.session_state.api_key_valid = True
            st.session_state.model = result
            st.success("✅ API key validated!")
            st.rerun()
        else:
            st.error(f"❌ Invalid API key: {result}")
    st.stop()

# Layout
col1, col2 = st.columns([1, 3])

with col1:
    st.header("🤖 AI Assistants")
    for key, val in PERSONALITIES.items():
        if st.button(f"{val['name']}\n{val['description']}", key=key, use_container_width=True):
            if key != st.session_state.personality:
                st.session_state.personality = key
                st.session_state.messages = []
                st.session_state.chat_session = None
                st.rerun()

    st.markdown("---")
    with st.expander("📊 Quick Assessment"):
        age = st.selectbox("Age Group:", ["13-17", "18-25", "Parent/Guardian", "Other"])
        concern = st.selectbox("Primary Concern:", ["Mental health", "Academic stress", "Parenting", "Child development", "Family communication"])
        mood = st.slider("Mood (1-10):", 1, 10, 5)
        if st.button("Get Recommendation"):
            rec = 'bridge'
            if age in ["13-17", "18-25"] and concern in ["Mental health", "Academic stress"]:
                rec = 'sage'
            elif age == "Parent/Guardian" and concern in ["Parenting", "Child development"]:
                rec = 'nurture'
            elif concern == "Child development":
                rec = 'spark'
            if rec != st.session_state.personality:
                st.session_state.personality = rec
                st.session_state.messages = []
                st.session_state.chat_session = None
                st.success(f"Switched to {PERSONALITIES[rec]['name']}")
                st.rerun()

    st.markdown("---")
    with st.expander("🚘 Crisis Resources"):
        st.markdown(get_crisis_response())

    with st.expander("📓 Journal Log"):
        journal_note = st.text_area("Write your daily reflection:")
        if st.button("Save Entry"):
            st.session_state.journal.append((datetime.now().strftime("%Y-%m-%d %H:%M"), journal_note))
            st.success("Journal entry saved!")
        for entry in reversed(st.session_state.journal):
            st.markdown(f"**{entry[0]}**\n> {entry[1]}")

    with st.expander("📈 Feedback"):
        fb = st.text_area("Share your feedback:")
        if st.button("Submit Feedback"):
            st.session_state.feedback.append((datetime.now().strftime("%Y-%m-%d %H:%M"), fb))
            st.success("Feedback submitted!")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()
    if st.button("🔄 Change API Key", use_container_width=True):
        for key in ["api_key_valid", "model", "messages", "chat_session"]:
            st.session_state[key] = None if key != "messages" else []
        st.rerun()

with col2:
    p = PERSONALITIES[st.session_state.personality]
    st.subheader(f"💬 Chat with {p['name']}")
    st.caption(f"Your {p['role']}")
    if st.session_state.chat_session is None:
        if initialize_chat_session(st.session_state.personality):
            st.session_state.messages.append({"role": "assistant", "content": f"Hello! I'm {p['name']}, your {p['role']}. How can I support you today?"})

    container = st.container(height=400)
    with container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    uploaded_image = st.file_uploader("Add an image (optional)", type=["jpg", "jpeg", "png"])

    if prompt := st.chat_input("Type your message here..."):
        with container:
            with st.chat_message("user"):
                st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        if check_crisis_keywords(prompt):
            response = get_crisis_response()
        else:
            try:
                with st.spinner("Thinking..."):
                    inputs = [prompt]
                    if uploaded_image:
                        import PIL.Image
                        img = PIL.Image.open(uploaded_image)
                        inputs.append(img)
                    response = st.session_state.chat_session.send_message(inputs).text
            except Exception as e:
                response = f"Error: {e}"

        with container:
            with st.chat_message("assistant"):
                st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🌟 Family Wellness & Development Platform | Powered by Gemini 1.5 Flash</p>
    <p>🔐 Your API key is used securely during this session</p>
    <p>✨ Take care of your family's mental health, one chat at a time.</p>
</div>
""", unsafe_allow_html=True)
