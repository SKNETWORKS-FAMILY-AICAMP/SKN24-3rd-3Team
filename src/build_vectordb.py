import json
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# 프로젝트 루트 기준 경로
BASE_DIR = Path(".")
OUTPUT_DIR = BASE_DIR / "output_chunks"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "kosha_child_chunks_BAAI"
EMBEDDING_MODEL = "BAAI/bge-m3"


def load_child_chunks(output_dir: Path) -> list[dict]:
    """모든 child chunk JSON을 불러온다."""
    all_children: list[dict] = []
    for json_file in sorted(output_dir.glob("*_child_chunks.json")):
        data = json.loads(json_file.read_text(encoding="utf-8"))
        all_children.extend(data["chunks"])
    return all_children


def load_parent_chunks(output_dir: Path) -> dict[str, dict]:
    """parent chunk를 chunk_id 기준으로 매핑한다."""
    parent_map: dict[str, dict] = {}
    for json_file in sorted(output_dir.glob("*_parent_chunks.json")):
        data = json.loads(json_file.read_text(encoding="utf-8"))
        for chunk in data["chunks"]:
            parent_map[chunk["chunk_id"]] = chunk
    return parent_map


def build_collection(
    output_dir: Path = OUTPUT_DIR,
    chroma_dir: Path = CHROMA_DIR,
    collection_name: str = COLLECTION_NAME,
    embedding_model: str = EMBEDDING_MODEL,
    batch_size: int = 1000,
) -> tuple[chromadb.Collection, dict[str, dict]]:
    """청킹된 문서를 임베딩하여 ChromaDB에 저장한다."""
    embedding_fn = SentenceTransformerEmbeddingFunction(model_name=embedding_model)
    chroma_client = chromadb.PersistentClient(path=str(chroma_dir))

    existing_names = [c.name for c in chroma_client.list_collections()]
    is_new = collection_name not in existing_names

    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )

    if is_new:
        all_children = load_child_chunks(output_dir)
        print(f"자식 청크 총 {len(all_children)}개 로드")

        total = len(all_children)
        for i in range(0, total, batch_size):
            batch = all_children[i:i + batch_size]

            collection.add(
                ids=[chunk["chunk_id"] for chunk in batch],
                documents=[
                    f"{chunk['depth_1']} {chunk['depth_2']} {chunk['depth_3']} {chunk['content']}"
                    for chunk in batch
                ],
                metadatas=[
                    {
                        "parent_id": chunk.get("parent_id", ""),
                        "source": chunk["source"],
                        "title": chunk.get("title", ""),
                        "year": str(chunk.get("year", "")),
                        "status": chunk.get("status", ""),
                        "depth_1": chunk.get("depth_1", ""),
                        "depth_2": chunk.get("depth_2", ""),
                        "depth_3": chunk.get("depth_3", ""),
                        "category": chunk.get("category", ""),
                        "task": chunk.get("task", ""),
                        "space": chunk.get("space", ""),
                    }
                    for chunk in batch
                ],
            )
            print(f"{min(i + batch_size, total):,} / {total:,} 저장 완료")

    parent_map = load_parent_chunks(output_dir)

    print(f"컬렉션 이름: {collection_name}")
    print(f"현재 저장된 문서 수: {collection.count()}")
    print(f"부모 청크 {len(parent_map)}개 로드")

    return collection, parent_map


if __name__ == "__main__":
    build_collection()
