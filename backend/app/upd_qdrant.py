import json
import logging
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)
from emb_model import embedding_model

logger = logging.getLogger(__name__)

COLLECTION_NAME = "ssu_docs"
def update_qdrant(qdrant_client: QdrantClient, data_path: str = "data/sgu_prepared.json"):
    logger.info("Начало обновления Qdrant из файла %s", data_path)

    with open(data_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    if not records:
        logger.warning("Файл %s пуст.", data_path)
        return {"status": "empty"}
    
    qdrant_client.delete_collection(COLLECTION_NAME)
    existing = qdrant_client.get_collections().collections
    logger.info("!")
    if not any(c.name == COLLECTION_NAME for c in existing):
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=embedding_model.dim, distance=Distance.COSINE)
        )

    points: List[PointStruct] = []
    for rec in records:
        text = rec.get("text", "")
        if not text.strip():
            continue

        vector = embedding_model.encode(text).tolist()
        points.append(
            PointStruct(
                id=rec["id"],
                vector=vector,
                payload={
                    "text": text,
                    "keywords": rec.get("keywords", []),
                    "source": rec.get("source", "")
                }
            )
        )
    logger.info("!!!")
    if not points:
        logger.warning("Нет валидных записей для загрузки.")
        return {"status": "no_points"}

    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
    logger.info("!!")
    return {"status": "ok", "count": len(points)}
