import sys
import os

_frontend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_frontend_dir, "..", "backend"))

import streamlit as st
from run import invoke_agent

AGENT_NAME = "jira_ticket"

st.set_page_config(page_title="JIRA Ticket Writer", page_icon="\U0001F3AB")
st.title("\U0001F3AB JIRA Ticket Writer")
st.caption("Describe your work casually and get a properly formatted JIRA ticket. Works for bugs, features, and tasks.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_context" not in st.session_state:
    st.session_state.chat_context = {}
if "last_ticket" not in st.session_state:
    st.session_state.last_ticket = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Show download button if a ticket was generated
if st.session_state.last_ticket:
    st.download_button(
        label="\u2B07 Download ticket as .md",
        data=st.session_state.last_ticket,
        file_name="jira_ticket.md",
        mime="text/markdown",
    )

if prompt := st.chat_input("What did you work on? (e.g. fixed the broken login flow...)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Generating JIRA ticket...", expanded=True) as status:
            st.write("\U0001F4CB Classifying ticket type (Bug / Story / Task)...")
            response = invoke_agent(AGENT_NAME, prompt, chat_context=st.session_state.chat_context)
            resp_body = response.get("response", {})
            reply = resp_body.get("text", str(response))
            new_context = resp_body.get("chat_context")
            if new_context:
                st.session_state.chat_context = new_context
            st.write("\u2705 Ticket generated!")
            status.update(label="Ticket ready!", state="complete", expanded=False)

        st.markdown(reply)
        st.session_state.last_ticket = reply

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
