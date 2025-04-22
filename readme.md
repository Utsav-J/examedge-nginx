# 📘 ExamEdge Backend

The **ExamEdge Backend** is a FastAPI-powered server designed to extract and process academic content from PDFs, generate AI-based summaries and MCQs, and recommend books, videos, and faculty based on content topics. This backend powers the ExamEdge app experience by delivering intelligent and interactive learning material.

---

## 🚀 Features

- 📤 Upload and extract text + images from PDF documents
- ✨ Generate AI-powered summaries using Gemini
- ❓ Create MCQs chunk-by-chunk from document content
- 📚 Recommend relevant books using Google Books API
- 🎥 Fetch relevant YouTube videos per topic
- 🧑‍🏫 Suggest expert faculty members based on document topics
- 💬 RAG-based chatbot to interact with uploaded PDF content
- 🌍 Deployed on an NGINX server hosted on an Ubuntu EC2 instance

---

## 📂 API Endpoints

### `/upload-pdf/` `POST`
Upload a `.pdf` file, extract its content, and generate structured JSON metadata.

**Returns:**
- Original filename
- Unique filename
- Confirmation message

---

### `/generate-summary/{filename}` `POST`
Generates a detailed summary of the uploaded PDF using Gemini.

**Requires:** Metadata to already exist from upload step.

---

### `/generate-mcqs/{filename}?start_page=1` `POST`
Generates Multiple Choice Questions based on document content, starting optionally from a given page.

---

### `/fetch-books/{filename}` `POST`
Returns one book recommendation per topic based on the PDF summary.

---

### `/fetch-videos/{filename}` `POST`
Returns one YouTube video per topic using YouTube API, based on document summary.

---

### `/fetch-faculties/{filename}` `POST`
Returns matched faculty members using static data and document summary topics.

---

### `/chat-with-pdf/{filename}` `POST`
Provides an AI chatbot experience with the uploaded PDF. Uses document context to respond to user queries (RAG-based).

**Request Body:**
```json
{
  "query": "What is the main idea of chapter 3?"
}
```
Returns: AI-generated response, Pages used for generating the response


## 🧪Tech Stack
### Framework: FastAPI
### LLM Integration: Gemma 3, 27B parameters (via Google Generative AI)
### OCR: PyTesseract
### PDF Handling: PyMuPDF, PDF2Image
### Media APIs: Google Books, YouTube
### Deployment: NGINX on Ubuntu EC2
