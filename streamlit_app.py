import streamlit as st
import time
from openai import OpenAI

st.title("💬 Chatbot mit eigenem Assistenten")
st.write("Gib deinen OpenAI API-Schlüssel ein, um den Assistenten zu nutzen.")

openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Bitte füge deinen OpenAI API-Schlüssel ein, um fortzufahren.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)
    assistant_id = "asst_qOQodrhsPuo6VmwhHJa1mMP3"

    if "thread_id" not in st.session_state:
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Schreibe deine Nachricht..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Nachricht zum Thread hinzufügen
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt,
        )

        # Run starten
        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
        )

        # Status abfragen bis "completed"
        run_status = run.status
        run_id = run.id
        while run_status != "completed":
            time.sleep(1)  # Warte 1 Sekunde
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run_id
            )
            run_status = run.status

        # Alle Nachrichten im Thread abrufen
        messages = client.beta.threads.messages.list(st.session_state.thread_id).data

        # Letzte Assistenz-Nachricht suchen
        assistant_response = ""
        for msg in reversed(messages):
            if msg.role == "assistant":
                assistant_response = msg.content[0].text.value if msg.content else ""
                break

        if not assistant_response:
            assistant_response = "Keine Antwort vom Assistenten erhalten."

        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)
