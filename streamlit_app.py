import streamlit as st
from openai import OpenAI

st.title("💬 Chatbot mit eigenem Assistenten")
st.write(
    "Gib deinen OpenAI API-Schlüssel ein, um den Assistenten zu nutzen."
)

openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Bitte füge deinen OpenAI API-Schlüssel ein, um fortzufahren.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)
    assistant_id = "asst_qOQodrhsPuo6VmwhHJa1mMP3"

    if "thread_id" not in st.session_state:
        # Neuen Thread anlegen
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        st.session_state.messages = []

    # Anzeige bisheriger Nachrichten
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Schreibe deine Nachricht..."):
        # Nutzer-Nachricht speichern und anzeigen
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Nachricht zum Thread hinzufügen
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt,
        )

        # Run des Assistenten starten für Antwort
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
        )

        # Antwort aus dem Run holen (sicher und geprüft)
        assistant_response = ""
        if hasattr(run, "choices") and len(run.choices) > 0:
            assistant_response = run.choices[0].message.content
        elif hasattr(run, "message") and hasattr(run.message, "content"):
            assistant_response = run.message.content
        else:
            assistant_response = "Keine Antwort vom Assistenten erhalten."

        # Antwort speichern und anzeigen
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)
