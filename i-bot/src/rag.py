from langchain_community.vectorstores.pgvector import PGVector
from langchain_openai import OpenAIEmbeddings
from langmem import create_memory_manager, create_search_memory_tool, create_manage_memory_tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader
import mimetypes
from markitdown import MarkItDown

from src.config import settings, llm

from langgraph.store.memory import InMemoryStore

embeddings = OpenAIEmbeddings()
store = InMemoryStore()
memory_manager = create_memory_manager(llm)
search_memory = create_search_memory_tool(store=store, namespace="default")
manage_memory = create_manage_memory_tool(store=store, namespace="default")
md = MarkItDown()

connection_string = settings.DATABASE_URL
collection_name = "documents"

def get_vectorstore():
    return PGVector(
        connection_string=connection_string,
        collection_name=collection_name,
        embedding_function=embeddings,
    )

def initialize_vectorstore():
    loader = TextLoader("documents.txt")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    vectorstore = get_vectorstore()
    vectorstore.add_documents(docs)

def add_documents(documents):
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents)

def add_documents_from_file(file_path: str, content_type: str):
    markdown_content = md.convert(file_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.create_documents([markdown_content])
    add_documents(docs)

def similarity_search(query, user_id, config):
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(query)
    
    # Get memories from langmem
    memories = search_memory.invoke(
        {"query": query}, config
    )
    
    # Combine the results
    context = "\n".join([doc.page_content for doc in docs])
    if memories:
        context += "\n\nRelevant past conversations:\n" + "\n".join(memories)
        
    return context


def add_memory(text, user_id):
    memory_manager.remember(text, user_id=user_id, namespace="default")
