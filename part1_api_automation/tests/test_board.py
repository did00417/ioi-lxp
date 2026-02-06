import pytest
import logging

logger = logging.getLogger(__name__)
# ---------------- STU_BOARD_01 ----------------

def test_get_article_list(rest_client, valid_headers, board_id, test_board_data):
    """STU_BOARD_01-001: 게시글 목록 조회"""
    logger.info("=== STU_BOARD_01-001: 게시글 목록 조회 시작 ===")
    query = test_board_data["queries"]["article_list"]
    logger.debug(f"파라미터: {query}")
    
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/list/",
        headers=valid_headers,
        params={**query, "board_id": board_id}
    )
    
    if response.status_code != 200:
        logger.error(f"요청 실패! 상태 코드: {response.status_code} | 응답: {response.text}")
    
    assert response.status_code == 200

    body = response.json()
    assert "board_articles" in body, "응답에 게시글 목록(board_articles)이 포함되어 있지 않습니다."
    logger.info("게시글 목록 조회 완료")

def test_articles_sorted_by_latest(classroom_client, valid_headers, classroom_id, test_board_data):
    """STU_BOARD_01-002: 게시글 최신순 정렬 조회"""
    logger.info("=== STU_BOARD_01-002: 게시글 최신순 정렬 조회 시작 ===")
    query = test_board_data["queries"]["sort_latest"]
    
    response = classroom_client.get(
        endpoint=f"/classroom/{classroom_id}/article",
        headers=valid_headers,
        params=query
    )
    
    assert response.status_code == 200, f"예상치 못한 상태 코드: {response.status_code}"
    articles = response.json()
    
    if len(articles) >= 2:
        for i in range(len(articles) - 1):
            current_date = articles[i]['created']
            next_date = articles[i+1]['created']
            
            logger.debug(f"정렬 비교 중: {current_date} vs {next_date}")
            assert current_date >= next_date
    logger.info("최신순 정렬 검증 완료")

def test_articles_sorted_by_likes(classroom_client, valid_headers, classroom_id, test_board_data):
    """STU_BOARD_01-003: 게시글 좋아요순 정렬 조회"""
    logger.info("=== STU_BOARD_01-003: 게시글 좋아요순 정렬 조회 시작 ===")
    query = test_board_data["queries"]["sort_likes"]
    
    response = classroom_client.get(
        endpoint=f"/classroom/{classroom_id}/article",
        headers=valid_headers,
        params=query
    )
    assert response.status_code == 200, f"조회 실패: {response.status_code}"
    articles = response.json()

    if len(articles) >= 2:
        for i in range(len(articles) - 1):
            current_likes = articles[i]['like_count']
            next_likes = articles[i+1]['like_count']
            
            logger.debug(f"정렬 비교 중: {current_likes} vs {next_likes}")
            assert current_likes >= next_likes
    logger.info("좋아요순 정렬 검증 완료")

@pytest.mark.parametrize("keyword, expected_count_min", [
    ("%커리큘럼%", 1),  # 1. 검색 결과가 있어야 하는 케이스
    ("%바나나%", 0)    # 2. 검색 결과가 없어야 하는 케이스
])
def test_get_article_list_by_filter(
    rest_client,
    valid_headers,
    board_id,
    keyword,
    expected_count_min,
    test_board_data
):
    """STU_BOARD_01-004: 제목 키워드 검색"""
    """STU_BOARD_01-005: 제목 키워드 일치하는 검색 결과 없음"""
    logger.info(f"=== 검색 테스트 시작: 키워드 '{keyword}' ===")
    query = test_board_data["queries"]["article_list"]
    
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/list/",
        headers=valid_headers,
        params={**query, "board_id": board_id, "filter_title": keyword}
    )
    assert response.status_code == 200
    
    body = response.json()
    articles = body.get("board_articles", [])
    article_count = body.get("board_article_count", 0)
    logger.info(f"검색 결과 수: {len(articles)} (기대 최소값: {expected_count_min})")
    
    if expected_count_min > 0:
        # 결과가 있어야 하는 경우
        assert len(articles) >= expected_count_min, f"'{keyword}' 검색 결과가 없습니다."
        # 모든 결과에 키워드가 포함되어 있는지
        for article in articles:
            clean_keyword = keyword.replace("%", "") # % 제거 후 실제 텍스트만 비교
            assert clean_keyword in article['title'], f"제목에 '{clean_keyword}'가 포함되어 있지 않습니다: {article['title']}"
    else:
        # 결과가 없어야 하는 경우
        assert len(articles) == 0, f"'{keyword}' 검색 결과가 없어야 하는데 {len(articles)}개가 발견되었습니다."
        assert article_count == 0, "board_article_count가 0이 아닙니다."
    logger.info(f"'{keyword}' 검색 테스트 완료")

