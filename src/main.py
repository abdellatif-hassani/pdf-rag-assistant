import os
from rag_system import RAGSystem

# Example system messages for different purposes
TECHNICAL_SYSTEM_MESSAGE = """
You are a technical documentation expert who:
1. Focuses on technical details and specifications
2. Explains complex concepts clearly
3. Provides code examples when relevant
4. References technical standards and best practices
"""

SUMMARY_SYSTEM_MESSAGE = """
You are a document summarizer who:
1. Provides concise overviews
2. Highlights key points and main ideas
3. Organizes information hierarchically
4. Maintains the essential message while condensing
"""

def main():
    # Initialize the RAG system with custom message
    pdf_directory = "./pdfs"
    rag = RAGSystem(
        pdf_directory=pdf_directory,
        system_message=TECHNICAL_SYSTEM_MESSAGE
    )

    # Load and process documents
    print("Loading documents...")
    rag.load_documents()
    
    print("Processing documents...")
    rag.process_documents()

    # Interactive query loop
    print("\nRAG System ready for queries (type 'exit' to quit, 'switch' to change system message)")
    print("-" * 50)

    while True:
        command = input("\nEnter question or command: ").strip()
        
        if command.lower() == 'exit':
            break
        elif command.lower() == 'switch':
            print("\nAvailable modes:")
            print("1. Technical")
            print("2. Summary")
            mode = input("Select mode (1/2): ").strip()
            
            if mode == "1":
                rag.update_system_message(TECHNICAL_SYSTEM_MESSAGE)
            elif mode == "2":
                rag.update_system_message(SUMMARY_SYSTEM_MESSAGE)
            continue

        try:
            # Get response
            result = rag.query(command)
            
            print("\nResponse:", result["response"])
            
            print("\nSource Documents:")
            for i, doc in enumerate(result["source_documents"], 1):
                print(f"\nSource {i}:")
                print("-" * 40)
                print(f"Content: {doc.page_content[:200]}...")
                print(f"Source: {doc.metadata.get('source', 'Unknown')}")
                print(f"Page: {doc.metadata.get('page', 'Unknown')}")

            print("\nTokens Used:")
            print(f"  Prompt tokens: {result['tokens_used']['prompt_tokens']}")
            print(f"  Completion tokens: {result['tokens_used']['completion_tokens']}")
            print(f"  Total tokens: {result['tokens_used']['total_tokens']}")
            print(f"  Cost: ${result['cost']:.4f}")

        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()