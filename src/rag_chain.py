import os
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings # Back to the local tool
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from src.config import EMBEDDING_MODEL_NAME, LLM_MODEL_NAME, GEMINI_API_KEY

def get_rag_chain():
    if not os.path.exists("vector_db"):
        return None
        
    # Back to the free local embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    # Load the persisted Chroma vectorstore
    vector_store = Chroma(persist_directory="vector_db", embedding_function=embeddings)
    
    # Create the retriever (getting top 30 hits to guarantee best output)
    # Create the retriever. Setting k=30 prevents "vector dilution," ensuring the bot can find specific pages like Core Values even across a massive dataset.
    retriever = vector_store.as_retriever(search_kwargs={"k": 30})

    # Initialize the LLM (Gemini 1.5 Flash via Google GenAI)
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL_NAME,
        google_api_key=GEMINI_API_KEY,
        temperature=0.2 # Lower temperature for better factual consistency
    )
    
    # Initialize memory to keep track of the conversation context
    memory = ConversationSummaryBufferMemory(
        llm=llm,
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    
    # Define system prompt with strict guardrails
    prompt_template = """
    You are an AI assistant for GitLab. Use ONLY the provided context. If the answer is not in the context, politely decline to answer. Cite your sources naturally.
    
    Context: {context}
    Chat History: {chat_history}
    Question: {question}
    
    Answer:
    """
    
    # Create a PromptTemplate instance from the string above
    prompt = PromptTemplate(
        input_variables=["context", "chat_history", "question"],
        template=prompt_template
    )
    
    # Build and return the Conversational Retrieval Chain
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True
    )
    
    return chain
