import json
import faiss
import numpy as np
import os
import glob
from dotenv import load_dotenv

from youtube_fetcher import fetch_youtube_videos
from docx_parser import parse_docx

load_dotenv()

INDEX_OUTPUT = "vector_stores/python.index"
META_OUTPUT = "vector_stores/python_metadata.json"

DATA_FOLDER = "data"
EMBED_SIZE = 1024
MIN_ITEMS_REQUIRED = 15


# ---------------------------------------------------------
# TEMP EMBEDDING (Replace with real embedding later)
# ---------------------------------------------------------
def embed(text: str) -> np.ndarray:
    vec = np.random.rand(EMBED_SIZE).astype("float32")
    vec /= np.linalg.norm(vec)
    return vec


# ---------------------------------------------------------
# SAFE YOUTUBE FETCH (NO CRASH)
# ---------------------------------------------------------
def fetch_youtube_videos_safe(query: str, max_results: int = 10):
    API_KEY = os.getenv("YOUTUBE_API_KEY")

    if not API_KEY:
        print("⚠️ No YouTube API Key found — skipping YouTube ingestion.")
        return []

    try:
        print(f"🎥 Fetching {max_results} videos from YouTube...")
        return fetch_youtube_videos(query, max_results=max_results)

    except Exception as e:
        print("⚠️ YouTube API failed — skipping.")
        print("Error:", str(e))
        return []


# ---------------------------------------------------------
# MAIN INGEST PIPELINE
# ---------------------------------------------------------
def main():
    print("====================================")
    print("📥 Starting Ingestion Pipeline")
    print("====================================")

    total_items = []

    # -----------------------------------------------------
    # LOAD ALL JSON FILES FROM data/
    # -----------------------------------------------------
    json_files = glob.glob(os.path.join(DATA_FOLDER, "*.json"))
    print(f"📄 Found {len(json_files)} JSON files in /data")

    for file in json_files:
        print(f"➡ Loading JSON: {file}")
        try:
            resources = json.load(open(file, "r", encoding="utf-8", errors="ignore"))
            total_items.extend(resources)
            print(f"✔ Loaded {len(resources)} items")
        except Exception as e:
            print(f"❌ Failed to load {file}: {str(e)}")

    # -----------------------------------------------------
    # LOAD ALL DOCX FILES FROM data/
    # -----------------------------------------------------
    docx_files = glob.glob(os.path.join(DATA_FOLDER, "*.docx"))
    print(f"📄 Found {len(docx_files)} DOCX files in /data")

    for file in docx_files:
        print(f"➡ Parsing DOCX: {file}")
        try:
            docx_data = parse_docx(file)
            total_items.extend(docx_data)
            print(f"✔ Loaded {len(docx_data)} entries")
        except Exception as e:
            print(f"❌ Failed to parse {file}: {str(e)}")

    # -----------------------------------------------------
    # FINAL RESOURCE COUNT CHECK
    # -----------------------------------------------------
    print(f"📊 Total items collected: {len(total_items)}")

    if len(total_items) == 0:
        print("❌ ERROR: No content found in /data and YouTube fallback failed.")
        print("   Ingestion stopped safely without crashing.")
        return

    # -----------------------------------------------------
    # ENCODING (FAKE EMBEDDING)
    # -----------------------------------------------------
    print("🔍 Embedding documents...")
    vectors = [embed(item["title"] + " " + item["description"]) for item in total_items]
    vectors = np.vstack(vectors)

    # -----------------------------------------------------
    # BUILD FAISS INDEX
    # -----------------------------------------------------
    print("📦 Building FAISS index...")
    index = faiss.IndexFlatL2(EMBED_SIZE)
    index.add(vectors)

    faiss.write_index(index, INDEX_OUTPUT)
    json.dump(total_items, open(META_OUTPUT, "w"), indent=2)

    print("====================================")
    print("✅ Ingestion Completed Successfully!")
    print(f"📁 Index saved to: {INDEX_OUTPUT}")
    print(f"📁 Metadata saved to: {META_OUTPUT}")
    print("====================================")


if __name__ == "__main__":
    main()
