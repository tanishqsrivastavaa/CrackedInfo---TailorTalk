import os
from typing import Any

import requests
import streamlit as st


st.set_page_config(page_title="TailorTalk Drive Search", page_icon="🔎", layout="wide")
st.title("TailorTalk Drive Search")

default_backend = os.getenv("BACKEND_CHAT_URL", "http://127.0.0.1:8000/chat")
backend_url = st.sidebar.text_input("Backend /chat URL", value=default_backend)
timeout_seconds = st.sidebar.number_input("Timeout (seconds)", min_value=5, max_value=120, value=30)

if "history" not in st.session_state:
    st.session_state.history = []


def call_backend(message: str) -> dict[str, Any]:
    response = requests.post(
        backend_url,
        json={"message": message},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    return response.json()


with st.form("chat_form", clear_on_submit=True):
    message = st.text_input("Message", placeholder="Find pdf reports")
    submitted = st.form_submit_button("Send")

if submitted and message.strip():
    try:
        payload = call_backend(message.strip())
        st.session_state.history.append(payload)
    except requests.RequestException as exc:
        st.error(f"Request failed: {exc}")

if not st.session_state.history:
    st.info("Enter a search message to test the backend.")

for item in reversed(st.session_state.history):
    st.subheader(f"User: {item.get('message', '')}")
    st.write(item.get("assistant_answer", ""))

    if item.get("error"):
        st.error(item["error"])

    st.code(item.get("query", ""), language="text")
    st.write(f"Results: {item.get('count', 0)}")

    files = item.get("files", [])
    if files:
        for file in files:
            name = file.get("name", "(no name)")
            mime_type = file.get("mime_type", "")
            modified = file.get("modified_time", "")
            link = file.get("web_view_link")
            if link:
                st.markdown(f"- [{name}]({link})  \n  `{mime_type}` | {modified}")
            else:
                st.markdown(f"- {name}  \n  `{mime_type}` | {modified}")
    else:
        st.write("No files returned.")
