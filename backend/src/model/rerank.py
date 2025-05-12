from __future__ import annotations

import os.path
from typing import Any
from typing import Optional, Sequence

from flashrank import Ranker
from flashrank.Ranker import RerankRequest
from langchain.callbacks.manager import Callbacks
from langchain.pydantic_v1 import Extra
from langchain.retrievers.document_compressors.base import BaseDocumentCompressor
from langchain.schema import Document


class FlashRerank(BaseDocumentCompressor):
    # put path here
    model_name: str = "ms-marco-MiniLM-L-12-v2"
    """Model name to use for reranking."""
    top_n: int = 3
    """Number of documents to return."""
    model: Optional[Any] = None

    def flashRank(self, query, docs):
        # model_inputs = [[query, doc] for doc in docs]
        passages = []
        if self.model is None:
            self.model = Ranker(
                model_name="ms-marco-MultiBERT-L-12",
                cache_dir=os.path.join("cache","rerank")
            )
        for i, response in enumerate(docs):
            passages.append(
                {
                    "id": int(i),
                    "text": response,
                    "meta": {"additional": f"info{i}"},
                }
            )
        rerankReq = RerankRequest(query=str(query), passages=passages)
        results = self.model.rerank(rerankReq)
        score_mapping = {result["id"]: result["score"] for result in results}
        sorted_results = sorted(
            score_mapping.items(), key=lambda item: item[1], reverse=True
        )
        return sorted_results[: self.top_n]

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """
        Compress documents using BAAI/bge-reranker models.

        Args:
            documents: A sequence of documents to compress.
            query: The query to use for compressing the documents.
            callbacks: Callbacks to run during the compression process.

        Returns:
            A sequence of compressed documents.
        """
        if len(documents) == 0:  # to avoid empty api call
            return []
        doc_list = list(documents)
        _docs = [d.page_content for d in doc_list]
        results = self.flashRank(query, _docs)
        final_results = []
        for r in results:
            print("r", r)
            doc = doc_list[r[0]]
            doc.metadata["relevance_score"] = r[1]
            # Hyper Parameter
            if doc.metadata["relevance_score"] > 0.3:
                final_results.append(doc)
        return final_results
