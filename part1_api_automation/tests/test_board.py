import pytest
# ---------------- STU_BOARD_01 ----------------

def test_get_article_list(rest_client, valid_headers, board_id, test_board_data):
    """STU_BOARD_01-001: 게시글 목록 조회"""
    query = test_board_data["queries"]["article_list"]
    
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/list/",
        headers=valid_headers,
        params={**query, "board_id": board_id}
    )
    assert response.status_code == 200, f"예상치 못한 상태 코드: {response.status_code}"

    body = response.json()
    
    assert "board_articles" in body, "응답에 게시글 목록(board_articles)이 포함되어 있지 않습니다."

def test_articles_sorted_by_latest(classroom_client, valid_headers, classroom_id, test_board_data):
    """STU_BOARD_01-002: 게시글 최신순 정렬 조회"""
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
            
            # 내림차순(최신순)이므로 앞의 날짜 문자열이 뒤보다 크거나 같아야 함
            assert current_date >= next_date, \
                f"정렬 오류: {i}번({current_date})보다 {i+1}번({next_date})이 더 최신입니다!"

def test_articles_sorted_by_likes(classroom_client, valid_headers, classroom_id, test_board_data):
    """STU_BOARD_01-003: 게시글 좋아요순 정렬 조회"""
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
            
            # 앞의 글 좋아요 수가 뒤의 글보다 크거나 같아야 함
            assert current_likes >= next_likes, \
                f"정렬 오류: {i}번({current_likes}개)보다 {i+1}번({next_likes}개)의 좋아요가 더 많습니다!"

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

# ---------------- STU_BOARD_02 ----------------

def test_create_article_success(rest_client, valid_headers, classroom_id, create_article_data):
    """STU_BOARD_02_001: 게시글 작성"""
    
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
    
    payload = {
        **create_article_data,
        "classroom_id": classroom_id
    }
    
    # parametrize에서 지정한 키를 데이터에서 삭제
    payload.pop(missing_key, None) 

    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        data=payload
    )

    res_data = response.json()

    assert res_data["_result"]["status"] == "fail"
    assert res_data["_result"]["status_code"] == expected_status, \
        f"{missing_key} 누락 시 {expected_status}를 기대했으나 {res_data['_result']['status_code']}가 옴"

    assert res_data.get("board_article_id") is None, \
        f"{missing_key}가 없는데 게시글이 생성됨!"
        
def test_get_linked_courses(classroom_client, valid_headers, classroom_id, test_board_data):
    """STU_BOARD_02_003: 게시글 작성 연결 과목 조회"""

    endpoint = f"/classroom/{classroom_id}/course"
    query = test_board_data["queries"]["course_query"]

    response = classroom_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params=query
    )

    assert response.status_code == 200, f"조회 실패: {response.status_code}"
    courses = response.json()
    assert isinstance(courses, list), "응답 형식이 리스트가 아닙니다."
    
    if len(courses) > 0:
        # 첫 번째 과목에 필수 필드가 있는지 확인
        assert "id" in courses[0], "과목 ID 필드가 없습니다."
        assert "title" in courses[0], "과목 제목 필드가 없습니다."

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
    
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/get/",
        headers=valid_headers,
        params={"board_article_id": article_id}
    )
    
    body = response.json()
    
    assert body["_result"]["status"] == expected_result
    assert body["_result"]["status_code"] == expected_status
    
    if expected_result == "ok":
        assert body["board_article"]["id"] == article_id
        assert "title" in body["board_article"]
    else:
        assert body["fail_code"] == expected_fail_code
        assert body["fail_message"] == "bad request"
        assert "board_article" not in body

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
    
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/get/",
        headers=valid_headers,
        params={"board_article_id": article_id}
    )
    
    body = response.json()
    
    # 실패해야 정상
    # 현재는 AssertionError가 발생하여 xfail 처리
    assert body["_result"]["status"] == "fail", f"보안 취약점: ID {article_id} 비밀글이 조회됨"
    assert body["_result"]["status_code"] == 409
    assert body["fail_code"] == "insufficient_permission"
        