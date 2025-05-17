import os
import glob
import logging
from langchain_community.document_loaders import Docx2txtLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.retrievers import ContextualCompressionRetriever
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from django.conf import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Configuration
DOCUMENTS_DIRECTORY = os.path.join(settings.BASE_DIR, "legal_documents")
PERSIST_DIRECTORY = os.path.join(settings.BASE_DIR, "chroma_db")
GOOGLE_API_KEY = settings.GOOGLE_API_KEY

class QAService:
    _instance = None

    def __new__(cls, force_reinitialize=False):
        if cls._instance is None:
            cls._instance = super(QAService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, force_reinitialize=False):
        if not self._initialized:
            self.embeddings = HuggingFaceEmbeddings(model_name="Omartificial-Intelligence-Space/GATE-AraBert-v1")
            self.qa_chain, self.retriever = self._initialize_system(force_reinitialize)
            self._initialized = True

    def load_documents(self, directory):
        """Load all .docx files from the specified directory."""
        docs = []
        for file_path in glob.glob(os.path.join(directory, "*.docx")):
            try:
                loader = Docx2txtLoader(file_path)
                docs.extend(loader.load())
                logging.info(f"Successfully loaded {file_path}")
            except Exception as e:
                logging.error(f"Error loading {file_path}: {e}")
        if not docs:
            raise ValueError("No valid Word documents found in the directory.")
        return docs

    def create_vectorstore(self, docs):
        """Create a Chroma vector store from the provided documents."""
        splitter = SemanticChunker(self.embeddings)
        chunks = splitter.split_documents(docs)
        logging.info("Documents split into chunks successfully.")
        vectorstore = Chroma.from_documents(chunks, self.embeddings, persist_directory=PERSIST_DIRECTORY)
        vectorstore.persist()
        logging.info("Vector store created and persisted.")
        return vectorstore

    def load_vectorstore(self):
        """Load an existing Chroma vector store from disk."""
        if not os.path.exists(PERSIST_DIRECTORY):
            raise FileNotFoundError(f"No vector store found at {PERSIST_DIRECTORY}. Please initialize it first.")
        vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=self.embeddings)
        logging.info("Vector store loaded from disk.")
        return vectorstore

    def setup_retriever(self, vectorstore):
        """Set up the retriever with cross-encoder reranking."""
        cross_encoder = HuggingFaceCrossEncoder(model_name="Omartificial-Intelligence-Space/ARA-Reranker-V1")
        compressor = CrossEncoderReranker(model=cross_encoder, top_n=3)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
        )
        logging.info("Retriever set up with cross-encoder reranking.")
        return compression_retriever

    def setup_llm(self):
        """Set up the language model."""
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7,
            max_output_tokens=256
        )
        logging.info("Language model initialized.")
        return llm

    def create_qa_chain(self, retriever, llm):
        """Create the QA chain with citation support."""
        template = """
        You are an intelligent assistant that answers questions in clear, concise Arabic.
        Context: {context}
        Question: {query}
        Please cite the source(s) of the information in your response.
        Answer:
        """
        prompt = ChatPromptTemplate.from_template(template)
        output_parser = StrOutputParser()

        def format_context(docs):
            """Format context and extract source metadata."""
            context = "\n\n".join(doc.page_content for doc in docs)
            sources = [doc.metadata.get('source', 'Unknown') for doc in docs]
            return {"context": context, "sources": sources}

        qa_chain = (
            {"context": retriever | format_context, "query": RunnablePassthrough()}
            | RunnablePassthrough.assign(
                answer=prompt | llm | output_parser
            )
        )
        logging.info("QA chain created.")
        return qa_chain

    def _initialize_system(self, force_reinitialize):
        """Initialize the system by loading or creating the vector store."""
        if force_reinitialize or not os.path.exists(PERSIST_DIRECTORY):
            logging.info("Initializing system from scratch...")
            docs = self.load_documents(DOCUMENTS_DIRECTORY)
            vectorstore = self.create_vectorstore(docs)
        else:
            logging.info("Loading existing vector store...")
            vectorstore = self.load_vectorstore()

        retriever = self.setup_retriever(vectorstore)
        llm = self.setup_llm()
        qa_chain = self.create_qa_chain(retriever, llm)
        return qa_chain, retriever

    def answer_question(self, query):
        """Answer a question using the QA chain and return answer with sources."""
        try:
            result = self.qa_chain.invoke(query)
            return {
                "answer": result["answer"],
                "sources": result["context"]["sources"]
            }
        except Exception as e:
            logging.error(f"Error answering question: {e}", exc_info=True)
            raise

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = QAService()
        return cls._instance