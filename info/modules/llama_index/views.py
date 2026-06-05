from info.modules.llama_index import llama_index_blu
from flask import request, Response
import json

from info.projects.main import llama_index_main
from info.utils.decorator import login_required
from info.utils.response_code import RET, error_map


@llama_index_blu.route('/retrieval', methods=["POST"])
# @login_required
def handle_llama_index_retrival():
    # {'retrieval_setting': {'top_k': 2, 'score_threshold': 0.0}, 'query': '信息中心受火灾\n', 'knowledge_id': '1212', 'metadata_condition': None}
    if request.is_json:
        print(request.json)
        query = request.json.get("query")
        min_rerank_score = request.json.get("retrieval_setting")["score_threshold"]
        top_k_str = request.json.get("retrieval_setting")["top_k"]
        data = llama_index_main(query, min_rerank_score, top_k_str)
        # data = [{
        #    "metadata": {
        #        "path": "s3://dify/knowledge.txt",
        #        "description": "dify knowledge document"
        #    },
        #    "score": 0.98,
        #    "title": "knowledge.txt",
        #    "content": "This is the document for external knowledge."
        # },
        #    {
        #        "metadata": {
        #            "path": "s3://dify/introduce.txt",
        #            "description": "dify introduce"
        #        },
        #        "score": 0.66,
        #        "title": "introduce.txt",
        #        "content": "The Innovation Engine for GenAI Applications"
        #    }
        # ]
        print(data)
        return Response(
            response=json.dumps({"records": data}),
            status=200,
            content_type="application/json"
        )
    else:
        return Response(status=200, content_type="application/json")
