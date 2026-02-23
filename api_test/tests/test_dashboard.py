import pytest
import logging
from utils.test_helpers import (
    assert_success, assert_error, assert_id_match, 
    assert_progress_exists, assert_title_contains, assert_valid_course_ids,
    assert_success_and_empty_list
)

logger = logging.getLogger(__name__)

#------------------ 테스트 시나리오 STU-DAB-01 : 학습 대시보드 메뉴의 전체 과목 학습 현황과 관련된 API 테스트 ------------------------------------
def test_all_courses_learning_page_success(dashboard_client, valid_headers, dashboard_params):
    logger.info("=== STU-DAB-01-001: 전체 과목 학습 현황 페이지 정상 조회 ===")
    
    endpoint = f"/student/{dashboard_params['student_id']}"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={"classroom_id": dashboard_params["classroom_id"]}
    )
    
    body = assert_success(response)
    assert_id_match(body["account"]["id"], dashboard_params["student_id"], "account id")
    assert_progress_exists(body["learning_progress"])
    logger.info("=== STU-DAB-01-001 테스트 완료 ===")

@pytest.mark.parametrize("test_id, desc, offset, page_key", [
    ("STU-DAB-01-002", "1 페이지", 0, "one_course_ids"),
    ("STU-DAB-01-003", "2 페이지", 5, "two_course_ids")
])
def test_all_courses_pagination(dashboard_client, valid_headers, dashboard_params, dashboard_page, test_id, desc, offset, page_key):
    logger.info(f"=== {test_id}: {desc} 과목 리스트 조회 ===")
    
    endpoint = f"/student/{dashboard_params['student_id']}/course"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
        "classroom_id": dashboard_params["classroom_id"], 
        "offset": offset, 
        "count": 5
    })
    
    body = assert_success(response)
    assert_valid_course_ids(body, set(dashboard_page[page_key]))
    logger.info(f"=== {test_id} 테스트 완료 ===")

def test_all_courses_page_with_invalid_token(dashboard_client, invalid_headers, dashboard_params):
    logger.info("=== STU-DAB-01-004: 만료된 토큰으로 전체 과목 학습 현황 조회 ===")
    
    endpoint = f"/student/{dashboard_params['student_id']}"
    response = dashboard_client.get(
        endpoint, 
        headers=invalid_headers, 
        params={"classroom_id": dashboard_params["classroom_id"]}
    )
    
    assert_error(response, 403, "permission")
    logger.info("=== STU-DAB-01-004 테스트 완료 ===")

# [Parametrize 통합] 005, 006: 409 에러(model)를 반환하는 전체 과목 학습 현황 예외 케이스 통합
@pytest.mark.parametrize("test_id, desc, student_key, classroom_key", [
    ("STU-DAB-01-005", "소속되지 않은 클래스의 전체 과목 학습 현황 조회", "student_id", "invalid_classroom_id"),
    ("STU-DAB-01-006", "유효하지 않은 student id로 전체 과목 학습 현황 조회", "invalid_student_id", "classroom_id")
])
def test_all_courses_page_with_invalid_parameters(dashboard_client, valid_headers, dashboard_params, test_id, desc, student_key, classroom_key):
    logger.info(f"=== {test_id}: {desc} ===")

    endpoint = f"/student/{dashboard_params[student_key]}"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={"classroom_id": dashboard_params[classroom_key]}
    )
    
    assert_error(response, 409, "model")
    logger.info(f"=== {test_id} 테스트 완료 ===")

def test_all_courses_delete_with_student_account(classroom_client, valid_headers, dashboard_params):
    logger.info("=== STU-DAB-01-007: 학생 권한으로 전체 과목 학습 현황 삭제 ===")
    endpoint = f"/classroom/{dashboard_params['classroom_id']}"
    response = classroom_client.delete(
        endpoint, 
        headers=valid_headers
    )
    
    assert_error(response, 403, "permission")
    logger.info("=== STU-DAB-01-007 테스트 완료 ===")
    
