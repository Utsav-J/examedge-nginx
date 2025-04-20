import json
import re
import os

def insert_text_to_file(filepath, text_to_insert):
    try:
        with open(filepath, 'w') as file:
            file.write(text_to_insert)
        print(f"Text successfully written to {filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_and_save_json(text, output_filename="output.json"):
    """Extracts JSON content from a string and saves it as a raw JSON file."""
    match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)

    if match:
        json_content = match.group(1)
        try:
            json_data = json.loads(json_content)
            with open(output_filename, "w", encoding="utf-8") as json_file:
                json.dump(json_data, json_file, indent=4, ensure_ascii=False)
            print(f"JSON data extracted and saved to {output_filename}")
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
    else:
        print("No valid JSON found in the input string.")
    return None

def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def load_main_topics(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("main_topics", [])
    except Exception as e:
        print(f"❌ Error loading file: {file_path} → {e}")
        return []

def append_summary_path_to_metadata(metadata_path: str):
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata file not found at: {metadata_path}")

    # Load existing metadata
    with open(metadata_path, "r") as meta_file:
        metadata = json.load(meta_file)

    # Build the summary path using folderName
    folder_path = metadata.get("folderName")
    if not folder_path:
        raise ValueError("Missing 'folderName' in metadata")

    summary_path = os.path.join(folder_path, "document_summary.json")

    # Add new field
    metadata["documentSummaryPath"] = summary_path

    # Save it back
    with open(metadata_path, "w") as meta_file:
        json.dump(metadata, meta_file, indent=4)

    return summary_path  # optional return 