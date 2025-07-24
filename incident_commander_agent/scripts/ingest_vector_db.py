from __future__ import annotations
import os, glob, uuid
from agent.memory.semantic_vector import VectorIndex, VectorDoc
from agent.tools.mcp_server import MCPServer
from agent.config import config
from agent.embeddings import embed_one

def read_markdown_files(path: str):
    for p in glob.glob(os.path.join(path, "*.md")):
        with open(p, "r") as f:
            yield os.path.basename(p), f.read()

def chunk_text(text: str, max_tokens: int = 512, overlap_tokens: int = 50):
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunk = " ".join(words[i:i+max_tokens])
        chunks.append(chunk)
        i += max_tokens - overlap_tokens
    return chunks

def main():
    vec = VectorIndex()
    server = MCPServer(vec)

    for folder, kind in [("data_fixtures/incidents", "incident"),
                         ("data_fixtures/runbooks", "runbook")]:
        for name, text in read_markdown_files(folder):
            for chunk in chunk_text(text):
                vid = str(uuid.uuid4())
                v = embed_one(chunk)
                vec.upsert([VectorDoc(id=vid, text=chunk, metadata={"type": kind, "source": name}, vector=v)])
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
