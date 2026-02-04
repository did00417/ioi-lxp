import pytest
import os
from utils.board_api_client import BoardApiClient
from dotenv import load_dotenv

# 환경 변수 로드 및 Fixture 정의
load_dotenv()

@pytest.fixture(scope="session")
def api():
    token = os.getenv("ELICE_TOKEN")
    if not token:
        pytest.fail(".env 파일에 ELICE_TOKEN이 설정되어 있지 않습니다!")
    return BoardApiClient(token=token)


def test_get_article_list(api):
    """STU_BOARD_01-001: 게시글 목록 조회"""

    response = api.get_article_list(board_id=9307, count=15)
    assert response.status_code == 200, f"예상치 못한 상태 코드: {response.status_code}"

    data = response.json()
    
    assert "board_articles" in data, "응답에 게시글 목록(board_articles)이 포함되어 있지 않습니다."

def test_articles_sorted_by_latest(api):
    """STU_BOARD_01-002: 게시글 최신순 정렬 조회"""
    
    response = api.get_classroom_articles(sort_by="created_desc")
    
    assert response.status_code == 200, f"예상치 못한 상태 코드: {response.status_code}"
    articles = response.json()
    
    if len(articles) >= 2:
        for i in range(len(articles) - 1):
            current_date = articles[i]['created']
            next_date = articles[i+1]['created']
            
            # 내림차순(최신순)이므로 앞의 날짜 문자열이 뒤보다 크거나 같아야 함
            assert current_date >= next_date, \
                f"정렬 오류: {i}번({current_date})보다 {i+1}번({next_date})이 더 최신입니다!"

def test_articles_sorted_by_likes(api):
    """STU_BOARD_01-003: 게시글 좋아요순 정렬 조회"""
    
    response = api.get_classroom_articles(sort_by="like_desc")
    assert response.status_code == 200, f"조회 실패: {response.status_code}"
    
    articles = response.json()

    if len(articles) >= 2:
        for i in range(len(articles) - 1):
            current_likes = articles[i]['like_count']
            next_likes = articles[i+1]['like_count']
            
            # 앞의 글 좋아요 수가 뒤의 글보다 크거나 같아야 함
            assert current_likes >= next_likes, \
                f"정렬 오류: {i}번({current_likes}개)보다 {i+1}번({next_likes}개)의 좋아요가 더 많습니다!"