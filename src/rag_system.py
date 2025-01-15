import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.callbacks import get_openai_callback
from langchain.prompts import ChatPromptTemplate

class RAGSystem:
    def __init__(self, pdf_directory: str, system_message: str = None):
        """Initialize the RAG system."""
        load_dotenv()
        
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your .env file")
        
        self.pdf_directory = pdf_directory
        self.documents = []
        self.vector_store = None
        
        # Default system message if none provided
        self.system_message = system_message or """
        You are a helpful assistant that answers questions based on the provided documents.
        Follow these guidelines:
        1. Only answer based on the information in the provided documents
        2. If you're not sure or the information isn't in the documents, say so
        3. Provide specific references to the documents when possible
        4. Keep answers clear and concise
        5. If you need to make assumptions, state them explicitly
        """
        
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        self.llm = ChatOpenAI(
            temperature=0.2,
            model_name='gpt-3.5-turbo',
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        print("RAG System initialized...")

    def load_documents(self) -> None:
        """Load PDF documents from the specified directory."""
        try:
            loader = DirectoryLoader(
                self.pdf_directory,
                glob="**/*.pdf",
                loader_cls=PyPDFLoader
            )
            self.documents = loader.load()
            print(f"Loaded {len(self.documents)} documents")
        except Exception as e:
            print(f"Error loading documents: {str(e)}")
            raise

    def process_documents(self) -> None:
        """Process documents: split into chunks and create vector store."""
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            splits = text_splitter.split_documents(self.documents)
            print(f"Created {len(splits)} splits")

            self.vector_store = Chroma.from_documents(
                documents=splits,
                embedding=self.embeddings,
                persist_directory="./chroma_db"
            )
            print("Vector store created")
            print("Chain initialized successfully")
                
        except Exception as e:
            print(f"Error processing documents: {str(e)}")
            raise

    def query(self, question: str) -> Dict[str, Any]:
        """Query the RAG system."""
        if not self.vector_store:
            raise ValueError("System not initialized. Run process_documents first.")

        try:
            with get_openai_callback() as cb:
                # Get relevant documents
                relevant_docs = self.vector_store.similarity_search(question, k=3)
                
                # Prepare context from relevant documents
                context = "\n".join([doc.page_content for doc in relevant_docs])
                
                # Create prompt
                prompt = ChatPromptTemplate.from_messages([
                    ("system", self.system_message),
                    ("user", """
                    Context: {context}
                    
                    Question: {question}
                    
                    Please provide a detailed answer based on the context above.
                    """)
                ])
                
                # Format messages
                messages = prompt.format_messages(
                    context=context,
                    question=question
                )
                
                # Get response
                response = self.llm.invoke(messages)
                
                return {
                    "response": response.content,
                    "source_documents": relevant_docs,
                    "tokens_used": {
                        "prompt_tokens": cb.prompt_tokens,
                        "completion_tokens": cb.completion_tokens,
                        "total_tokens": cb.total_tokens
                    },
                    "cost": cb.total_cost
                }
            
        except Exception as e:
            print(f"Error during query: {str(e)}")
            raise

    def get_relevant_docs(self, question: str, k: int = 3) -> List[str]:
        """Get relevant documents for a question."""
        if not self.vector_store:
            raise ValueError("Vector store not initialized")
            
        docs = self.vector_store.similarity_search(question, k=k)
        return [doc.page_content for doc in docs]

    def update_system_message(self, new_message: str) -> None:
        """Update the system message."""
        self.system_message = new_message
        print("System message updated successfully")

    def get_system_message(self) -> str:
        """Get the current system message."""
        return self.system_message