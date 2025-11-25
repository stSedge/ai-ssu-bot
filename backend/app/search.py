import json
import logging
from typing import List, Dict
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, SearchRequest
from emb_model import embedding_model

logger = logging.getLogger(__name__)

COLLECTION_NAME = "ssu_docs"

def search_qdrant(query_text: str, qdrant_client: QdrantClient, top_k: int = 3) -> str:
    
    query_vector = embedding_model.encode(query_text).tolist()

    search_result = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector, 
        limit=top_k,
        with_payload=True,
    )
    if not search_result.points:
        return "Релевантная информация не найдена."

    result_parts = []

    for i, hit in enumerate(search_result.points):
        source = hit.payload.get("source", "Неизвестный источник")
        text_fragment = hit.payload.get("text", "Текст отсутствует")
        score = hit.score
        
        result_parts.append(
            f"--- Фрагмент {i + 1} (Релевантность: {score:.4f}) ---\n"
            f"Источник: **{source}**\n"
            f"Текст: {text_fragment}\n"
        )
    
    final_context = "\n\n".join(result_parts)

    return f"'{query_text}'\n\n{final_context}"