#-------------------- 테스트 시나리오 STU-DAB-02 : 학습 대시보드 메뉴의 과목별 학습 현황과 관련된 API 테스트 ------------------------------------
def test_course_learning_page_success(dashboard_client, valid_headers, dashboard_params, dashboard_scenarios):
    logger.info("=== STU-DAB-02-001: 과목 선택 후 학습 현황 페이지 정상 조회 ===")
    
    endpoint = f"/student/{dashboard_params['student_id']}/lecture" 
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
        "classroom_id": dashboard_params["classroom_id"], 
        "course_id": dashboard_params["course_id"], 
        **dashboard_scenarios["course_learning_base"]
    })
    
    body = assert_success(response)
    assert_id_match(body[0]["lecture"]["course_id"], dashboard_params["course_id"], "course id")
    assert_progress_exists(body[0]["learning_progress"])
    logger.info("=== STU-DAB-02-001 테스트 완료 ===")

def test_course_page_with_invalid_token(dashboard_client, invalid_headers, dashboard_params, dashboard_scenarios):
    logger.info("=== STU-DAB-02-002: 만료된 토큰으로 한 과목의 학습 현황 조회 ===")
    
    endpoint = f"/student/{dashboard_params['student_id']}/lecture"
    response = dashboard_client.get(
        endpoint, 
        headers=invalid_headers, 
        params={
        "classroom_id": dashboard_params["classroom_id"], 
        "course_id": dashboard_params["course_id"], 
        **dashboard_scenarios["course_learning_base"]
    })
    
    assert_error(response, 403, "permission")
    logger.info("=== STU-DAB-02-002 테스트 완료 ===")

# [Parametrize 통합] 003, 004, 005: 409 에러(model)를 반환하는 과목별 학습 현황 예외 케이스 통합
@pytest.mark.parametrize("test_id, desc, student_key, classroom_key, course_key", [
    ("STU-DAB-02-003", "소속되지 않은 클래스 홈으로 한 과목의 학습 현황 조회", "student_id", "invalid_classroom_id", "course_id"),
    ("STU-DAB-02-004", "유효하지 않은 student id로 한 과목의 학습 현황 조회", "invalid_student_id", "classroom_id", "course_id"),
    ("STU-DAB-02-005", "소속된 클래스 홈과 맞지 않는 과목의 학습 현황 조회", "student_id", "classroom_id", "invalid_course_id")
])
def test_course_page_with_invalid_parameters(dashboard_client, valid_headers, dashboard_params, test_id, desc, student_key, classroom_key, course_key):
    logger.info(f"=== {test_id}: {desc} ===")

    endpoint = f"/student/{dashboard_params[student_key]}"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
            "classroom_id": dashboard_params[classroom_key], 
            "course_id": dashboard_params[course_key]
        }
    )
    
    assert_error(response, 409, "model")
    logger.info(f"=== {test_id} 테스트 완료 ===")

def test_course_page_delete_with_student_account(classroom_client, valid_headers, dashboard_params):
    logger.info("=== STU-DAB-02-006: 학생 권한으로 한 과목 학습 현황 삭제 ===")
    endpoint = f"/classroom/{dashboard_params['classroom_id']}/course/{dashboard_params['course_id']}"
    response = classroom_client.delete(
        endpoint, 
        headers=valid_headers
    )
    assert_error(response, 403, "permission")
    logger.info("=== STU-DAB-02-006 테스트 완료 ===")
    
