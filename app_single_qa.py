import os
from datetime import datetime
from typing import List, Dict

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# ---------- Config & Gemini client ----------
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY is not set in .env")
    st.stop()

# Configure Gemini client
genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

SUBJECTS = ["Math", "Science", "Programming", "English"]

EXAMPLE_QUESTIONS: Dict[str, List[str]] = {
    "Math": [
        "How do I solve quadratic equations?",
        "What is the Pythagorean theorem?",
        "Explain derivatives in calculus.",
    ],
    "Science": [
        "What is Newton's second law?",
        "How does photosynthesis work?",
        "Explain the water cycle.",
    ],
    "Programming": [
        "What is a recursive function?",
        "Explain object-oriented programming.",
        "What is Big O notation?",
    ],
    "English": [
        "How do I write a thesis statement?",
        "What is the difference between simile and metaphor?",
        "Explain active vs passive voice.",
    ],
}


def ask_single_question(question: str, subject: str) -> str:
    system_prompt = (
        f"You are a helpful academic tutor specializing in {subject}. "
        "Answer student questions clearly and concisely."
    )

    full_prompt = f"{system_prompt}\n\nStudent question: {question}"

    try:
        response = gemini_model.generate_content(full_prompt)
        return getattr(response, "text", str(response)) or "No response."
    except Exception as e:
        return f"Error from Gemini API: {e}"


# ---------- Streamlit app ----------
st.set_page_config(
    page_title="AI Tuition Assistant (Q&A)",
    page_icon="🎓",
    layout="wide",
)

# Title / description
st.title("🎓 AI Tuition Assistant - Q&A")
st.caption("Ask questions. No uploads, no RAG, just a simple Q&A.")

# Session state for latest Q&A
if "answer" not in st.session_state:
    st.session_state.answer = None

if "question" not in st.session_state:
    st.session_state.question = None

if "timestamp" not in st.session_state:
    st.session_state.timestamp = None

if "subject" not in st.session_state:
    st.session_state.subject = SUBJECTS[0]

# Sidebar: subject + examples
with st.sidebar:
    st.header("Tutor settings")

    subject = st.selectbox(
        "Subject",
        SUBJECTS,
        index=SUBJECTS.index(st.session_state.subject),
    )
    st.session_state.subject = subject

    st.markdown("### Example questions")

    for q in EXAMPLE_QUESTIONS[subject]:
        if st.button(q, key=f"example-{q}"):
            st.session_state.question = q

    st.markdown("---")
    st.info("Ask as many questions as you like.", icon="💡")

# Main section
st.subheader(f"Q&A - {st.session_state.subject}")

# Input
placeholder_text = f"Ask a {st.session_state.subject} question..."
user_input = st.text_area(
    "Your question",
    value=st.session_state.question or "",
    placeholder=placeholder_text,
)

ask_button = st.button("Ask", disabled=not user_input.strip())

# Handle question
if ask_button:
    question = user_input.strip()
    if question:
        with st.spinner("Thinking..."):
            answer = ask_single_question(question, st.session_state.subject)
            st.session_state.answer = answer
            st.session_state.question = question
            st.session_state.timestamp = datetime.now()

# Show latest result
if st.session_state.answer:
    st.markdown("### Result")
    st.markdown(f"**Question:** {st.session_state.question}")
    st.markdown(f"**Subject:** {st.session_state.subject}")
    st.markdown("---")
    st.markdown(st.session_state.answer)

    if st.session_state.timestamp:
        st.caption(
            f"Answered at {st.session_state.timestamp.strftime('%H:%M')}"
        )