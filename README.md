## Azure Cosmos DB와 Flask를 사용한 문서 관계 탐색 API
이 프로젝트는 Azure Cosmos DB에 저장된 문서 데이터를 기반으로 특정 문서와 관련된 문서를 탐색하는 API를 제공합니다. 
API는 Flask 프레임워크를 사용하여 구현되었으며, Azure Functions에서 배포될 수 있습니다.

### 기능
- 특정 문서를 기준으로 관련된 표준 문서를 탐색합니다.
- BFS(Breadth-First Search) 알고리즘을 사용하여 관련 문서를 탐색합니다.
- 탐색 결과에는 문서의 계층 구조(depth)와 부모 문서 정보가 포함됩니다.
- 탐색 결과에는 각 문서의 세부 정보(제목, 버전, 연도, 소유 여부)가 포함됩니다.
- CORS(Cross-Origin Resource Sharing)를 지원하여 다른 도메인에서의 API 호출을 허용합니다.

### 사용 방법
- 필요한 Python 패키지를 설치합니다. (Flask, azure-cosmos, flask-cors)
- 로컬에서 테스트하려면 python function_app.py 명령을 사용하여 Flask 서버를 실행합니다.
- Azure Functions에 배포하려면 프로젝트를 함수 앱으로 구성하고 배포합니다.
- API 엔드포인트는 /api/standards이며, subcommittee_standard_no 쿼리 매개변수를 사용하여 기준 문서를 지정합니다.

### 코드 구조
- bfs 함수: BFS 알고리즘을 사용하여 관련 문서를 탐색합니다.
- find_referencing_nodes 함수: 기준 문서를 참조하는 상위 문서를 찾습니다.
- get_standard_details 함수: 문서의 세부 정보를 가져옵니다.
- main 함수: API 요청을 처리하고 응답을 반환합니다.

### 종속성
- Flask: 웹 프레임워크
- azure-cosmos: Azure Cosmos DB 클라이언트 라이브러리
- flask-cors: CORS 지원을 위한 Flask 확장
