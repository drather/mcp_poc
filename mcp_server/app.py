import requests
import json
import re

# Phase 1에서 만든 WAS API 주소 (Docker로 실행되고 Nginx를 통해 80번 포트로 접근)
WAS_API_URL = "http://127.0.0.1/api/tasks"

# RAG API 주소
RAG_API_URL = "http://127.0.0.1:8008/ask"

def call_was_api(query: str):
    """
    할 일(Task) 관련 API를 호출하는 도구
    """
    print(">>> 도구: WAS API 호출")
    try:
        if "추가" in query or "등록" in query:
            content = query.split("을 추가")[0].split("을 등록")[0].replace("'", "").replace('"', "")
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
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"RAG API 호출 오류: {e}"}

def run_combined_task(query: str):
    """
    RAG 검색 결과에 기반하여 WAS 작업을 수행하는 복합 도구
    """
    print(">>> 복합 작업 실행: RAG 검색 -> WAS 작업 추가")
    
    print("1단계: RAG 시스템에서 정보 검색...")
    rag_response = call_rag_system(query)
    rag_answer = rag_response.get('answer', 'RAG에서 답변을 찾지 못했습니다.')
    
    # 아래 라인을 추가하여 전체 답변을 확인
    print(f"\n--- RAG 전체 답변 확인 ---\n{rag_answer}\n--------------------------\n")
    
    print("2단계: RAG 답변을 기반으로 새 작업 내용 생성...")
    task_content = "RAG 기반 작업"
    # 최종적으로 수정한 정규표현식
    match = re.search(r"'(.*?)'", query)
    if match:
        task_content = match.group(1)
        
    new_task_description = f"'{task_content}' (근거: {rag_answer[:80]}...)"
    
    print(f"3단계: 생성된 내용으로 WAS에 작업 추가 요청...")
    return call_was_api(f"'{new_task_description}' 할 일을 추가해줘")


def router(query: str):
    """
    사용자 질문의 의도를 파악하여 적절한 도구를 호출하는 라우터
    """
    print(f"\n[사용자 질문] \"{query}\"")
    
    task_keywords = ["할 일", "업무", "작업", "task"]
    reference_keywords = ["참고해서", "바탕으로", "찾아서", "보고"]
    
    is_task_query = any(keyword in query for keyword in task_keywords)
    is_reference_query = any(keyword in query for keyword in reference_keywords)
    
    if is_task_query and is_reference_query:
        return run_combined_task(query)
    elif is_task_query:
        return call_was_api(query)
    else:
        return call_rag_system(query)

if __name__ == "__main__":
    # --- 테스트 케이스 ---
    response1 = router("현재 할 일 목록 보여줘")
    print(response1)

    response2 = router("인프라팀 역할이 뭐야?")
    print(response2)
    
    response3 = router("'MCP 기능 회의' 할 일을 추가해줘")
    print(response3)
    
    response4 = router("인프라 미들웨어 변경 내역을 참고해서 '월간 인프라팀 보고서 작성' 할 일을 추가해줘")
    print(response4)