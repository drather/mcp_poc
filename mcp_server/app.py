import requests
import json

# Phase 1에서 만든 WAS API 주소 (Docker로 실행되고 Nginx를 통해 80번 포트로 접근)
WAS_API_URL = "http://127.0.0.1/api/tasks"

# RAG API 주소 (가상)
# 추후 rag_poc 프로젝트를 API로 실행했을 때의 주소를 사용합니다.
RAG_API_URL = "http://127.0.0.1:8008/ask"

def call_was_api(query: str):
    """
    할 일(Task) 관련 API를 호출하는 도구
    - 질문에 '목록', '보여줘' 등이 있으면 GET 요청
    - 질문에 '추가', '등록' 등이 있으면 POST 요청
    """
    print(">>> 도구: WAS API 호출")
    try:
        # PoC를 위해 간단한 키워드로 분기
        if "추가" in query or "등록" in query:
            # 실제로는 질문에서 content를 파싱해야 하지만, 여기서는 예시용 content 사용
            content = query.split("을 추가")[0].replace("'", "").replace('"', "")
            response = requests.post(WAS_API_URL, json={'content': content})
            return f"WAS API 응답 (작업 추가): {response.json()}"
        else:
            response = requests.get(WAS_API_URL)
            return f"WAS API 응답 (작업 목록): {response.json()}"

    except requests.exceptions.RequestException as e:
        return f"WAS API 호출 오류: {e}"

def call_rag_system(query: str):
    """
    지식 검색(RAG) API를 호출하는 도구
    """
    print(">>> 도구: RAG 시스템 호출")
    try:
        response = requests.post(RAG_API_URL, json={'query': query})
        response.raise_for_status()  # 4xx, 5xx 에러 발생 시 예외를 던집니다.
        return f"RAG 시스템 응답: {response.json()}"
    except requests.exceptions.RequestException as e:
        return f"RAG API 호출 오류: {e}"

def router(query: str):
    """
    사용자 질문의 의도를 파악하여 적절한 도구를 호출하는 라우터
    """
    print(f"\n[사용자 질문] \"{query}\"")
    # PoC를 위한 간단한 키워드 기반 라우팅
    task_keywords = ["할 일", "업무", "작업", "task"]
    if any(keyword in query for keyword in task_keywords):
        return call_was_api(query)
    else:
        return call_rag_system(query)

if __name__ == "__main__":
    # --- 테스트 케이스 ---
    # 1. 할 일 목록 조회 (WAS API 호출 예상)
    response1 = router("현재 할 일 목록 보여줘")
    print(response1)

    # 2. RAG 시스템에 질문 (RAG 호출 예상)
    response2 = router("인프라 미들웨어 변경 내역 알려줘")
    print(response2)
    
    # 3. 할 일 추가 (WAS API 호출 예상)
    response3 = router("'MCP 라우터 기능 검증' 할 일을 추가해줘")
    print(response3)
