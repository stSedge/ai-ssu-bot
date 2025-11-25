import json
import re
from pathlib import Path


def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"(наверх|рисунок|фото:.*|изображение:.*)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[\*\#•«»\"“”]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text: str, max_chars: int = 1500, overlap: int = 150):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current_chunk = ""

    for s in sentences:
        if len(current_chunk) + len(s) + 1 <= max_chars:
            current_chunk += (" " + s).strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)

            overlap_text = current_chunk[-overlap:].strip() if current_chunk else ""

            current_chunk = (overlap_text + " " + s).strip()

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def process_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_chunks = []
    idx = 1
    
    MAX_CHARS_FOR_CHUNK = 750
    OVERLAP_CHARS = 80
    MIN_CHARS_FOR_CHUNK = 150

    for item in data:
        raw_text = item.get("content") or ""
        if not raw_text.strip():
            continue

        clean = clean_text(raw_text)
        chunks = chunk_text(clean, max_chars=MAX_CHARS_FOR_CHUNK, overlap=OVERLAP_CHARS)

        for ch in chunks:
            if len(ch) < MIN_CHARS_FOR_CHUNK:
                continue

            all_chunks.append({
                "id": idx,
                "text": ch,
                "source": item.get("url") or "unknown"
            })
            idx += 1

    return all_chunks


if __name__ == "__main__":
    input_path = Path("data_ssu.json")
    output_path = Path("sgu_prepared.json")

    chunks = process_json(str(input_path))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Подготовлено {len(chunks)} чанков")
