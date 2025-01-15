# test_setup.py
from dotenv import load_dotenv
import os
import openai

load_dotenv()

def test_environment():
    print("Testing environment setup...")
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"API Key present: {'Yes' if api_key else 'No'}")
    
    # Check directories
    print(f"PDFs directory exists: {os.path.exists('pdfs')}")
    print(f"Chroma directory exists: {os.path.exists('chroma_db')}")
    
    # Test OpenAI connection
    try:
        openai.api_key = api_key
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello!"}]
        )
        print("OpenAI connection successful!")
    except Exception as e:
        print(f"OpenAI connection failed: {str(e)}")

if __name__ == "__main__":
    test_environment()