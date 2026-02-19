import pytest

from utils.config_loader import get_service_url, get_header, load_test_data
from api.api_client import APIClient
import logging

logger = logging.getLogger(__name__)

#--------------- 각 url 받아서 클라이언트 생성하기 ----------------

@pytest.fixture(scope="session")
def dashboard_client():
    return APIClient(get_service_url("dashboard"))

@pytest.fixture(scope="session")
def classroom_client():
    return APIClient(get_service_url("classroom"))

@pytest.fixture(scope="session")
def rest_client():
    return APIClient(get_service_url("rest"))

@pytest.fixture(scope="session")
def course_client():
    return APIClient(get_service_url("course"))

#------------------ <공용> 헤더 받아서 사용 --------------------------

@pytest.fixture(scope="session")
def header_data():
    return get_header()

@pytest.fixture(scope="session")
def valid_headers(header_data):
    return header_data["headers"]

@pytest.fixture(scope="session")
def invalid_headers(header_data):
    return header_data["invalid_headers"]

@pytest.fixture(scope="session")
def hyojin_headers(header_data):
    return header_data["hyojin_headers"]

#------------------ <공용> logger 설정 --------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_api_client():
    logger.info("=== 전체 API 테스트 세션 시작 ===")
    yield
    logger.info("=== 전체 API 테스트 세션 종료 ===")

#--------------------- 각자 사용할 테스트 데이터 받기 ------------------------

@pytest.fixture(scope="session")
def test_board_data():
    return load_test_data("board")

@pytest.fixture(scope="session")
def test_dashboard_data():
    return load_test_data("dashboard")

@pytest.fixture(scope="session")
def test_classhome_data():
    return load_test_data("classhome")

@pytest.fixture(scope="session")
def test_subject_data():
    return load_test_data("subject")

#-------------- <수진> 학습 대시보드 메뉴 데이터 -----------------------

@pytest.fixture(scope="session")
def dashboard_params(test_dashboard_data):
    return test_dashboard_data["params"]

@pytest.fixture(scope="session")
def dashboard_page(test_dashboard_data):
    return test_dashboard_data["page"]

#-------------------- <유진> 게시판 메뉴 데이터 ------------------------------

@pytest.fixture(scope="session")
def board_id(test_board_data):
    return test_board_data["params"]["board_id"]

@pytest.fixture(scope="session")
def classroom_id(test_board_data):
    return test_board_data["params"]["classroom_id"]

@pytest.fixture(scope="session")
def create_article_data(test_board_data):
    return test_board_data["articles"]["create_article"]

@pytest.fixture
def created_article_id(rest_client, valid_headers, classroom_id, create_article_data):
    """
    테스트용 게시글을 생성하고 board_article_id를 반환하고 삭제하는 공용 픽스처
    """
    # [Setup] 게시글 생성
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    create_payload = {**create_article_data, "classroom_id": classroom_id}
    
    response = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        form_data=create_payload
    )
    
    article_id = response.json().get("board_article_id")
    logger.info(f"[Fixture] 테스트용 임시 게시글 생성 완료 (ID: {article_id})")
    
    yield article_id 

    # [Teardown] 
    logger.info(f"[Teardown] 테스트 종료 후 임시 게시글 삭제 시작 (ID: {article_id})")
    delete_res = rest_client.post(
        endpoint="/org/qatrack/board/article/delete/",
        headers=headers,
        form_data={"board_article_id": article_id}
    )
    
    # 이미 삭제 테스트(009)에서 지웠다면 응답이 'ok'가 아닐 수 있으므로 로그만 남김
    if delete_res.json().get("_result", {}).get("status") == "ok":
        logger.info(f"[Teardown] ID {article_id} 자동 삭제 완료")
    else:
        logger.info(f"[Teardown] ID {article_id}는 이미 삭제되었거나 삭제할 수 없는 상태입니다.")

@pytest.fixture
def created_comment_id(rest_client, valid_headers, created_article_id):
    # [Setup] 방금 생성된 article_id를 받아서 댓글 작성
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)
    payload = {"board_article_id": created_article_id, "content": "테스트 댓글"}
    res = rest_client.post(endpoint="/org/qatrack/board/article/comment/edit/", headers=headers, form_data=payload)
    comment_id = res.json().get("article_comment_id")
    
    yield comment_id
    
    # [Teardown] 테스트 끝나면 댓글 먼저 삭제
    logger.info(f"[Teardown] 테스트 종료 후 임시 댓글 삭제 시작 (ID: {comment_id})")
    res = rest_client.post(
        endpoint="/org/qatrack/board/article/comment/delete/", 
        headers=headers, 
        form_data={"article_comment_id": comment_id}
    )
    if res.json().get("_result", {}).get("status") == "ok":
        logger.info(f"[Teardown] 댓글 ID {comment_id} 자동 삭제 완료")

#-------------------- <정은> 클래스 홈 사용 데이터 ------------------------------

@pytest.fixture(scope="session")
def classhome_params(test_classhome_data):
    return test_classhome_data["params"]

@pytest.fixture(scope="session")
def classhome_schedule_common(test_classhome_data):
    return test_classhome_data["schedule_common_data"]

@pytest.fixture(scope="session")
def classhome_schedule_cases(test_classhome_data):
    return test_classhome_data["schedule_cases_data"]

@pytest.fixture(scope="session")
def classhome_student_course_case(test_classhome_data):
    return test_classhome_data["student_course_data"]

@pytest.fixture(scope="session")
def classhome_board_case(test_classhome_data):
    return test_classhome_data["classhome_board_data"]

@pytest.fixture(scope="session")
def classhome_emotion_case(test_classhome_data):
    return test_classhome_data["emotion_date_data"]

#-------------------- <효진> 학습 과목 데이터 ------------------------------

@pytest.fixture(scope="session")
def subject_params(test_subject_data):
    return test_subject_data["params"]

#-------------------- <동빈> 수업 일정 데이터 ------------------------------

@pytest.fixture(scope="session")
def test_schedule_data():
    return load_test_data("schedule")

@pytest.fixture(scope="session")
def schedule_params(test_schedule_data):
    return test_schedule_data["params"]

@pytest.fixture(scope="session")
def weekly_case(test_schedule_data):
    return test_schedule_data["cases"]["weekly"]

@pytest.fixture(scope="session")
def schedule_cases(test_schedule_data):
    return test_schedule_data["cases"]