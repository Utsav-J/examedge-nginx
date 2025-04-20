import requests
from googleapiclient.discovery import build
from config import GOOGLE_BOOKS_API, YOUTUBE_API_KEY

def get_books_google(query: str):
    url = GOOGLE_BOOKS_API.format(query)
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Failed to fetch book for: {query}")
        return None

    data = response.json()
    if "items" not in data:
        print(f"📭 No book found for: {query}")
        return None

    item = data["items"][0]
    info = item.get("volumeInfo", {})

    title = info.get("title", "Unknown Title")
    authors = ", ".join(info.get("authors", ["Unknown Author"]))
    full_description = info.get("description", "No description available.")
    short_description = full_description.split(".")[0].strip() + "." if "." in full_description else full_description[:150] + "..."
    preview_link = info.get("previewLink", "No preview available.")
    thumbnail = info.get("imageLinks", {}).get("thumbnail", "")

    return {
        "title": title,
        "authors": authors,
        "description": short_description,
        "preview": preview_link,
        "thumbnail": thumbnail
    }

def yt_search(query: str):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=1
    )

    response = request.execute()

    if not response["items"]:
        print(f"📭 No video found for: {query}")
        return None

    item = response["items"][0]
    snippet = item["snippet"]
    video_id = item["id"]["videoId"]

    title = snippet.get("title", "Untitled")
    channel = snippet.get("channelTitle", "Unknown Channel")
    description = snippet.get("description", "No description available.")
    short_description = description.split(".")[0].strip() + "." if "." in description else description[:150] + "..."

    return {
        "title": title,
        "channel": channel,
        "description": short_description,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", "")
    }

def fetch_books_for_topics(file_path="document_summary.json"):
    from .file_utils import load_main_topics
    
    topics = load_main_topics(file_path)
    if not topics:
        print("⚠️ No topics found.")
        return {}

    result = {}
    for topic in topics:
        print(f"🔍 Searching one book for: {topic}")
        book = get_books_google(topic)
        if book:
            result[topic] = book

    return [result]  # ✅ Just returning, not saving

def fetch_youtube_videos_for_topics(file_path):
    from .file_utils import load_main_topics
    
    topics = load_main_topics(file_path)
    if not topics:
        print("⚠️ No topics found.")
        return {}

    result = {}
    for topic in topics:
        print(f"🔍 Searching one YouTube video for: {topic}")
        video = yt_search(topic)
        if video:
            result[topic] = video

    return result 