# ---------------- STU_BOARD_02 ----------------

def test_create_article_success(rest_client, valid_headers, classroom_id, create_article_data):
    """STU_BOARD_02_001: 게시글 작성"""
    logger.info("=== STU_BOARD_02_001: 게시글 작성 테스트 시작 ===")
    
    payload = {
        **create_article_data,
        "classroom_id": classroom_id
    }
    
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        data=payload
    )

    assert response.status_code == 200, f"작성 실패: {response.status_code}"
    
    res_data = response.json()
    assert res_data["_result"]["status"] == "ok"
    
    article_id = res_data.get("board_article_id")
    logger.info(f"게시글 작성 성공! 생성된 ID: {res_data.get('board_article_id')}")
    assert article_id is not None, "게시글 ID가 생성되지 않았습니다."

@pytest.mark.parametrize("missing_key, expected_status", [
    ("classroom_id", 409), # (1) classroom_id 누락
    ("title", 400),        # (2) title 누락
    ("content", 400)       # (3) content 누락
])
def test_create_article_fail_by_missing_param(
    rest_client, 
    valid_headers, 
    classroom_id, 
    create_article_data, 
    missing_key, 
    expected_status
):
    """STU_BOARD_02_002: 게시글 작성 필수값 누락 검증"""
    logger.info(f"=== STU_BOARD_02_002: 필수값 누락 검증 시작 (누락 키: {missing_key}) ===")
    payload = {
        **create_article_data,
        "classroom_id": classroom_id
    }
    
    # parametrize에서 지정한 키를 데이터에서 삭제
    payload.pop(missing_key, None) 
    logger.debug(f"요청 페이로드 (누락 적용): {payload}")

    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        data=payload
    )

    res_data = response.json()
    logger.debug(f"응답 데이터: {res_data}")
    
    if res_data["_result"]["status_code"] != expected_status:
        logger.error(f"상태 코드 불일치! 기대: {expected_status}, 실제: {res_data['_result']['status_code']}")

    assert res_data["_result"]["status"] == "fail"
    assert res_data["_result"]["status_code"] == expected_status
    assert res_data.get("board_article_id") is None
    
    logger.info(f"=== STU_BOARD_02_002: {missing_key} 누락 케이스 검증 완료 ===")
        
def test_get_linked_courses(classroom_client, valid_headers, classroom_id, test_board_data):
    """STU_BOARD_02_003: 게시글 작성 연결 과목 조회"""
    logger.info("=== STU_BOARD_02_003: 연결 과목 조회 시작 ===")

    endpoint = f"/classroom/{classroom_id}/course"
    query = test_board_data["queries"]["course_query"]
    logger.debug(f"API 요청 경로: {endpoint} | 파라미터: {query}")

    response = classroom_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params=query
    )

    assert response.status_code == 200, f"조회 실패: {response.status_code}"
    courses = response.json()
    logger.info(f"조회된 과목 수: {len(courses)}")
    assert isinstance(courses, list), "응답 형식이 리스트가 아닙니다."
    
    if len(courses) > 0:
        # 첫 번째 과목에 필수 필드가 있는지 확인
        assert "id" in courses[0], "과목 ID 필드가 없습니다."
        assert "title" in courses[0], "과목 제목 필드가 없습니다."
        logger.debug(f"첫 번째 과목 데이터 확인: {courses[0]}")
    logger.info("=== STU_BOARD_02_003: 테스트 완료 ===")

@pytest.mark.parametrize("article_id, expected_status, expected_result, expected_fail_code", [
    (65912, 200, "ok", None),                  # 정상 조회
    (99999, 400, "fail", "resource_not_found")  # 존재하지 않는 게시글
])
def test_get_article_detail_cases(
    rest_client, 
    valid_headers, 
    article_id, 
    expected_status, 
    expected_result,
    expected_fail_code
):
    """STU_BOARD_02_004: 특정 게시글 조회"""
    """STU_BOARD_02_005: 존재하지 않는 게시글 상세 조회"""
    logger.info(f"=== 상세 조회 테스트 시작 (ID: {article_id}) ===")
    
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/get/",
        headers=valid_headers,
        params={"board_article_id": article_id}
    )
    
    body = response.json()
    logger.debug(f"응답 결과: {body}")
    
    assert body["_result"]["status"] == expected_result
    assert body["_result"]["status_code"] == expected_status
    
    if expected_result == "ok":
        logger.info(f"정상 조회 성공: {body['board_article']['title']}")
        assert body["board_article"]["id"] == article_id
        assert "title" in body["board_article"]
    else:
        logger.warning(f"에러 케이스 검증 (결과: {expected_fail_code})")
        assert body["fail_code"] == expected_fail_code
        assert body["fail_message"] == "bad request"
        assert "board_article" not in body
    
    logger.info(f"=== 상세 조회 케이스(ID: {article_id}) 완료 ===")

