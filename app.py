from flask import Flask, render_template, request, jsonify
from rag_system import RAGSystem
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

# Initialize RAG system
pdf_directory = "./pdfs"
rag_system = None

TECHNICAL_SYSTEM_MESSAGE = """
You are a precise and concise technical assistant who:
1. Provides ONLY the specific information requested
2. Avoids including unnecessary details not asked for
3. Formats responses in a clear, structured way
4. Never adds unrequested information
5. Responds in the most brief way possible while being complete
6. If multiple items are found, presents them in a list format
7. If specific information is not found, clearly states that
"""

SUMMARY_SYSTEM_MESSAGE = """
You are a concise document analyzer who:
1. Provides ONLY the exact information requested
2. Keeps responses as brief as possible
3. Uses bullet points for multiple items
4. Avoids any unnecessary elaboration
5. Sticks strictly to answering the specific question asked
6. Never includes additional context unless specifically requested
"""

def initialize_rag():
    global rag_system
    rag_system = RAGSystem(pdf_directory, TECHNICAL_SYSTEM_MESSAGE)
    rag_system.load_documents()
    rag_system.process_documents()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.json
        question = data.get('question')
        
        if not rag_system:
            initialize_rag()
            
        result = rag_system.query(question)
        
        return jsonify({
            'response': result['response'],
            'sources': [
                {
                    'content': doc.page_content[:200] + "...",
                    'source': doc.metadata.get('source', 'Unknown'),
                    'page': doc.metadata.get('page', 'Unknown')
                }
                for doc in result['source_documents']
            ],
            'tokens': result['tokens_used'],
            'cost': result['cost']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/switch-mode', methods=['POST'])
def switch_mode():
    try:
        data = request.json
        mode = data.get('mode')
        
        if not rag_system:
            initialize_rag()
            
        if mode == 'technical':
            rag_system.update_system_message(TECHNICAL_SYSTEM_MESSAGE)
        elif mode == 'summary':
            rag_system.update_system_message(SUMMARY_SYSTEM_MESSAGE)
            
        return jsonify({'success': True, 'mode': mode})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    initialize_rag()
    app.run(debug=True)