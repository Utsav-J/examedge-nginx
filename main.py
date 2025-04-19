from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import shutil
import uuid
import json
from typing import Optional
from utils import insert_text_to_file,extract_text_from_pdf,extract_images_from_pdf,save_extraction_to_json,run_demo_pdf_data_extraction,extract_and_save_json,load_extracted_json,query_gemini_for_summary,process_pdf_with_gemini_summary,generate_mcqs_chunked,append_summary_path_to_metadata,get_books_google,load_main_topics,fetch_books_for_topics,yt_search,fetch_youtube_videos_for_topics,insert_text_to_file,load_json_file,match_faculty_with_topics
from utils import YOUTUBE_API_KEY, GOOGLE_BOOKS_API, GEMINI_API_KEY,client
from utils import UPLOAD_DIR, FACULTY_DATASET_PATH

app = FastAPI(title="Exam Edge API",
            description="Exam Edge API for processing PDFs and generating summaries and MCQs",
            version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    # Generate a unique suffix
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]  # Short UUID
    base_name = os.path.splitext(file.filename)[0]
    new_filename = f"{base_name}_{unique_id}.pdf"
    file_path = os.path.join(UPLOAD_DIR, new_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run extraction once
        extraction_results = run_demo_pdf_data_extraction(file_path)
        metadata_path = os.path.join(UPLOAD_DIR, f"{new_filename}_metadata.json")

        print(type(metadata_path))
        print(metadata_path)
        print(type(extraction_results))
        print(extraction_results)

        with open(metadata_path, "w") as meta_file:
            json.dump(extraction_results, meta_file)

        print(file.filename)
        print(new_filename)

        return {
            "original_filename": file.filename,
            "unique_filename": new_filename,
            "message": "File uploaded and processed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-summary/{filename}")
async def generate_summary(filename: str):
    """
    Generate a summary from an uploaded PDF file.
    """
    print(f"""
    Generating a summary from an uploaded PDF file {filename}.
    """)
    metadata_path = os.path.join(UPLOAD_DIR, f"{filename}_metadata.json")
    summary_path = append_summary_path_to_metadata(metadata_path)

    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Metadata not found. Please upload the PDF first.")

    try:
        with open(metadata_path) as f:
            extraction_results = json.load(f)

        extracted_json_path = extraction_results["extractedDataJsonPath"]
        output_folder = extraction_results["folderName"]

        summary = process_pdf_with_gemini_summary(extracted_json_path, output_folder)

        # Optional: Don't delete the folder if you still need it for MCQs
        # shutil.rmtree(output_folder)

        return summary

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-mcqs/{filename}")
async def generate_mcqs(filename: str, start_page: Optional[int] = 1):
    """
    Generate MCQs from an uploaded PDF file.
    """

    metadata_path = os.path.join(UPLOAD_DIR, f"{filename}_metadata.json")
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Metadata not found. Please upload the PDF first.")

    try:
        with open(metadata_path) as f:
            extraction_results = json.load(f)

        extracted_json_path = extraction_results["extractedDataJsonPath"]

        with open(extracted_json_path) as f:
            data = json.load(f)

        mcqs = generate_mcqs_chunked(data, start_page=start_page)

        # Optional: Clean up here if you're done with both summary and MCQs
        # shutil.rmtree(extraction_results["folderName"])

        return {"mcqs": mcqs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fetch-books/{filename}")
async def fetch_books(filename: str):
    """
    Fetch one book per topic from the document_summary.json
    using the metadata JSON to locate the correct summary path.
    """
    metadata_path = os.path.join(UPLOAD_DIR, f"{filename}_metadata.json")

    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Metadata not found.")

    try:
        # Load metadata to locate summary path
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        document_summary_path = metadata.get("documentSummaryPath")

        if not document_summary_path or not os.path.exists(document_summary_path):
            raise HTTPException(status_code=404, detail="document_summary.json path missing or file not found.")

        # Fetch books for topics
        books = fetch_books_for_topics(document_summary_path)
        return {"books": books}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fetch-videos/{filename}")
async def fetch_videos(filename: str):
    """
    Fetch one YouTube video per topic from the document_summary.json
    using metadata JSON to locate the correct summary path.
    """
    metadata_path = os.path.join(UPLOAD_DIR, f"{filename}_metadata.json")

    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Metadata not found.")

    try:
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        document_summary_path = metadata.get("documentSummaryPath")

        if not document_summary_path or not os.path.exists(document_summary_path):
            raise HTTPException(status_code=404, detail="document_summary.json path missing or file not found.")

        videos = fetch_youtube_videos_for_topics(document_summary_path)
        return {"videos": videos}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fetch-faculties/{filename}")
async def fetch_faculties(filename: str):
    """
    Match top faculty members based on topics in document summary and static faculty data.
    """
    metadata_path = os.path.join("uploads", f"{filename}_metadata.json")

    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Metadata not found.")

    try:
        # Load metadata to locate summary path
        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        document_summary_path = metadata.get("documentSummaryPath")

        if not document_summary_path or not os.path.exists(document_summary_path):
            raise HTTPException(status_code=404, detail="document_summary.json path missing or file not found.")

        summary = load_json_file(document_summary_path)
        main_topics = summary.get("main_topics", [])

        if not main_topics:
            raise HTTPException(status_code=400, detail="No main topics found in summary.")

        # Load faculty data (hardcoded path)
        faculty_data = load_json_file(FACULTY_DATASET_PATH)

        # Match faculty with topics from document summary
        matched_faculties = match_faculty_with_topics(main_topics, faculty_data)

        return {"faculties": matched_faculties}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """
    Root endpoint returning API information.
    """
    return {
        "message": "PDF Processing API",
        "endpoints": {
            "/upload-pdf/": "Upload a PDF file",
            "/generate-summary/{filename}": "Generate summary from uploaded PDF",
            "/generate-mcqs/{filename}": "Generate MCQs from uploaded PDF"
        }
    }
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)