#------------------- 테스트 시나리오 STU-DAB-03 : 학습 대시보드 메뉴의 수업별 학습 현황과 관련된 API 테스트 ------------------------------------
def test_lecture_learning_page_success(dashboard_client, valid_headers, dashboard_params):
    logger.info("=== STU-DAB-03-001: 수업 선택 후 학습 현황 페이지 정상 조회 ===")
    
    endpoint = f"/lecture/{dashboard_params['lecture_id']}"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
        "classroom_id": dashboard_params["classroom_id"], 
        "course_id": dashboard_params["course_id"], 
        "elice_course_id": dashboard_params["course_id"]
    })
    
    body = assert_success(response)
    assert_id_match(body["lecture"]["id"], dashboard_params["lecture_id"], "lecture id")
    assert len(body["lecture"]["title"]) > 0, "STEP 실패 : 수업 title 데이터 존재하지 않음"
    logger.info("STEP 성공 : 수업 title 데이터 정상 존재")
    assert_progress_exists(body["learning_progress"])
    logger.info("=== STU-DAB-03-001 테스트 완료 ===")
    
def test_lecture_page_with_invalid_token(dashboard_client, invalid_headers, dashboard_params):
    logger.info("=== STU-DAB-03-002: 만료된 토큰으로 수업 현황 페이지 조회 ===")
    
    endpoint = f"/lecture/{dashboard_params['lecture_id']}"
    response = dashboard_client.get(
        endpoint, 
        headers=invalid_headers, 
        params={
        "classroom_id": dashboard_params["classroom_id"], 
        "course_id": dashboard_params["course_id"], 
        "elice_course_id": dashboard_params["course_id"]
    })
    
    assert_error(response, 403, "permission")
    logger.info("=== STU-DAB-03-002 테스트 완료 ===")
    
# [Parametrize 통합] 003, 004, 005: 409 에러(model)를 반환하는 수업 현황 예외 케이스 통합
@pytest.mark.parametrize("test_id, desc, student_key, classroom_key, lecture_key", [
    ("STU-DAB-03-003", "소속되지 않은 클래스의 수업 현황 페이지 조회", "student_id", "invalid_classroom_id", "lecture_id"),
    ("STU-DAB-03-004", "유효하지 않은 student id로 수업 현황 페이지 조회", "invalid_student_id", "classroom_id", "lecture_id"),
    ("STU-DAB-03-005", "과목과 매칭되지 않는 수업 현황 페이지 조회", "student_id", "classroom_id", "invalid_lecture_id")
])
def test_lecture_page_with_invalid_parameters(dashboard_client, valid_headers, dashboard_params, test_id, desc, student_key, classroom_key, lecture_key):
    logger.info(f"=== {test_id}: {desc} ===")
    
    endpoint = f"/student/{dashboard_params[student_key]}"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
            "classroom_id": dashboard_params[classroom_key], 
            "course_id": dashboard_params["course_id"], # course_id는 3개 다 정상값 사용
            "lecture_id": dashboard_params[lecture_key]
        }
    )
    
    assert_error(response, 409, "model")
    logger.info(f"=== {test_id} 테스트 완료 ===")
  
# [단독 유지] 006: 파라미터 누락(Missing) 케이스는 구조가 다르므로 분리  
def test_lecture_page_with_no_course_id(dashboard_client, valid_headers, dashboard_params):
    logger.info("=== STU-DAB-03-006: 수업 현황 페이지 조회 시 필수 파라미터인 course_id 누락 ===")
    
    endpoint = f"/student/{dashboard_params['student_id']}"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
        "classroom_id": dashboard_params["invalid_classroom_id"], 
        "lecture_id": dashboard_params["lecture_id"]
    })
    
    assert_error(response, 409, "model")
    logger.info("=== STU-DAB-03-006 테스트 완료 ===")
    
#-------------------- 테스트 시나리오 STU-DAB-04 : 학습 대시보드 메뉴의 챕터 테스트 현황과 관련된 API 테스트 ------------------------------------
def test_chapter_test_page_success(dashboard_client, valid_headers, dashboard_params):
    logger.info("=== STU-DAB-04-001: 챕터 테스트 선택 후 학습 현황 페이지 정상 조회 ===")
    
    endpoint = f"/lecture/{dashboard_params['chapter_test_id']}"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
        "classroom_id": dashboard_params["classroom_id"], 
        "course_id": dashboard_params["course_id"], 
        "elice_course_id": dashboard_params["course_id"]
    })
    
    body = assert_success(response)
    assert_id_match(body["lecture"]["id"], dashboard_params["chapter_test_id"], "챕터 테스트 lecture id")
    assert_title_contains(body["lecture"]["title"], "챕터 테스트")
    assert_progress_exists(body["learning_progress"])
    logger.info("=== STU-DAB-04-001 테스트 완료 ===")
    
