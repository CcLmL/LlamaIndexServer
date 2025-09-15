import time
from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex, StorageContext, PromptTemplate
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.llms.deepseek import DeepSeek
import chromadb
from info import embedding_model, reranker_model
from llama_index.vector_stores.chroma import ChromaVectorStore
from config import Config


def load_and_create_nodes(data_dir):
    # 读取单个文件，需要将文件路径放到列表里，然后传给 input_files
    reader = SimpleDirectoryReader(
        input_dir=data_dir
    )

    docs = reader.load_data()  # 返回的是一个列表，该列表只有一个 Document 对象
    # Settings.embed_model = HuggingFaceEmbedding(model_name=Config.EMBED_MODEL_PATH, device='cpu')
    # Settings.embed_model = XinferenceEmbedding(model_uid='bge-m3', base_url='http://10.0.27.59:9997', device='cuda')

    semantic_parser = SemanticSplitterNodeParser(
        buffer_size=1,
        breakpoint_percentile_threshold=90,
        embed_model=embedding_model
    )

    # 执行语义分割
    semantic_nodes = semantic_parser.get_nodes_from_documents(docs)  # 分割的结果是由 TextNode 对象构成的列表
    return semantic_nodes


def init_vector_store(nodes):
    chroma_client = chromadb.HttpClient(host=Config.CHROMA_HOST, port=Config.CHROMA_PORT)

    # 创建或者获取集合（首次运行是创建，第二次运行则是获取）
    chroma_collection = chroma_client.get_or_create_collection(
        name=Config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    # 判断是否需要新建索引
    if chroma_collection.count() == 0 and nodes is not None:
        # print(f"创建新索引（{len(nodes)}个节点）...")

        # 创建存储上下文
        storage_context = StorageContext.from_defaults(
            # 将 ChromaDB 的集合（collection）封装为 LlamaIndex 可识别的向量存储接口，以支持索引构建与查询。
            # 后续通过 VectorStoreIndex 构建索引时，会使用该 ChromaVectorStore 实例来添加或搜索向量。
            vector_store=ChromaVectorStore(chroma_collection=chroma_collection)
        )
        # 创建 StorageContext 对象的作用是为 LlamaIndex 提供一个统一的数据存储管理上下文，
        # 用于协调向量存储（vector store）、文档存储（docstore）和索引之间的数据流动与持久化操作。

        # 将文本节点存入文档存储（元数据+文本内容）
        storage_context.docstore.add_documents(nodes)

        # 创建索引，将节点向量化并创建可搜索的索引结构
        index = VectorStoreIndex(
            nodes,
            storage_context=storage_context,
            show_progress=True
        )
        # 在创建 VectorStoreIndex 对象时需要传入该 StorageContext 对象，以确保索引知道如何访问向量和文档。

        # 双重持久化保障，将存储上下文和索引对象保存到 Config.PERSIST_DIR 目录（双重保证）
        # storage_context.persist()
        # index.storage_context.persist()
    else:
        # print("加载已有索引...")

        # 加载存储上下文，从持久化目录加载已有状态
        storage_context = StorageContext.from_defaults(
            # persist_dir=Config.PERSIST_DIR,
            vector_store=ChromaVectorStore(chroma_collection=chroma_collection)
        )

        # 构建索引对象，基于已有向量存储重建内存索引结构
        index = VectorStoreIndex.from_vector_store(
            storage_context.vector_store,
            storage_context=storage_context,
            embed_model=embedding_model
        )

    # 安全验证
    # print("\n存储验证结果：")
    # doc_count = len(storage_context.docstore.docs)
    # print(f"DocStore记录数：{doc_count}")
    #
    # if doc_count > 0:
    #     sample_key = next(iter(storage_context.docstore.docs.keys()))
    #     print(f"示例节点ID：{sample_key}")
    # else:
    #     print("警告：文档存储为空，请检查节点添加逻辑！")

    return index


def init_llm_model():
    # 初始化大语言模型
    llm = DeepSeek(model="deepseek-chat", api_key="cc", api_base="http://10.0.27.59:8001/v1",
                   model_kwargs={"trust_remote_code": True},
                   tokenizer_kwargs={"trust_remote_code": True},
                   generate_kwargs={"temperature": 0.3,
                                    "top_p": 0.7, }  # 要让回答偏向于知识库，要让模型减少随机性，因此把temperature设置低一些，不要高于0.3)
                   )
    Settings.llm = llm

    return llm


# QA_TEMPLATE = (
#     "<|im_start|>system\n"
#     "您是一个SOP专业助手，必须严格遵循以下规则：\n"
#     "1.使用提供的知识回答问题\n"
#     "2.引用条文时标注出处\n\n"
#     "如果你不知道，就直说你不知道。如果你在不确定的时候不知道，就寻求澄清。\n"
#     "避免提及你是从上下文中获取的信息。"
#     "并根据用户问题的语言来回答。"
#     "可用知识内容（共{context_count}条）：\n{context_str}\n<|im_end|>\n"
#     "<|im_start|>user\n问题：{query_str}<|im_end|>\n"
#     "<|im_start|>assistant\n"
# )
#
# response_template = PromptTemplate(QA_TEMPLATE)


def llama_index_main(question, min_rerank_score=0.5):
    # llm, embed_model = init_llm_model(), init_embedding_model()
    # llm = init_llm_model()
    # print(question)
    # nodes = load_and_create_nodes(Config.DIR_PATH)

    # print("\n初始化向量存储...")
    start_time = time.time()
    index = init_vector_store(None)
    print(f"索引加载耗时：{time.time() - start_time:.2f}s")

    # 创建检索器和响应合成器
    retriever = index.as_retriever(
        similarity_top_k=Config.TOP_K
    )
    # response_synthesizer = get_response_synthesizer(
    #     text_qa_template=response_template,
    #     verbose=True
    # )

    # 创建查询引擎
    # query_engine = index.as_query_engine(
    #     similarity_top_k=Config.TOP_K,
    #     # text_qa_template=response_template,
    #     verbose=True
    # )

    # 执行检索-重排序-回答流程
    # start_time = time.time()

    # 1.初始检索
    initial_nodes = retriever.retrieve(question)
    retrieval_time = time.time() - start_time

    for node in initial_nodes:
        node.node.metadata['initial_score'] = node.score  # 保存初始分数到元数据

    # 2. 重排序
    reranked_nodes = reranker_model.postprocess_nodes(
        initial_nodes,
        query_str=question
    )
    rerank_time = time.time() - start_time - retrieval_time

    # 3. 过滤
    # 设置重排序得分阈值，低于此阈值的知识节点不作为参考依据
    MIN_RERANK_SCORE = min_rerank_score

    # 执行过滤
    # 一般对模型的回复做限制就从filtered_nodes的返回值下手
    filtered_nodes = [
        node for node in reranked_nodes
        if node.score > MIN_RERANK_SCORE
    ]

    # if len(filtered_nodes) == 0:
    #   print("\n您好！我是劳动法咨询助手，专注解答《劳动法》《劳动合同法》等相关问题，其他问题无法回答。")

    # 4. 合成答案
    # response = response_synthesizer.synthesize(
    #     question,
    #     nodes=filtered_nodes  # 使用过滤后的节点
    # )
    synthesis_time = time.time() - start_time - retrieval_time - rerank_time
    # 执行查询
    # response = query_engine.query(question)

    # 显示结果
    res_data = []
    print(f"\n[性能分析] 检索: {retrieval_time:.2f}s | 重排序: {rerank_time:.2f}s | 合成: {synthesis_time:.2f}s")
    for filtered_node in filtered_nodes:
        record_dict_temp = {}
        record_dict_temp['metadata'] = {
            "path": filtered_node.metadata.get("file_path"),
            "description": filtered_node.metadata.get("file_name"),
        }
        record_dict_temp['score'] = filtered_node.score
        record_dict_temp['title'] = filtered_node.metadata.get("file_name")
        record_dict_temp['content'] = filtered_node.text
        res_data.append(record_dict_temp)
    # for idx, node in enumerate(response.source_nodes, 1):
    #     meta = node.metadata
    #     print(f"\n[{idx}] {meta['full_title']}")
    #     print(f"  meta{meta}")
    #     print(f"  条款内容：{node.text[:100]}...")
    #     print(f"  相关度得分：{node.score:.4f}")

    return res_data


if __name__ == '__main__':
    llama_index_main('为什么要进行计算机化系统的验证？')
