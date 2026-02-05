import pytest

def test_get_article_list(rest_client, valid_headers, board_id):
    """STU_BOARD_01-001: 게시글 목록 조회"""

    response = rest_client.get(
        endpoint="/org/qatrack/board/article/list/",
        headers=valid_headers,
        params={
            "board_id": board_id,
            "offset": 0,
            "count": 15
        }
    )
    assert response.status_code == 200, f"예상치 못한 상태 코드: {response.status_code}"

    body = response.json()
    
    assert "board_articles" in body, "응답에 게시글 목록(board_articles)이 포함되어 있지 않습니다."

def test_articles_sorted_by_latest(classroom_client, valid_headers, classroom_id):
    """STU_BOARD_01-002: 게시글 최신순 정렬 조회"""
    
    response = classroom_client.get(
        endpoint=f"/classroom/{classroom_id}/article",
        headers=valid_headers,
        params={
            "sort_by": "created_desc",
            "skip": 0,
            "count": 10,
            "filter_title": "%%"
        }
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

def test_articles_sorted_by_likes(classroom_client, valid_headers, classroom_id):
    """STU_BOARD_01-003: 게시글 좋아요순 정렬 조회"""
    
    response = classroom_client.get(
        endpoint=f"/classroom/{classroom_id}/article",
        headers=valid_headers,
        params={
            "sort_by": "like_desc",
            "skip": 0,
            "count": 10,
            "filter_title": "%%"
        }
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
    expected_count_min
):
    """STU_BOARD_01-004: 제목 키워드 검색"""
    """STU_BOARD_01-005: 제목 키워드 일치하는 검색 결과 없음"""
    
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/list/",
        headers=valid_headers,
        params={
            "board_id": board_id,
            "filter_title": keyword,
            "offset": 0,
            "count": 15
        }
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