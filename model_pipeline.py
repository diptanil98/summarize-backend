# RAG with Cohere Embeddings
import warnings
import os
import traceback
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseLLM
from langchain_core.prompts import PromptTemplate
import cohere
import google.generativeai as genai

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Load environment variables from .env file
load_dotenv()

# ENV variables
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Cohere client
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY not found in environment variables")

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Cohere Embeddings class for LangChain
class CohereEmbeddings(Embeddings):
    def __init__(self, model_name="embed-english-v3.0"):
        self.client = cohere.Client(COHERE_API_KEY)
        self.model_name = model_name
        
    def embed_documents(self, texts):
        try:
            # Cohere's batch embedding for documents
            if not texts:
                return []
                
            response = self.client.embed(
                texts=texts,
                model=self.model_name,
                input_type="search_document"
            )
            return response.embeddings
        except Exception as e:
            print(f"Error generating embeddings: {str(e)}")
            raise

    def embed_query(self, text):
        try:
            # Cohere's embedding for a single query
            response = self.client.embed(
                texts=[text],
                model=self.model_name,
                input_type="search_query"
            )
            return response.embeddings[0]
        except Exception as e:
            print(f"Error generating query embedding: {str(e)}")
            raise

# Custom LLM class for LangChain
class GeminiLLM(BaseLLM):
    def _call(self, prompt: str, stop=None, **kwargs):
        return self._generate([prompt], stop=stop, **kwargs).generations[0][0].text

    def _generate(self, prompts, stop=None, **kwargs):
        from langchain_core.outputs import Generation, LLMResult
        
        generations = []
        for prompt in prompts:
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                generations.append([Generation(text=response.text)])
            except Exception as e:
                print(f"Error in Gemini LLM call: {str(e)}")
                raise
                
        return LLMResult(generations=generations)

    @property
    def _llm_type(self) -> str:
        return "gemini-2.5-flash"
        
    @property
    def _identifying_params(self) -> dict:
        return {"model_name": "gemini-2.5-flash"}

# Main RAG processing function
def process_pdf_and_summarize(pdf_path: str, query: str):
    try:
        print("[DEBUG] Loading PDF")
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        print(f"[DEBUG] Loaded {len(documents)} documents")

        print("[DEBUG] Splitting text")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        print(f"[DEBUG] Split into {len(chunks)} chunks")

        print("[DEBUG] Creating embeddings using Cohere")
        embeddings = CohereEmbeddings(model_name="embed-english-v3.0")

        print("[DEBUG] Creating FAISS vectorstore")
        vectorstore = FAISS.from_documents(chunks, embedding=embeddings)

        print("[DEBUG] Initializing Retriever and LLM")
        retriever = vectorstore.as_retriever(search_type="similarity", k=5)
        llm = GeminiLLM()

        print("[DEBUG] Setting up RetrievalQA chain")
        prompt_template = """
You are a legal expert AI. Based on the context below, answer the following legal analysis request.

Context:
{context}

Question: {question}

Provide a detailed legal analysis and summary:
"""

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            verbose=True,
            chain_type_kwargs={
                "prompt": PromptTemplate(
                    template=prompt_template,
                    input_variables=["context", "question"],
                ),
            },
        )

        print("[DEBUG] Running query")
        result = qa_chain({"query": query})

        return {
            "result": result["result"],
            "source_documents": [
                {
                    "page_content": doc.page_content,
                    "metadata": doc.metadata
                } for doc in result["source_documents"]
            ]
        }

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        print(traceback.format_exc())
        return {"error": str(e), "traceback": traceback.format_exc()}

# Example usage
if __name__ == "__main__":
    # Example usage
    pdf_path = "sample_legal_document.pdf"  # Replace with your PDF path
    query = "Summarize the key legal points in this document"
    
    result = process_pdf_and_summarize(pdf_path, query)
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("\nSummary:")
        print(result["result"])
        print("\nSources:")
        for i, doc in enumerate(result["source_documents"], 1):
            print(f"\nSource {i} (Page {doc['metadata'].get('page', 'N/A')}):")
            print(doc["page_content"][:300] + "...")
