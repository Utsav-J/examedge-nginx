import fitz
import pytesseract
from pdf2image import convert_from_path
import os
from datetime import datetime
import json

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF using a hybrid approach (PyMuPDF + OCR)."""
    doc = fitz.open(pdf_path)
    extracted_text = []

    for page_num, page in enumerate(doc):
        # Try extracting text normally
        text = page.get_text("text")

        if text.strip():  # If text is found, use it
            extracted_text.append(text)
        else:  # If no text found, apply OCR on image
            print(f"Applying OCR on page {page_num + 1} (scanned image detected)...")
            image = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)[0]
            text = pytesseract.image_to_string(image)
            extracted_text.append(text)

    full_text = "\n".join(extracted_text)
    return full_text

def extract_images_from_pdf(pdf_path, output_folder="extracted_images"):
    """Extracts and saves images from a PDF."""
    doc = fitz.open(pdf_path)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_count = 0
    for page_num, page in enumerate(doc):
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]  # Image reference ID
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]  # Image format (e.g., PNG, JPEG)

            image_filename = f"{output_folder}/page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
            with open(image_filename, "wb") as f:
                f.write(image_bytes)

            image_count += 1
            print(f"✅ Saved image: {image_filename}")

    if image_count == 0:
        print("❌ No images found in the PDF.")
    else:
        print(f"✅ Extracted {image_count} images.")

def save_extraction_to_json(text_data, images_folder, output_filepath):
    """Saves extracted text and image references into a structured JSON format."""
    extracted_data = {"document_title": "Extracted Report", "sections": []}

    for page_num, text in enumerate(text_data.split("\n\n")):
        page_info = {
            "page": page_num + 1,
            "text": text.strip(),
            "images": []
        }

        # Find corresponding images for this page
        for img_file in os.listdir(images_folder):
            if f"page_{page_num + 1}_" in img_file:
                page_info["images"].append({
                    "filename": os.path.join(images_folder, img_file),
                    "description": "Extracted image"
                })

        extracted_data["sections"].append(page_info)

    final_path = os.path.join(output_filepath, "extracted_data.json")
    with open(final_path, "w", encoding="utf-8") as f:
        json.dump(extracted_data, f, indent=4)

    print(f"✅ JSON saved as {final_path}")
    return final_path

def run_demo_pdf_data_extraction(pdf_path: str):
    folder_name = os.path.splitext(pdf_path)[0] + datetime.now().strftime("%m%d%Y-%H%M%S%f")
    os.mkdir(folder_name)

    pdf_text = extract_text_from_pdf(pdf_path)
    text_file_path = os.path.join(folder_name, 'result-hybrid-unprocessed.txt')
    from .file_utils import insert_text_to_file
    insert_text_to_file(text_file_path, pdf_text)
    image_folder_path = os.path.join(folder_name, "extracted_images")
    extract_images_from_pdf(pdf_path, output_folder=image_folder_path)
    extractedDataJsonPath = save_extraction_to_json(pdf_text, image_folder_path, folder_name)
    return {
        "folderName": folder_name,
        "extractedDataJsonPath": extractedDataJsonPath
    } 