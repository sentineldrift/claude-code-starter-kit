"""
Local RAG Semantic Search — project-agnostic version.

Indexes any project's markdown docs + Python scripts into ChromaDB.
Claude can query for fuzzy context without loading entire files.

Usage:
    python scripts/local_rag_server.py index
    python scripts/local_rag_server.py search "my query"
    python scripts/local_rag_server.py stats

Configuration:
    Set PROJECT_ROOT env var or edit BASE below.
"""

import os
import sys
import json
from pathlib import Path

# --- CONFIG ---
# Defaults to the parent of this script. Override with PROJECT_ROOT env var.
BASE = Path(os.environ.get("PROJECT_ROOT", Path(__file__).parent.parent)).resolve()
CHROMA_PATH = BASE / ".claude" / "rag_chroma_db"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Directories to index (relative to BASE)
DOC_DIRS = ["docs", "results", "README.md", "."]  # indexes any .md
CODE_DIRS = ["scripts", "src"]                     # indexes .py, .js, .ts
# Extensions to skip
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".claude"}


def index_project():
    import chromadb
    from chromadb.utils import embedding_functions

    CHROMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )

    docs_coll = client.get_or_create_collection(name="project_docs", embedding_function=ef)
    code_coll = client.get_or_create_collection(name="project_code", embedding_function=ef)

    # --- Index markdown ---
    md_files = []
    for p in BASE.rglob("*.md"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        md_files.append(p)

    print(f"Indexing {len(md_files)} markdown files...", flush=True)
    docs_text, docs_meta, docs_ids = [], [], []
    for i, p in enumerate(md_files):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            chunks = [text[j:j + 1000] for j in range(0, len(text), 800)]
            for ci, chunk in enumerate(chunks[:50]):
                if len(chunk.strip()) < 50:
                    continue
                docs_text.append(chunk)
                docs_meta.append({"path": str(p.relative_to(BASE)), "chunk": ci, "type": "markdown"})
                docs_ids.append(f"md_{i}_{ci}")
        except Exception as e:
            print(f"Skip {p}: {e}", flush=True)

    if docs_text:
        batch = 100
        for i in range(0, len(docs_text), batch):
            docs_coll.upsert(
                ids=docs_ids[i:i + batch],
                documents=docs_text[i:i + batch],
                metadatas=docs_meta[i:i + batch],
            )
        print(f"Indexed {len(docs_text)} doc chunks", flush=True)

    # --- Index code ---
    code_files = []
    for ext in ("*.py", "*.js", "*.ts", "*.go", "*.rs", "*.java"):
        for p in BASE.rglob(ext):
            if any(part in SKIP_DIRS for part in p.parts):
                continue
            code_files.append(p)

    print(f"Indexing {len(code_files)} code files...", flush=True)
    code_text, code_meta, code_ids = [], [], []
    for i, p in enumerate(code_files):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
            summary = text[:2000]
            code_text.append(summary)
            code_meta.append({"path": str(p.relative_to(BASE)), "type": p.suffix[1:]})
            code_ids.append(f"code_{i}")
        except Exception:
            continue

    if code_text:
        code_coll.upsert(ids=code_ids, documents=code_text, metadatas=code_meta)
        print(f"Indexed {len(code_text)} code files", flush=True)

    print("Indexing complete.", flush=True)


def search(query, collection_name="project_docs", n_results=5):
    import chromadb
    from chromadb.utils import embedding_functions

    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    coll = client.get_collection(name=collection_name, embedding_function=ef)
    results = coll.query(query_texts=[query], n_results=n_results)

    output = []
    for i in range(len(results["ids"][0])):
        output.append({
            "id": results["ids"][0][i],
            "path": results["metadatas"][0][i].get("path", ""),
            "preview": results["documents"][0][i][:300],
            "distance": float(results["distances"][0][i]) if "distances" in results else 0.0,
        })
    return output


def stats():
    import chromadb
    from chromadb.utils import embedding_functions

    if not CHROMA_PATH.exists():
        print("No index yet. Run: python scripts/local_rag_server.py index")
        return
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
    for name in ("project_docs", "project_code"):
        try:
            coll = client.get_collection(name=name, embedding_function=ef)
            print(f"{name}: {coll.count()} items")
        except Exception:
            print(f"{name}: not indexed yet")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "index":
        index_project()
    elif cmd == "search":
        query = " ".join(sys.argv[2:])
        coll = "project_code" if query.startswith("code:") else "project_docs"
        if coll == "project_code":
            query = query[5:].strip()
        results = search(query, collection_name=coll)
        print(json.dumps(results, indent=2))
    elif cmd == "stats":
        stats()
    else:
        print(f"Unknown command: {cmd}")
