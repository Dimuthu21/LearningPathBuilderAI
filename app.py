import streamlit as st
from gemini_agent import generate_learning_path
from youtube_tool import search_youtube
from github_tool import search_github_repos
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import re  # Added for JSON extraction

# === Load API Key and Configure Gemini ===
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Helper function to extract JSON from model responses
def extract_json_from_text(text):
    pattern = r'```json(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return matches[0].strip()
    return text

# === Streamlit UI Settings ===
st.set_page_config(page_title="📚 AI-Powered Learning Chatbot", layout="wide")
st.title("📚 AI-Powered Learning Chatbot")
st.markdown("Type a topic to start. First message will give you a learning roadmap. Then continue chatting!")

# === Session State Initialization ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "topic_context" not in st.session_state:
    st.session_state.topic_context = ""
if "roadmap_given" not in st.session_state:
    st.session_state.roadmap_given = False
if "chat_summary" not in st.session_state:
    st.session_state.chat_summary = ""
if "show_quiz" not in st.session_state:
    st.session_state.show_quiz = False
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:  # Added for quiz state tracking
    st.session_state.quiz_answers = {}

# === Chat Bubble Colors ===
theme_bg = st.get_option("theme.base")
if theme_bg == "dark":
    USER_BUBBLE = "background-color:rgba(10, 115, 115, 0.9); color:#FFFFFF; padding:8px; border-radius:10px; margin:4px; max-width:70%; float:right;"
    BOT_BUBBLE = "background-color:rgba(26, 26, 26, 0.95); color:#FFFFFF; padding:8px; border-radius:10px; margin:4px; max-width:70%; float:left;"
else:
    USER_BUBBLE = "background-color:#DCF8C6; color:#000000; padding:8px; border-radius:10px; margin:4px; max-width:70%; float:right;"
    BOT_BUBBLE = "background-color:#F1F0F0; color:#000000; padding:8px; border-radius:10px; margin:4px; max-width:70%; float:left;"

# === Step 1: Generate Roadmap ===
if not st.session_state.roadmap_given:
    topic = st.text_input("Enter a topic to start:", placeholder="e.g., Artificial Intelligence")
    if st.button("Generate Learning Plan") and topic.strip() != "":
        try:
            with st.spinner("Generating roadmap..."):
                roadmap = generate_learning_path(topic)
                youtube_videos = search_youtube(topic)
                github_repos = search_github_repos(topic)

            st.session_state.topic_context = topic
            st.session_state.roadmap_given = True

            # Combine all responses into one message
            yt_text = "\n".join([f"- [{title}]({url})" for title, url in youtube_videos])
            gh_text = "\n".join([f"- [{name}]({url})" for name, url in github_repos])
            
            full_response = (
                f"**🎯 Personalized {topic} Learning Roadmap**\n\n{roadmap}\n\n"
                f"🎥 **Top YouTube Tutorials**\n\n{yt_text}\n\n"
                f"💻 **Top GitHub Projects**\n\n{gh_text}"
            )
            
            st.session_state.chat_history.append(("Gemini", full_response))
            st.success("✅ Roadmap generated! You can now chat below 👇")

        except Exception as e:
            st.error(f"❌ Failed to generate roadmap: {e}")

# === Step 2: Chat + Quiz Features ===
if st.session_state.roadmap_given:
    st.markdown("### 💬 Chat")

    # Display chat history
    for sender, message in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"<div style='{USER_BUBBLE}'><b>{message}</b></div><div style='clear:both'></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='{BOT_BUBBLE}'>{message}</div><div style='clear:both'></div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🎓 Start Skill Quiz"):
        st.session_state.show_quiz = True
        st.session_state.quiz_questions = []
        st.session_state.quiz_answers = {}  # Reset previous answers

    if st.session_state.show_quiz:
        st.markdown("### 📝 Skill Assessment Quiz")
        difficulty = st.selectbox("Select difficulty:", ["Easy", "Medium", "Hard"])
        num_q = st.slider("Number of questions:", 1, 5, 3)

        if st.button("Generate Quiz"):
            prompt = f"""
Generate {num_q} {difficulty.lower()} level multiple-choice questions on {st.session_state.topic_context}.
Return output strictly as a JSON array with this structure:
[
  {{
    "question": "string",
    "options": ["A. option1", "B. option2", "C. option3", "D. option4"],
    "answer": "A",
    "explanation": "string"
  }}
]
"""
            try:
                with st.spinner("Creating quiz..."):
                    output = model.generate_content(prompt).text
                    # Extract JSON from response
                    json_str = extract_json_from_text(output)
                    st.session_state.quiz_questions = json.loads(json_str)
            except json.JSONDecodeError:
                st.error("⚠️ Quiz format error. Please regenerate.")
                st.session_state.quiz_questions = []
            except Exception as e:
                st.error(f"❌ Quiz error: {e}")
                st.session_state.quiz_questions = []

        # === Display Questions from JSON ===
        if st.session_state.quiz_questions:
            for i, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Question {i+1}: {q.get('question','No question')}**")
                
                # Create unique key for each question
                options = q.get("options", [])
                key = f"quiz_{i}"
                
                # Store user selection in session state
                if key not in st.session_state.quiz_answers:
                    st.session_state.quiz_answers[key] = None
                
                # Display radio buttons
                user_choice = st.radio(
                    "Select an answer:", 
                    options, 
                    key=key,
                    index=None if st.session_state.quiz_answers[key] is None else options.index(st.session_state.quiz_answers[key])
                )
                
                # Update session state with user's selection
                if user_choice:
                    st.session_state.quiz_answers[key] = user_choice
                
                # Check answer button
                if st.button(f"Check Answer {i+1}", key=f"check_{i}"):
                    correct_answer = q.get("answer", "")
                    user_answer = st.session_state.quiz_answers[key]
                    
                    if not correct_answer or not user_answer:
                        st.warning("⚠️ Please select an answer first.")
                    else:
                        # Extract the letter from selected option (e.g., "A" from "A. Option text")
                        user_letter = user_answer[0] if user_answer else ""
                        
                        if user_letter == correct_answer:
                            st.success("✅ Correct!")
                        else:
                            st.error(f"❌ Incorrect! Correct answer: {correct_answer}")
                        st.info(q.get("explanation", ""))

    # === Follow-Up Chat ===
    user_question = st.chat_input("Ask a follow-up question...")
    if user_question:
        st.session_state.chat_history.append(("You", user_question))
        
        # Prepare context for Gemini
        last_n = 5
        recent_chat = "\n".join([f"{s}: {m}" for s, m in st.session_state.chat_history[-last_n*2:]])
        condensed = st.session_state.chat_summary
        
        prompt = f"""
You are an AI tutor helping with topic: {st.session_state.topic_context}

Previous summary:
{condensed}

Recent chat:
{recent_chat}

Now user asks: \"{user_question}\"

Give clear, concise, helpful response."""
        try:
            with st.spinner("Gemini is thinking..."):
                response = model.generate_content(prompt)
                st.session_state.chat_history.append(("Gemini", response.text))
                
                # Update summary periodically
                if len(st.session_state.chat_history) % 6 == 0:
                    summary_prompt = f"Summarize this chat in 3-5 lines:\n{recent_chat}"
                    summary_resp = model.generate_content(summary_prompt)
                    st.session_state.chat_summary = summary_resp.text.strip()
        except Exception as e:
            st.error(f"❌ Gemini failed to respond: {e}")
            st.session_state.chat_history.append(("Gemini", "Sorry, I encountered an error. Please try again."))
        
        st.rerun()