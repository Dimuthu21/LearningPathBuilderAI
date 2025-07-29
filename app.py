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

# === Topic Input UI ===
if not st.session_state.roadmap_given:
    topic = st.text_input("Enter a topic to start:", placeholder="e.g., Artificial Intelligence")
    if st.button("Generate Learning Plan") and topic.strip() != "":
        with st.spinner("Generating roadmap..."):
            roadmap = generate_learning_path(topic)
            youtube_videos = search_youtube(topic)
            github_repos = search_github_repos(topic)

        # Save context
        st.session_state.topic_context = topic
        st.session_state.roadmap_given = True

        # Store Gemini's first message in history
        st.session_state.chat_history.append(("Gemini", f"**🗺️ Personalized {topic} Learning Roadmap:**\n\n{roadmap}"))
        yt_list = "\n".join([f"- [{title}]({url})" for title, url in youtube_videos])
        st.session_state.chat_history.append(("Gemini", f"🎥 **Top 5 YouTube Tutorials:**\n\n{yt_list}"))
        gh_list = "\n".join([f"- [{name}]({url})" for name, url in github_repos])
        st.session_state.chat_history.append(("Gemini", f"💻 **Top 5 GitHub Projects:**\n\n{gh_list}"))
        st.success("✅ Roadmap generated! You can now chat below 👇")

# === Display Chat History and Follow-Up Questions ===
if st.session_state.roadmap_given:
    st.markdown("---")
    st.markdown("### 💬 Chat with Gemini")

    for sender, message in st.session_state.chat_history:
        if sender == "You":
            st.markdown(
                f"<div style='font-size:17px; font-weight:600; color:#0066cc'>🧍‍♂️ You: {message}</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='font-size:15px; color:#222'>🤖 <b>Gemini:</b> {message}</div>",
                unsafe_allow_html=True,
            )

    # === Ask Follow-up Question ===
    user_question = st.text_input("Ask a follow-up question:", key="followup_input", placeholder="e.g., Give more video links")

    if st.button("Ask Gemini"):
        if user_question.strip() != "":
            # Add user message to history
            st.session_state.chat_history.append(("You", user_question))

            # Build context prompt
            previous_chat = "\n".join(
                [f"{sender}: {msg}" for sender, msg in st.session_state.chat_history if sender in ["You", "Gemini"]]
            )
            full_prompt = f"""
You are a helpful AI tutor.

The topic the user is learning about is: **{st.session_state.topic_context}**

Here is the previous conversation:
{previous_chat}

Now the user is asking: "{user_question}"

Respond clearly, helpfully, and concisely with reference to earlier discussion.
"""

            # Get Gemini response
            response = model.generate_content(full_prompt)
            st.session_state.chat_history.append(("Gemini", response.text))

            # ✅ Clear input box after asking
            st.session_state["followup_input"] = ""
            st.rerun()
