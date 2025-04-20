from .pdf_processing import (
    extract_text_from_pdf,
    extract_images_from_pdf,
    save_extraction_to_json,
    run_demo_pdf_data_extraction
)

from .gemini_utils import (
    query_gemini_for_summary,
    process_pdf_with_gemini_summary,
    generate_mcqs_chunked
)

from .external_apis import (
    get_books_google,
    yt_search,
    fetch_books_for_topics,
    fetch_youtube_videos_for_topics
)

from .faculty_utils import match_faculty_with_topics

from .file_utils import (
    insert_text_to_file,
    extract_and_save_json,
    load_json_file,
    load_main_topics,
    append_summary_path_to_metadata
)

from .chat_with_pdf import (
    extract_pages_from_response,
    create_prompt,
    build_context_from_json,
    chunk_text,
    load_document
)

# Re-export all functions
__all__ = [
    'extract_text_from_pdf',
    'extract_images_from_pdf',
    'save_extraction_to_json',
    'run_demo_pdf_data_extraction',
    'query_gemini_for_summary',
    'process_pdf_with_gemini_summary',
    'generate_mcqs_chunked',
    'get_books_google',
    'yt_search',
    'fetch_books_for_topics',
    'fetch_youtube_videos_for_topics',
    'match_faculty_with_topics',
    'insert_text_to_file',
    'extract_and_save_json',
    'load_json_file',
    'load_main_topics',
    'append_summary_path_to_metadata',
    'extract_pages_from_response',
    'create_prompt',
    'build_context_from_json',
    'chunk_text',
    'load_document'
] 