def test_chapter_test_page_with_invalid_token(dashboard_client, invalid_headers, dashboard_params):
    logger.info("=== STU-DAB-04-002: 만료된 토큰으로 챕터 테스트 학습 현황 조회 ===")
    
    endpoint = f"/lecture/{dashboard_params['chapter_test_id']}"
    response = dashboard_client.get(
        endpoint, 
        headers=invalid_headers, 
        params={
        "classroom_id": dashboard_params["classroom_id"], 
        "course_id": dashboard_params["course_id"], 
        "elice_course_id": dashboard_params["course_id"]
    })
    
    assert_error(response, 403, "permission")
    logger.info("=== STU-DAB-04-002 테스트 완료 ===")
    
# [Parametrize 통합] 003, 004, 005: 409 에러(model)를 반환하는 챕터 테스트 예외 케이스 통합
@pytest.mark.parametrize("test_id, desc, student_key, classroom_key, lecture_key", [
    ("STU-DAB-04-003", "소속되지 않은 클래스의 챕터 테스트 학습 현황 조회", "student_id", "invalid_classroom_id", "chapter_test_id"),
    ("STU-DAB-04-004", "유효하지 않은 student id로 챕터 테스트 학습 현황 조회", "invalid_student_id", "classroom_id", "chapter_test_id"),
    ("STU-DAB-04-005", "과목과 매칭되지 않는 챕터 테스트 학습 현황 조회", "student_id", "classroom_id", "invalid_chapter_test_id")
])
def test_chapter_test_page_with_invalid_parameters(dashboard_client, valid_headers, dashboard_params, test_id, desc, student_key, classroom_key, lecture_key):
    logger.info(f"=== {test_id}: {desc} ===")
    
    endpoint = f"/student/{dashboard_params[student_key]}"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
            "classroom_id": dashboard_params[classroom_key], 
            "course_id": dashboard_params["course_id"], # course_id는 3개 다 정상값 사용
            "lecture_id": dashboard_params[lecture_key]
        }
    )
    
    assert_error(response, 409, "model")
    logger.info(f"=== {test_id} 테스트 완료 ===")
    
def test_chapter_test_page_with_no_classroom_id(dashboard_client, valid_headers, dashboard_params):
    logger.info("=== STU-DAB-04-006: 필수 파라미터 classroom_id 누락 ===")
    
    endpoint = f"/student/{dashboard_params['student_id']}"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
        "course_id": dashboard_params["course_id"], 
        "lecture_id": dashboard_params["chapter_test_id"]
    })
    
    assert_error(response, 422, "missing")
    assert "classroom_id" in str(response.json()["detail"]), "STEP 실패 : 누락된 파라미터 field id가 제공되지 않음"
    logger.info("STEP 성공 : 누락된 파라미터 field id가 제공됨")
    logger.info("=== STU-DAB-04-006 테스트 완료 ===")
    
#-------------------- 테스트 시나리오 STU-DAB-05 : 학습 대시보드 메뉴의 복습 테스트 현황과 관련된 API 테스트 ------------------------------------
def test_review_test_page_success(dashboard_client, valid_headers, dashboard_params):
    logger.info("=== STU-DAB-05-001: 복습 테스트 정상 조회 ===")
    
    endpoint = f"/lecture/{dashboard_params['review_test_id']}"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
        "classroom_id": dashboard_params["classroom_id"], 
        "course_id": dashboard_params["course_id"], 
        "elice_course_id": dashboard_params["course_id"]
    })
    
    body = assert_success(response)
    assert_id_match(body["lecture"]["id"], dashboard_params["review_test_id"], "복습 테스트 lecture id")
    assert_title_contains(body["lecture"]["title"], "복습 테스트")
    assert_progress_exists(body["learning_progress"])
    logger.info("=== STU-DAB-05-001 테스트 완료 ===")
    
