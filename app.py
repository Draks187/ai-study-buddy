"""
AI-Powered Study Buddy
-----------------------
A single-file Streamlit app that helps students:
  1. Get complex concepts explained in simple terms
  2. Summarize long study notes into key points
  3. Generate quizzes (MCQs) on demand
  4. Generate flashcards on demand

Powered by the OpenAI API.

Run locally:
    streamlit run app.py

Author: Built with Claude
"""

import json
import os

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader

# --------------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------------

load_dotenv()

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
    layout="wide",
)

DEFAULT_MODEL = "gpt-4o-mini"


def get_client() -> OpenAI:
    """Create an OpenAI client using the key from session, env, or secrets."""
    api_key = (
        st.session_state.get("api_key")
        or os.getenv("OPENAI_API_KEY")
        or st.secrets.get("OPENAI_API_KEY", None)
        if hasattr(st, "secrets")
        else None
    )
    if not api_key:
        api_key = st.session_state.get("api_key") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def call_openai(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """Send a chat completion request and return the text (or JSON string)."""
    client = get_client()
    if client is None:
        st.error("No OpenAI API key found. Add one in the sidebar or a .env file.")
        st.stop()

    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    response = client.chat.completions.create(
        model=st.session_state.get("model", DEFAULT_MODEL),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
        **kwargs,
    )
    return response.choices[0].message.content


def extract_text_from_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    text = []
    for page in reader.pages:
        text.append(page.extract_text() or "")
    return "\n".join(text)


def get_input_text(label_prefix: str, key_prefix: str) -> str:
    """Reusable widget: let user paste text OR upload a .txt/.pdf file."""
    mode = st.radio(
        f"{label_prefix} input method",
        ["Paste text", "Upload file (.txt or .pdf)"],
        horizontal=True,
        key=f"{key_prefix}_mode",
    )
    text = ""
    if mode == "Paste text":
        text = st.text_area(
            f"{label_prefix} text",
            height=220,
            key=f"{key_prefix}_text",
            placeholder="Paste your notes or topic description here...",
        )
    else:
        uploaded = st.file_uploader(
            f"Upload {label_prefix.lower()} file",
            type=["txt", "pdf"],
            key=f"{key_prefix}_file",
        )
        if uploaded is not None:
            if uploaded.name.lower().endswith(".pdf"):
                text = extract_text_from_pdf(uploaded)
            else:
                text = uploaded.read().decode("utf-8", errors="ignore")
            with st.expander("Preview extracted text"):
                st.text(text[:3000] + ("..." if len(text) > 3000 else ""))
    return text


# --------------------------------------------------------------------------
# Sidebar — API key & model settings
# --------------------------------------------------------------------------

with st.sidebar:
    st.title("📚 Study Buddy")
    st.caption("Your AI-powered study companion")

    st.subheader("⚙️ Settings")
    default_key = os.getenv("OPENAI_API_KEY", "")
    api_key_input = st.text_input(
        "OpenAI API Key",
        value=st.session_state.get("api_key", default_key),
        type="password",
        help="Get a key at https://platform.openai.com/api-keys. "
        "You can also set OPENAI_API_KEY in a .env file instead.",
    )
    st.session_state["api_key"] = api_key_input

    model_choice = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0,
    )
    st.session_state["model"] = model_choice

    st.divider()
    st.markdown(
        "**Features**\n"
        "- 🧠 Explain any concept simply\n"
        "- 📝 Summarize study notes\n"
        "- ❓ Generate quizzes\n"
        "- 🗂️ Generate flashcards"
    )
    st.divider()
    st.caption("Built with Streamlit + OpenAI API")


# --------------------------------------------------------------------------
# Main tabs
# --------------------------------------------------------------------------

st.title("🎓 AI-Powered Study Buddy")
st.write(
    "Struggling with a tricky concept, a wall of notes, or exam prep? "
    "Pick a tool below and let AI help you study smarter."
)

