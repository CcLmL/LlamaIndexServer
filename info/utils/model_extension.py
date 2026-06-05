from llama_index.embeddings.xinference import XinferenceEmbedding
from llama_index.postprocessor.xinference_rerank import XinferenceRerank
# from llama_index.core.postprocessor import SentenceTransformerRerank
from sentence_transformers import SentenceTransformer
from config import Config


def init_embedding_model():
    """初始化模型并验证"""
    # Embedding模型
    # embed_model = HuggingFaceEmbedding(
    #     model_name=Config.EMBED_MODEL_PATH,
    #     device='cpu'
    #     # 在一些比较老版本的 llama-index-embeddings-huggingface 中，需要加下面的参数，当前版本(0.5.4)不需要
    #     # encode_kwargs = {
    #     #     'normalize_embeddings': True,
    #     #     'device': 'cuda' if hasattr(Settings, 'device') else 'cpu'
    #     # }
    # )
    embed_model = XinferenceEmbedding(model_uid='bge-m3', base_url='http://10.0.27.59:9997', device='cuda')

    return embed_model


def init_reranker_model():
    # 初始化reranker模型
    # reranker = SentenceTransformerRerank(
    #     model=Config.RERANK_MODEL_PATH,
    #     top_n=Config.RERANK_TOP_K,
    #     device='cuda'
    # )
    reranker = XinferenceRerank(model='bge-reranker-v2-m3', base_url='http://10.0.27.59:9997',
                                top_n=Config.RERANK_TOP_K)
    return reranker


class SentenceTransformerEmbeddingFunction:
    def __init__(self, model_path: str, device: str = "cuda"):
        self.model = SentenceTransformer(model_path, device=device)

    def __call__(self, input: list[str]) -> list[list[float]]:
        if isinstance(input, str):
            input = [input]
        return self.model.encode(input, convert_to_numpy=True).tolist()