def test_review_test_page_with_invalid_token(dashboard_client, invalid_headers, dashboard_params):
    logger.info("=== STU-DAB-05-002: 만료된 토큰으로 복습 테스트 학습 현황 조회 ===")
    
    endpoint = f"/lecture/{dashboard_params['review_test_id']}"
    response = dashboard_client.get(
        endpoint, 
        headers=invalid_headers, 
        params={
        "classroom_id": dashboard_params["classroom_id"], 
        "course_id": dashboard_params["course_id"], 
        "elice_course_id": dashboard_params["course_id"]
    })
    
    assert_error(response, 403, "permission")
    logger.info("=== STU-DAB-05-002 테스트 완료 ===")
    
# [Parametrize 통합] 003, 004, 005: 409 에러(model)를 반환하는 예외 케이스 통합
@pytest.mark.parametrize("test_id, desc, student_key, classroom_key, lecture_key", [
    ("STU-DAB-05-003", "소속되지 않은 클래스의 복습 테스트 학습 현황 조회", "student_id", "invalid_classroom_id", "review_test_id"),
    ("STU-DAB-05-004", "유효하지 않은 student id로 복습 테스트 학습 현황 조회", "invalid_student_id", "classroom_id", "review_test_id"),
    ("STU-DAB-05-005", "과목과 매칭되지 않는 복습 테스트 학습 현황 조회", "student_id", "classroom_id", "invalid_review_test_id")
])
def test_review_test_page_with_invalid_parameters(dashboard_client, valid_headers, dashboard_params, test_id, desc, student_key, classroom_key, lecture_key):
    logger.info(f"=== {test_id}: {desc} ===")
    
    endpoint = f"/student/{dashboard_params[student_key]}"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
            "classroom_id": dashboard_params[classroom_key], 
            "course_id": dashboard_params["course_id"], # course_id는 3개 다 정상값 사용
            "lecture_id": dashboard_params[lecture_key]
        }
    )
    
    assert_error(response, 409, "model")
    logger.info(f"=== {test_id} 테스트 완료 ===")
    
#-------------------- 테스트 시나리오 STU-DAB-06 : 학습 대시보드 메뉴의 오답 노트 현황과 관련된 API 테스트 ------------------------------------
def test_review_note_page_when_exist_test(dashboard_client, valid_headers, dashboard_params, dashboard_scenarios) :
    '''
    챕터 테스트 or 복습 테스트가 존재하는 과목의 오답 노트 관련 API 조회 시 
    응답 바디에 해당 테스트의 각 문제 페이지 id와 채점된 점수가 포함됨
    '''
    logger.info("=== STU-DAB-06-001: 테스트 lecture가 존재할 때 오답 노트 정상 조회 ===")
    endpoint = f"/student/{dashboard_params['student_id']}/lecture"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
        "classroom_id": dashboard_params["classroom_id"], 
        "course_id": dashboard_params["course_id"], 
        **dashboard_scenarios["review_note_base"]
    })
    
    body = assert_success(response)
    assert_id_match(body[0]["lecture"]["course_id"], dashboard_params["course_id"], "과목 ID")
    assert_id_match(body[0]["lecture"]["id"], dashboard_params["chapter_test_id"], "챕터 테스트 ID")
    assert body[0]["page_score"][0]["id"], "Step 실패 : 챕터 테스트 문제 페이지 id 제공되지 않음"
    logger.info("Step 성공 : 챕터 테스트 문제 페이지 id 제공됨")
    assert body[0]["page_score"][0]["score"] is not None, "Step 실패 : 채점 결과 데이터 제공되지 않음"
    logger.info("Step 성공 : 채점 결과 데이터 제공됨")
    logger.info("=== STU-DAB-06-001 테스트 완료 ===")
    
