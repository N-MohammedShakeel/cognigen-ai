import os
from dotenv import load_dotenv
import googleapiclient.discovery

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")


def fetch_youtube_videos(query: str, max_results: int = 10):
    """
    Fetches YouTube videos safely using YouTube Data API v3.
    If API Key is missing or API fails, returns an empty list (does not crash).
    """

    # -------------------------------------------------------------
    # SAFETY CHECK 1 — Missing API Key
    # -------------------------------------------------------------
    if not API_KEY:
        print("⚠️ YOUTUBE_API_KEY not found in .env — skipping YouTube fetch.")
        return []

    try:
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=API_KEY
        )

        request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results,
            safeSearch="strict"
        )

        response = request.execute()

        videos = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            title = snippet.get("title", "")
            description = snippet.get("description", "")

            videos.append({
                "title": title,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "description": description[:300]  # limit for embedding
            })

        print(f"🎥 YouTube fetch successful: {len(videos)} videos retrieved.")
        return videos

    except Exception as e:
        # ---------------------------------------------------------
        # SAFETY CHECK 2 — YouTube API failure (no crash)
        # ---------------------------------------------------------
        print("⚠️ YouTube API request failed — continuing without videos.")
        print("Error →", str(e))
        return []
