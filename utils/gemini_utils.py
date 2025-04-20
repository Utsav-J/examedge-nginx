import json
import re
from config import client
import os
def query_gemini_for_summary(document_text):
    """Sends the entire document text to Gemini and extracts key insights."""
    prompt = (
        "Analyze the following document text and generate a structured JSON output with:\n"
        "- 'document_overview' (a large paragraph summarizing the document)\n"
        "- 'key_points' (a list of essential takeaways from the document)\n"
        "- 'main_topics' (a list of core topics covered in the document, maximum 4 words per topic)\n\n"
        "Document Text:\n" + document_text
    )

    try:
        response = client.models.generate_content(model="gemma-3-27b-it", contents=prompt)
        return response.text if response else "No response"
    except Exception as e:
        print(f"Error querying Gemini API: {e}")
        return None

def process_pdf_with_gemini_summary(json_path, output_folder):
    from .file_utils import load_json_file, extract_and_save_json
    
    data = load_json_file(json_path)

    if "sections" not in data:
        print("Invalid JSON structure: 'sections' key missing.")
        return {"error": "Invalid JSON structure: 'sections' key missing."}

    document_text = "\n\n".join(
        section.get("text", "").strip()
        for section in data["sections"]
        if section.get("text")
    )

    if not document_text:
        print("No valid text found in the document.")
        return {"error": "No valid text found in the document."}

    print("Processing entire document with Gemini for structured summary...")
    response_text = query_gemini_for_summary(document_text)

    summary_path = os.path.join(output_folder, "document_summary.json")
    structured_output = extract_and_save_json(response_text, summary_path)

    if structured_output:
        print(summary_path)
        print(f"Document summary successfully saved in {summary_path}")
        return structured_output
    else:
        print("Failed to extract structured JSON from Gemini response.")
        return {"error": "Failed to extract structured JSON from Gemini response."}

def generate_mcqs_chunked(pdf_data, start_page=1, chunk_size=5):
    end_page = start_page + chunk_size - 1

    filtered_sections = [
        section for section in pdf_data.get("sections", [])
        if start_page <= section.get("page", 0) <= end_page
    ]

    if not filtered_sections:
        return {"error": "No pages found in the specified range."}

    combined_text = "\n\n".join(section["text"] for section in filtered_sections)

    prompt = f"""
              You are a helpful AI assistant that creates multiple-choice questions (MCQs) for exam preparation.

              Generate 5 to 7 MCQs as you can based strictly on the following academic text.
              The questions should cover main topics discussed in the text.
              Each question must include:
              - a "question" string,
              - an "options" array of 4 strings,
              - a correct "answer" string (must match one of the options exactly).

              Return the response as a valid JSON list of dictionaries.

              TEXT:
              \"\"\"
              {combined_text}
              \"\"\"
              """

    try:
        response = client.models.generate_content(model="gemma-3-27b-it", contents=prompt)
        raw_output = response.text.strip()

        start_idx = raw_output.find("[")
        end_idx = raw_output.rfind("]") + 1
        json_str = raw_output[start_idx:end_idx]

        mcqs = json.loads(json_str)
        return mcqs

    except Exception as e:
        print("❌ Gemini Error:", e)
        print("📤 Raw Output:\n", raw_output)
        return {"error": "Failed to parse MCQs from Gemini."} 