tab_explain, tab_summarize, tab_quiz, tab_flashcards = st.tabs(
    ["🧠 Explain a Concept", "📝 Summarize Notes", "❓ Generate Quiz", "🗂️ Flashcards"]
)

# ---------------------------- Tab 1: Explain --------------------------------
with tab_explain:
    st.subheader("Explain a complex concept in simple terms")

    topic = st.text_input(
        "What concept, term, or question do you want explained?",
        placeholder="e.g. Newton's Second Law, mitochondria, recursion in programming...",
    )
    level = st.select_slider(
        "Explain like I'm...",
        options=["a 5-year-old", "a high schooler", "a college student", "an expert"],
        value="a high schooler",
    )
    extra = st.text_input("Anything specific you're confused about? (optional)")

    if st.button("Explain it", type="primary", key="explain_btn"):
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            with st.spinner("Thinking of the clearest way to explain this..."):
                system_prompt = (
                    "You are a friendly, patient tutor. Explain concepts clearly, "
                    "using simple language, relatable analogies, and short paragraphs. "
                    "Use markdown formatting (headers, bullet points, bold) to make it "
                    "easy to skim."
                )
                user_prompt = (
                    f"Explain the following topic as if I am {level}.\n\n"
                    f"Topic: {topic}\n"
                )
                if extra.strip():
                    user_prompt += f"\nSpecifically, I'm confused about: {extra}\n"
                user_prompt += (
                    "\nStructure your answer with:\n"
                    "1. A one-sentence summary\n"
                    "2. A simple explanation with an analogy\n"
                    "3. A short real-world example\n"
                    "4. 2-3 key takeaways as bullet points"
                )
                result = call_openai(system_prompt, user_prompt)
            st.markdown(result)

# ---------------------------- Tab 2: Summarize ------------------------------
with tab_summarize:
    st.subheader("Summarize your study notes")

    notes_text = get_input_text("Notes", "summarize")
    summary_style = st.selectbox(
        "Summary style",
        ["Concise bullet points", "Detailed outline", "One paragraph summary"],
    )

    if st.button("Summarize", type="primary", key="summarize_btn"):
        if not notes_text.strip():
            st.warning("Please paste some notes or upload a file first.")
        else:
            with st.spinner("Reading through your notes..."):
                system_prompt = (
                    "You are a study assistant that creates clear, well-organized "
                    "summaries of study notes, highlighting the most important "
                    "concepts, definitions, and facts a student needs to remember."
                )
                user_prompt = (
                    f"Summarize the following study notes in the style of: "
                    f"{summary_style}.\n\nNotes:\n{notes_text[:12000]}"
                )
                result = call_openai(system_prompt, user_prompt)
            st.markdown(result)

