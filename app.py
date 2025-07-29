import streamlit as st
from gemini_agent import generate_learning_path
from youtube_tool import search_youtube
from github_tool import search_github_repos
import google.generativeai as genai
import os
from dotenv import load_dotenv

# === Load API Key and Configure Gemini ===
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")

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

# === Chat Bubble Colors (Dark/Light mode friendly) ===
theme_bg = st.get_option("theme.base")
if theme_bg == "dark":
    USER_BUBBLE = (
        "background-color:rgba(10, 115, 115, 0.9); color:#FFFFFF; "
        "padding:8px; border-radius:10px; margin:4px; max-width:70%; float:right;"
    )
    BOT_BUBBLE = (
        "background-color:rgba(26, 26, 26, 0.95); color:#FFFFFF; "
        "padding:8px; border-radius:10px; margin:4px; max-width:70%; float:left;"
    )
else:
    USER_BUBBLE = (
        "background-color:#DCF8C6; color:#000000; "
        "padding:8px; border-radius:10px; margin:4px; max-width:70%; float:right;"
    )
    BOT_BUBBLE = (
        "background-color:#F1F0F0; color:#000000; "
        "padding:8px; border-radius:10px; margin:4px; max-width:70%; float:left;"
    )

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

            # Store roadmap & resources in chat
            st.session_state.chat_history.append(("Gemini", f"**🗺️ Personalized {topic} Learning Roadmap**\n\n{roadmap}"))
            yt_text = "\n".join([f"- [{title}]({url})" for title, url in youtube_videos])
            st.session_state.chat_history.append(("Gemini", f"🎥 **Top YouTube Tutorials**\n\n{yt_text}"))
            gh_text = "\n".join([f"- [{name}]({url})" for name, url in github_repos])
            st.session_state.chat_history.append(("Gemini", f"💻 **Top GitHub Projects**\n\n{gh_text}"))
            st.success("✅ Roadmap generated! You can now chat below 👇")

        except Exception as e:
            st.error(f"❌ Failed to generate roadmap: {e}")

# === Step 2: Display Chat + Chat Input ===
if st.session_state.roadmap_given:
    st.markdown("### 💬 Chat")

    # Display chat bubbles
    for sender, message in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"<div style='{USER_BUBBLE}'>{message}</div><div style='clear:both'></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='{BOT_BUBBLE}'>{message}</div><div style='clear:both'></div>", unsafe_allow_html=True)

    # Chat input (clears automatically)
    user_question = st.chat_input("Ask a follow-up question...")

    if user_question:
        # Save user question
        st.session_state.chat_history.append(("You", user_question))

        # Limit context & summarization
        last_n = 5
        recent_chat = "\n".join([f"{s}: {m}" for s, m in st.session_state.chat_history[-last_n * 2:]])
        condensed = st.session_state.chat_summary

        prompt = f"""
You are an AI tutor helping with topic: {st.session_state.topic_context}

Previous summary:
{condensed}

Recent chat:
{recent_chat}

Now user asks: "{user_question}"

Give clear, concise, helpful response.
"""
        try:
            with st.spinner("Gemini is thinking..."):
                response = model.generate_content(prompt)
                st.session_state.chat_history.append(("Gemini", response.text))

                # Update summary every 6 messages
                if len(st.session_state.chat_history) % 6 == 0:
                    summary_prompt = f"Summarize this chat in 3-5 lines:\n{recent_chat}"
                    summary_resp = model.generate_content(summary_prompt)
                    st.session_state.chat_summary = summary_resp.text.strip()

        except Exception as e:
            st.error(f"❌ Gemini failed to respond: {e}")

        st.rerun()
