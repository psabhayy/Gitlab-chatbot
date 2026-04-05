import streamlit as st
from src.rag_chain import get_rag_chain

# --- Page Configuration ---
st.set_page_config(page_title="GitLab Assistant", page_icon="🦊")
st.title("GitLab Assistant 🦊")
st.markdown("Ask me anything about GitLab handbook and direction pages!")

# --- Initialization ---
# Initialize session state for messages if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize the RAG chain
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = get_rag_chain()
    
# If chain is None, wait until DB is built
if st.session_state.qa_chain is None:
    st.error("Vector database not found. Please run `python build_vector_store.py` first.")
    st.stop()

# --- Sidebar ---
with st.sidebar:
    # Button to clear the conversation
    if st.button("Clear Chat"):
        st.session_state.messages = []
        # Reinitialize RAG chain to clear the memory correctly
        st.session_state.qa_chain = get_rag_chain()

# --- Chat Rendering ---
# Display all prior messages in the UI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Input Handling ---
# Text input box at the bottom
prompt = st.chat_input("Ask a question about GitLab...")

if prompt:
    # 1. Render user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Save user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Render assistant message
    with st.chat_message("assistant"):
        # Show a spinner while invoking the chain
        with st.spinner("Searching GitLab Knowledge Base..."):
            # Get response from the RAG pipeline
            response = st.session_state.qa_chain.invoke({"question": prompt})
            answer = response["answer"]
            
            # Extract citations/sources
            source_documents = response.get("source_documents", [])
            sources = set()
            for doc in source_documents:
                source = doc.metadata.get("source")
                if source:
                    sources.add(source)
            
            # Print answer
            st.markdown(answer)
            
            # Print citations quietly
            if sources:
                st.caption("Sources:")
                for src in sources:
                    st.caption(f"- {src}")

    # Save assistant message to state
    st.session_state.messages.append({"role": "assistant", "content": answer})