@pytest.mark.parametrize("article_id", [
    67176,  # 타인A의 비밀글 ID
    67183   # 타인B의 비밀글 ID
])
@pytest.mark.xfail(reason="보안 버그: 타인의 비밀글이 권한 체크 없이 조회됨")
def test_get_others_private_article_security_bug(rest_client, valid_headers, article_id):
    """
    STU_BOARD_02_006: 타인 비밀글 조회
    기대 결과: status 'fail', fail_code 'insufficient_permission' 반환하며 차단되어야 함
    현재 현상: 200 OK와 함께 게시글 내용이 반환됨
    """
    logger.info(f"=== STU_BOARD_02_006 보안 취약점 테스트 (ID: {article_id}) ===")
    
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/get/",
        headers=valid_headers,
        params={"board_article_id": article_id}
    )
    
    body = response.json()
    
    if body["_result"]["status"] == "ok":
        logger.critical(f"보안 경고: 비밀글(ID: {article_id})이 타인에게 노출됨!")
    
    # 실패해야 정상
    # 현재는 AssertionError가 발생하여 xfail 처리
    assert body["_result"]["status"] == "fail", f"보안 취약점: ID {article_id} 비밀글이 조회됨"
    assert body["_result"]["status_code"] == 409
    assert body["fail_code"] == "insufficient_permission"
    logger.info("=== 보안 테스트 시나리오 종료 ===")

def test_update_article_success(rest_client, valid_headers, classroom_id, test_board_data):
    """STU_BOARD_02_007: 게시글 수정"""
    logger.info("=== STU_BOARD_02_007: 게시글 수정 테스트 시작 ===")

    edit_data = test_board_data["edit_article"]
    article_id = edit_data["board_article_id"]
    
    payload = {
        "board_article_id": article_id,
        **edit_data["update_payload"],
        "classroom_id": classroom_id
    }
    
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)
    
    response = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        data=payload
    )

    res_data = response.json()
    logger.debug(f"API 응답 데이터: {res_data}")

    assert res_data["_result"]["status"] == "ok"
    assert res_data["_result"]["status_code"] == 200
    assert res_data["board_article_id"] == article_id

    logger.info(f"=== STU_BOARD_03_001: ID {article_id} 수정 검증 완료 ===")

def test_update_others_article_fail(rest_client, valid_headers, classroom_id, test_board_data):
    """STU_BOARD_02_008: 타인 게시글 수정 시도"""
    logger.info("=== STU_BOARD_02_008: 타인 게시글 수정 시도 테스트 시작 ===")

    edit_data = test_board_data["edit_others_article"]
    article_id = edit_data["board_article_id"]
    
    payload = {
        "board_article_id": article_id,
        **edit_data["update_payload"],
        "classroom_id": classroom_id
    }
    
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        data=payload
    )

    res_data = response.json()
    logger.debug(f"타인 글 수정 시도 응답: {res_data}")

    assert res_data["_result"]["status"] == "fail", f"보안 취약점: 타인의 게시글({article_id})이 수정되었습니다!"

    assert res_data["_result"]["status_code"] == 400
    assert res_data["fail_code"] == "resource_not_found"

    logger.info(f"=== STU_BOARD_03_002: 타인 게시글({article_id}) 수정 차단 확인 완료 ===")

def test_delete_article_success(rest_client, valid_headers, classroom_id, create_article_data):
    """STU_BOARD_02_009: 게시글 삭제 """
    """반복 테스트를 위해 게시글 생성 후 삭제 로직"""
    logger.info("=== STU_BOARD_02_009: 게시글 삭제 테스트 시작 ===")

    # 1. ID 확보용 게시글 생성
    create_payload = {**create_article_data, "classroom_id": classroom_id}
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    create_res = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        data=create_payload
    )
    
    # 생성된 글의 ID를 가져옵니다.
    article_id = create_res.json().get("board_article_id")
    logger.info(f"삭제 테스트를 위한 임시 게시글 생성 완료 (ID: {article_id})")

    # 2. 방금 생성된 ID로 삭제 요청
    delete_payload = {"board_article_id": article_id}

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/delete/",
        headers=headers,
        data=delete_payload
    )

    res_data = response.json()
    assert res_data["_result"]["status"] == "ok"
    assert res_data["_result"]["status_code"] == 200
    
    logger.info(f"=== ID {article_id} 삭제 검증 완료 ===")