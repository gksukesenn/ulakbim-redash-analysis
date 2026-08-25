from typing import List, Sequence


class FastEmbedModel:
    """FastEmbed ONNX modeli üzerinden yerel CPU embedding üretir."""

    def __init__(self, model_name: str) -> None:
        try:
            from fastembed import TextEmbedding
        except ImportError as error:
            raise RuntimeError(
                "Embedding bağımlılığı eksik; `pip install -e '.[vector]'` "
                "komutunu çalıştırın."
            ) from error
        self._model = TextEmbedding(model_name=model_name)

    def _embed(self, texts: Sequence[str]) -> List[List[float]]:
        return [vector.tolist() for vector in self._model.embed(list(texts))]

    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text])[0]