# ---------------------------- Tab 3: Quiz -----------------------------------
with tab_quiz:
    st.subheader("Generate a quiz on demand")

    quiz_source = get_input_text("Topic / Notes", "quiz")
    col1, col2 = st.columns(2)
    with col1:
        num_questions = st.slider("Number of questions", 3, 15, 5)
    with col2:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    if st.button("Generate Quiz", type="primary", key="quiz_btn"):
        if not quiz_source.strip():
            st.warning("Please enter a topic or paste/upload notes first.")
        else:
            with st.spinner("Writing quiz questions..."):
                system_prompt = (
                    "You are a quiz generator for students. Create multiple-choice "
                    "questions strictly based on the given topic or notes. "
                    "Respond ONLY with valid JSON, no extra commentary, matching this "
                    'schema: {"questions": [{"question": str, "options": '
                    '{"A": str, "B": str, "C": str, "D": str}, "correct": "A"|"B"|"C"|"D", '
                    '"explanation": str}]}'
                )
                user_prompt = (
                    f"Create {num_questions} {difficulty.lower()} difficulty multiple "
                    f"choice questions based on:\n\n{quiz_source[:12000]}"
                )
                raw = call_openai(system_prompt, user_prompt, json_mode=True)
                try:
                    quiz_data = json.loads(raw)
                    st.session_state["quiz_data"] = quiz_data.get("questions", [])
                    st.session_state["quiz_answers"] = {}
                except json.JSONDecodeError:
                    st.error("Couldn't parse the quiz. Please try again.")
                    st.session_state["quiz_data"] = []

    quiz_questions = st.session_state.get("quiz_data", [])
    if quiz_questions:
        st.divider()
        with st.form("quiz_form"):
            for i, q in enumerate(quiz_questions):
                st.markdown(f"**{i + 1}. {q['question']}**")
                choice = st.radio(
                    "Select an answer",
                    list(q["options"].keys()),
                    format_func=lambda k, opts=q["options"]: f"{k}. {opts[k]}",
                    key=f"quiz_q_{i}",
                    label_visibility="collapsed",
                )
                st.session_state["quiz_answers"][i] = choice
                st.write("")
            submitted = st.form_submit_button("Submit Quiz", type="primary")

        if submitted:
            score = 0
            st.divider()
            st.subheader("Results")
            for i, q in enumerate(quiz_questions):
                user_ans = st.session_state["quiz_answers"].get(i)
                correct = q["correct"]
                is_correct = user_ans == correct
                score += int(is_correct)
                icon = "✅" if is_correct else "❌"
                st.markdown(
                    f"{icon} **Q{i + 1}.** {q['question']}\n\n"
                    f"Your answer: **{user_ans}** — Correct answer: **{correct}**\n\n"
                    f"_{q.get('explanation', '')}_"
                )
            st.success(f"Score: {score} / {len(quiz_questions)}")

# ---------------------------- Tab 4: Flashcards -----------------------------
with tab_flashcards:
    st.subheader("Generate flashcards")

    fc_source = get_input_text("Topic / Notes", "flashcards")
    num_cards = st.slider("Number of flashcards", 3, 20, 8)

    if st.button("Generate Flashcards", type="primary", key="fc_btn"):
        if not fc_source.strip():
            st.warning("Please enter a topic or paste/upload notes first.")
        else:
            with st.spinner("Making flashcards..."):
                system_prompt = (
                    "You create concise study flashcards. Respond ONLY with valid "
                    'JSON matching this schema: {"cards": [{"front": str, "back": str}]}. '
                    "Keep 'front' short (a term or question) and 'back' a clear, "
                    "brief answer or definition."
                )
                user_prompt = (
                    f"Create {num_cards} flashcards based on:\n\n{fc_source[:12000]}"
                )
                raw = call_openai(system_prompt, user_prompt, json_mode=True)
                try:
                    fc_data = json.loads(raw)
                    st.session_state["flashcards"] = fc_data.get("cards", [])
                    st.session_state["fc_index"] = 0
                    st.session_state["fc_flipped"] = False
                except json.JSONDecodeError:
                    st.error("Couldn't parse flashcards. Please try again.")
                    st.session_state["flashcards"] = []

    cards = st.session_state.get("flashcards", [])
    if cards:
        st.divider()
        idx = st.session_state.get("fc_index", 0)
        flipped = st.session_state.get("fc_flipped", False)
        card = cards[idx]

        st.markdown(f"Card {idx + 1} of {len(cards)}")
        card_text = card["back"] if flipped else card["front"]
        st.markdown(
            f"""
            <div style="
                border: 2px solid #4A90E2;
                border-radius: 12px;
                padding: 60px 30px;
                text-align: center;
                font-size: 22px;
                min-height: 150px;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: #f7faff;
                color: #1a1a1a;
            ">
                {card_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("⬅️ Previous", disabled=idx == 0):
                st.session_state["fc_index"] = max(0, idx - 1)
                st.session_state["fc_flipped"] = False
                st.rerun()
        with c2:
            if st.button("🔄 Flip card"):
                st.session_state["fc_flipped"] = not flipped
                st.rerun()
        with c3:
            if st.button("Next ➡️", disabled=idx == len(cards) - 1):
                st.session_state["fc_index"] = min(len(cards) - 1, idx + 1)
                st.session_state["fc_flipped"] = False
                st.rerun()
