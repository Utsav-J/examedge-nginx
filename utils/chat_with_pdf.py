
# # Load environment variables
import textwrap
import google.generativeai as genai2
from config import model
import json
import re

document_cache = {}
MAX_CHUNK_SIZE = 1000  # words
CHUNK_OVERLAP = 100     # words

def load_document(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def chunk_text(text, max_size=MAX_CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + max_size, len(words))
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start += max_size - overlap
    return chunks

def build_context_from_json(doc_json):
    all_chunks = []
    for page_num, page in enumerate(doc_json['sections'], start=1):
        page_text = page.get('text', '')
        if page_text.strip():
            chunks = chunk_text(page_text)
            all_chunks.extend([(page_num, chunk) for chunk in chunks])
    return all_chunks

def create_prompt(context_chunks, user_query):
    context = "\n\n".join([
        f"Page {page_num}, Chunk {i+1}:\n{chunk}"
        for i, (page_num, chunk) in enumerate(context_chunks)
    ])

    prompt = textwrap.dedent(f"""
        You are a helpful assistant with access to a document split into several pages and chunks.
        When answering the user's question, also return the page numbers that contributed to the answer.
        Wherever you reference a certain page, include the page number in the format (Page i) where i is the page number.

        Document Context:
        {context}

        Question: {user_query}
        Answer (make sure to include (Page X) when you reference info):
    """)
    return prompt

def extract_pages_from_response(response_text):
    # Matches both (Page 3) and Page 3, even (Page 6, Page 8)
    print("here are the pages")
    matches = re.findall(r'\(?Page (\d+)\)?', response_text)
    print(matches)
    pages = sorted(set(int(page) for page in matches))
    print(pages)
    return pages
