import os
import json
from datetime import datetime

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class PresentationRAG:
    def __init__(
        self, model_name="BAAI/bge-small-en-v1.5", db_path="presentation_vector_db"
    ):

        self.model = SentenceTransformer(model_name)

        self.db_path = db_path

        self.index = None
        self.documents = []

        os.makedirs(self.db_path, exist_ok=True)

    # =====================================================
    # ADD DOCUMENT
    # =====================================================

    def add_document(self, text, source_type, source_id=None):

        if not text:
            return

        text = text.strip()

        if not text:
            return

        document = {
            "text": text,
            "source_type": source_type,
            "source_id": source_id,
            "timestamp": datetime.now().isoformat(),
        }

        self.documents.append(document)

    # =====================================================
    # BUILD EMBEDDINGS
    # =====================================================

    def build(self):

        if not self.documents:
            print("No documents available.")

            return

        texts = [doc["text"] for doc in self.documents]

        embeddings = self.model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        )

        embeddings = np.asarray(embeddings, dtype="float32")

        dimension = embeddings.shape[1]

        # Inner Product with normalized
        # embeddings = cosine similarity

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        self.save()

    # =====================================================
    # RETRIEVE
    # =====================================================

    def retrieve(self, query, top_k=5):

        if self.index is None or not self.documents:
            return []

        query_embedding = self.model.encode(
            [query], normalize_embeddings=True, show_progress_bar=False
        )

        query_embedding = np.asarray(query_embedding, dtype="float32")

        scores, indices = self.index.search(
            query_embedding, min(top_k, len(self.documents))
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue

            document = dict(self.documents[index])

            document["score"] = float(score)

            results.append(document)

        return results

    # =====================================================
    # SAVE VECTOR DATABASE
    # =====================================================

    def save(self):

        if self.index is not None:
            faiss.write_index(self.index, os.path.join(self.db_path, "index.faiss"))

        with open(
            os.path.join(self.db_path, "documents.json"), "w", encoding="utf-8"
        ) as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)

    # =====================================================
    # LOAD VECTOR DATABASE
    # =====================================================

    def load(self):

        index_path = os.path.join(self.db_path, "index.faiss")

        documents_path = os.path.join(self.db_path, "documents.json")

        if not os.path.exists(index_path) or not os.path.exists(documents_path):
            return False

        self.index = faiss.read_index(index_path)

        with open(documents_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        return True

    # =====================================================
    # CLEAR CURRENT PRESENTATION
    # =====================================================

    def clear(self):

        self.index = None

        self.documents = []
