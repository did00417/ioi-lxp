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