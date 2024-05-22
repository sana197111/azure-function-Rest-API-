# function_app.py
import json
import logging
import azure.functions as func
from flask import Flask, request, jsonify
from collections import deque
from azure.cosmos import CosmosClient
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Cosmos DB 접속 정보
url = "{url_data}"
key = "{cosmos db key}"
database_name = '{db_name}'
container_name = '{container_name}'

# Cosmos DB 클라이언트 초기화
client = CosmosClient(url, credential=key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

def bfs(adj_matrix, start_node, referencing_nodes, node_to_index, index_to_node, depth_limit=3):
    start_index = node_to_index[start_node]
    visited = [False] * len(adj_matrix)
    queue = deque([(start_index, 0, None)])  # 부모 노드 정보 추가
    results = []

    # 참조하는 상위 노드를 결과에 먼저 추가
    for ref_node in referencing_nodes:
        ref_index = node_to_index[ref_node]
        results.append((ref_node, -1, None))  # 상위 노드의 depth를 -1로 설정
        visited[ref_index] = True  # 상위 노드를 방문 처리

    while queue:
        current_index, current_depth, parent_node = queue.popleft()
        if not visited[current_index] and current_depth <= depth_limit:
            visited[current_index] = True
            current_node = index_to_node[current_index]
            results.append((current_node, current_depth, parent_node))

            for neighbor_index, is_connected in enumerate(adj_matrix[current_index]):
                if is_connected and not visited[neighbor_index]:
                    queue.append((neighbor_index, current_depth + 1, current_node))

    return results

def find_referencing_nodes(items, start_node):
    start_standard_no = start_node.split(' ')[-1] 
    referencing_nodes = []
    for item in items:
        if start_standard_no in item['related_standards'] or start_standard_no in item['related_other_organizations']:
            referencing_nodes.append(item['subcommittee'] + ' ' + item['standard_no'])
    return referencing_nodes

def get_standard_details(key, items):
    for item in items:
        if key == item['subcommittee'] + " " + item['standard_no']:
            return {
                "title": item["title"],
                "version": item["version"],
                "year": item["year"],
                "owned": item["owned"]
            }
    return {}

## 로컬 테스트 코드
@app.route('/api/standards', methods=['GET'])
def main(req=None):
    if req is None:
        req = func.HttpRequest(
            method='GET',
            body=None,
            url='/api/standards',
            headers={},
            params={'subcommittee_standard_no': request.args.get('subcommittee_standard_no')}
        )
    
    logging.info('Python HTTP trigger function processed a request.')
    
    subcommittee_standard_no = req.params.get('subcommittee_standard_no')
    if not subcommittee_standard_no:
        return jsonify({"error": "Please pass a subcommittee_standard_no on the query string"}), 400

    # 데이터베이스에서 데이터 가져오기
    query = "SELECT * FROM c"
    items = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))

    # 모든 고유 노드 식별 및 인덱스 매핑
    all_standards = list(set([item['subcommittee'] + ' ' + item['standard_no'] for item in items]))
    node_to_index = {node: idx for idx, node in enumerate(all_standards)}
    index_to_node = {idx: node for node, idx in node_to_index.items()}

    # 인접 행렬 초기화 및 채우기
    adj_matrix = [[0] * len(all_standards) for _ in range(len(all_standards))]

    for item in items:
        source_node = item['subcommittee'] + ' ' + item['standard_no']
        source_index = node_to_index[source_node]
        for rel in item['related_standards'] + item['related_other_organizations']:
            target_node = rel if ' ' in rel else item['subcommittee'] + ' ' + rel
            if target_node in node_to_index:
                target_index = node_to_index[target_node]
                adj_matrix[source_index][target_index] = 1
                adj_matrix[target_index][source_index] = 1

    # BFS 실행 및 결과 출력
    referencing_nodes = find_referencing_nodes(items, subcommittee_standard_no)
    results = bfs(adj_matrix, subcommittee_standard_no, referencing_nodes, node_to_index, index_to_node)

    response_data = []
    for node, depth, parent_node in results:
        node_details = get_standard_details(node, items)
        response_data.append({
            "node": node,
            "depth": depth,
            "parent": parent_node,
            "details": node_details
        })

    # 로컬 테스트 코드
    return jsonify(response_data)

# 로컬 테스트 코드
if __name__ == '__main__':
    app.run()