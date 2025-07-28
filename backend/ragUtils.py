import os
from typing import List, Dict, Any
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.schema import Document
from dotenv import load_dotenv
from typing import Optional

# load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

CHROMA_DB_PATH = "./chroma_db"

_vector_store = None

def get_vector_store_instance():
    """Returns a singleton ChromaDB client."""
    global _vector_store
    if _vector_store is None:
        _vector_store = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)
    return _vector_store

def create_and_store_embeddings_simple(
    meeting_id: str,
    full_text_content: str, 
    metadata: Dict[str, Any] 
):
    """
    Chunks the combined meeting content, generates embeddings, and stores them.
    Metadata from the meeting analysis will be attached to each chunk.
    """
    combined_content = f"Meeting ID: {meeting_id}\n" \
                       f"Timestamp: {metadata.get('timestamp', 'N/A')}\n" \
                       f"Summary: {metadata.get('summary', 'No summary.')}\n" \
                       f"Action Items: {', '.join([item['task'] for item in metadata.get('action_items', [])]) if metadata.get('action_items') else 'None'}\n" \
                       f"Key Decisions: {', '.join([d['description'] for d in metadata.get('key_decisions', [])]) if metadata.get('key_decisions') else 'None'}\n" \
                       f"Speakers: {', '.join(metadata.get('speakers_detected', [])) if metadata.get('speakers_detected') else 'None'}\n" \
                       f"Important Topics: {', '.join(metadata.get('important_topics', [])) if metadata.get('important_topics') else 'None'}\n" \
                       f"Transcript:\n{full_text_content}" 

    doc = Document(
        page_content=combined_content,
        metadata={"meeting_id": meeting_id, "type": "meeting_record", **metadata}
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    split_docs = text_splitter.split_documents([doc]) 

    print(f"Adding {len(split_docs)} chunks to vector store for meeting {meeting_id}")

    vector_store = get_vector_store_instance()
    vector_store.add_documents(split_docs)
    vector_store.persist()
    print(f"Embeddings stored for meeting {meeting_id}.")

async def query_rag_simple(query: str, meeting_id: Optional[str] = None) -> dict:
    """
    Queries the RAG system with a user question.
    Can filter by meeting_id if provided.
    """
    vector_store = get_vector_store_instance()

    if meeting_id:
        retriever = vector_store.as_retriever(
            search_kwargs={
                "k": 5,
                "where": {"meeting_id": meeting_id}
            }
        )
    else:
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    result = await qa_chain.ainvoke({"query": query})
    return result