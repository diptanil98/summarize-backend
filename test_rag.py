import os
from dotenv import load_dotenv
from model_pipeline import process_pdf_and_summarize

# Load environment variables
load_dotenv()

def test_rag_pipeline():
    # Test document path - make sure this PDF exists
    test_pdf_path = "C://Users//Manav//Downloads//31ef08129e281fd8f6ee6759d673eb05.pdf"
    
    try:
        print("\n=== Testing RAG Pipeline ===\n")
        
        print("Step 1: Processing PDF...")
        summary, sources = process_pdf_and_summarize(test_pdf_path)
        
        print("\n=== Results ===\n")
        print("Summary:")
        print("-" * 50)
        print(summary)
        print("\n" + "=" * 50 + "\n")
        
        print("Sources Used:")
        print("-" * 50)
        for idx, source in enumerate(sources, 1):
            print(f"\nSource {idx}:")
            print(f"Page: {source['page']}")
            print(f"Text excerpt: {source['text'][:200]}...")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    test_rag_pipeline()