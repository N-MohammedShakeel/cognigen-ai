# main.py

import logging
import json
import traceback
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request

from schemas import (
    LearningPathCreateRequest,
    LearningPathResponse,
    TopicContentGenerateRequest,
    TopicContentResponse
)
from graphs.learning_path import learning_path_graph
from graphs.content_gen import content_graph


# ---------------------------------------------------------
# SETUP LOGGER
# ---------------------------------------------------------
logger = logging.getLogger("cognigen-ai-service")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


app = FastAPI(title="Cognigen AI Service")


@app.get("/health")
def health():
    logger.info("Health check hit")
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


# ---------------------------------------------------------
# LEARNING PATH GENERATION
# ---------------------------------------------------------
@app.post("/api/generate-learning-path", response_model=LearningPathResponse)
async def generate_learning_path(payload: LearningPathCreateRequest, request: Request):
    start_time = datetime.utcnow()

    logger.info("📥 Received Learning Path Request")
    logger.info(f"➡ Endpoint: {request.url.path}")
    logger.info(f"➡ Payload: {json.dumps(payload.dict(), indent=2)}")

    try:
        logger.info("⚙️ Running Learning Path Graph...")
        result = learning_path_graph.invoke(payload.dict())
        logger.info("✅ Graph Execution Completed")

        path = result.get("learning_path")

        if not path:
            raise ValueError("Graph returned no result")

        exec_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"⏳ Learning Path generation took {exec_time} seconds")
        logger.info("📤 Sending Learning Path Response")

        return path

    except Exception as e:
        logger.error("❌ Error during learning path generation")
        logger.error(f"Exception: {str(e)}")
        logger.error(traceback.format_exc())

        raise HTTPException(
            status_code=500,
            detail=f"Learning path generation failed: {str(e)}"
        )


# ---------------------------------------------------------
# TOPIC CONTENT GENERATION
# ---------------------------------------------------------
@app.post("/api/generate-topic-content", response_model=TopicContentResponse)
async def generate_topic_content(payload: TopicContentGenerateRequest, request: Request):
    start_time = datetime.utcnow()

    logger.info("📥 Received Topic Content Request")
    logger.info(f"➡ Endpoint: {request.url.path}")
    logger.info(f"➡ Payload: {json.dumps(payload.dict(), indent=2)}")

    try:
        logger.info("⚙️ Running Content Generation Graph...")
        result = content_graph.invoke(payload.dict())
        logger.info("✅ Graph Execution Completed")

        contents = result.get("topic_content")

        if not contents:
            raise ValueError("No content generated")

        exec_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"⏳ Topic Content generation took {exec_time} seconds")
        logger.info("📤 Sending Topic Content Response")

        return {
            "topic_id": payload.topic_id,
            "topic_name": payload.topic_name,
            "content": contents
        }

    except Exception as e:
        logger.error("❌ Error during content generation")
        logger.error(f"Exception: {str(e)}")
        logger.error(traceback.format_exc())

        raise HTTPException(
            status_code=500,
            detail=f"Topic content creation failed: {str(e)}"
        )

# file structure:
# - main.py
# - schemas.py
# - graphs/
#   - __init__.py
#   - learning_path.py
#   - content_gen.py
# - utils/
#   - __init__.py
#   - common.py

# To run the service:
# 1. Install dependencies: pip install fastapi uvicorn
# 2. Start the server: uvicorn main:app --reload