# [Parametrize 통합] 002, 004, 005, 006: 모두 "200 ok, 빈 배열(Empty List)"을 반환하는 동일 패턴
@pytest.mark.parametrize("test_id, desc, student_key, classroom_key, course_key", [
    ("STU-DAB-06-002", "테스트 lecture가 존재하지 않는 과목의 오답 노트 조회", "student_id", "classroom_id", "no_test_course_id"),
    ("STU-DAB-06-004", "소속되지 않은 클래스의 오답 노트 조회", "student_id", "invalid_classroom_id", "course_id"),
    ("STU-DAB-06-005", "유효하지 않은 student id로 오답 노트 조회", "invalid_student_id", "classroom_id", "course_id"),
    ("STU-DAB-06-006", "클래스룸과 매칭되지 않는 course id로 조회", "student_id", "classroom_id", "invalid_course_id")
])
def test_review_note_page_empty_list_cases(dashboard_client, valid_headers, dashboard_params, dashboard_scenarios, test_id, desc, student_key, classroom_key, course_key):
    logger.info(f"=== {test_id}: {desc} (빈 배열 검증) ===")
    
    endpoint = f"/student/{dashboard_params[student_key]}/lecture"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
            "classroom_id": dashboard_params[classroom_key], 
            "course_id": dashboard_params[course_key], 
            **dashboard_scenarios["review_note_base"]
        }
    )
    
    assert_success_and_empty_list(response)
    logger.info(f"=== {test_id} 테스트 완료 ===")
    
def test_review_note_page_with_invalid_token(dashboard_client, invalid_headers, dashboard_params, dashboard_scenarios):
    logger.info("=== STU-DAB-06-003: 유효하지 않은 토큰으로 오답 노트 페이지 조회 ===")
    
    endpoint = f"/student/{dashboard_params['student_id']}/lecture"
    response = dashboard_client.get(
        endpoint, 
        headers=invalid_headers, 
        params={
        "classroom_id": dashboard_params["classroom_id"], 
        "course_id": dashboard_params["course_id"], 
        **dashboard_scenarios["review_note_base"]
    })
    
    assert_error(response, 403, "permission")
    logger.info("=== STU-DAB-06-003 테스트 완료 ===")
    
def test_review_note_page_with_weird_parameter(dashboard_client, valid_headers, dashboard_params):
    logger.info("=== STU-DAB-06-007: 적절하지 않은 파라미터 값으로 오답 노트 조회 ===")
    
    endpoint = f"/student/{dashboard_params['student_id']}/lecture"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
        "classroom_id": dashboard_params["classroom_id"], 
        "course_id": dashboard_params["course_id"], 
        "filter_test_admission_status": "incompleted", 
        "offset": 0, 
        "count": 40
    })
    
    assert_error(response, 422, "Input should be")
    logger.info("=== STU-DAB-06-007 테스트 완료 ===")
    
def test_review_note_page_without_parameter(dashboard_client, valid_headers, dashboard_params):
    logger.info("=== STU-DAB-06-008: 필수 파라미터인 offset 누락 시 오답 노트 조회 ===")
    
    endpoint = f"/student/{dashboard_params['student_id']}/lecture"
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers, 
        params={
        "classroom_id": dashboard_params["classroom_id"], 
        "course_id": dashboard_params["course_id"], 
        "filter_test_admission_status": "completed", 
        "count": 40
    })
    
    assert_error(response, 422, "missing")
    assert "offset" in str(response.json()["detail"]), "Step 실패 : 누락된 파라미터 field id가 제공되지 않음"
    logger.info("Step 성공 : 누락된 파라미터 field id가 제공됨")
    logger.info("=== STU-DAB-06-008 테스트 완료 ===")