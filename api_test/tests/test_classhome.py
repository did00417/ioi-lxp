import pytest
import logging
from datetime import datetime
from utils.test_helpers import (
    assert_success, assert_error,
    assert_success_and_empty_list,
    assert_success_text, assert_business_error1
)


logger = logging.getLogger(__name__)

'''
작성자: 양정은
passed: 29 ~ 30개(정상)
skipped: 0 ~1 1개(정상)
fail: 1개(정상)
'''

# 테스트 케이스: STU-CHM-01-001(유효한 토큰 사용 시 사용자 정보 조회)
def test_get_user_details(rest_client,valid_headers):
    logger.info("=== STU-CHM-01-001: 유효한 토큰 사용 시 사용자 정보 조회 ===")
    
    endpoint = "/global/account/get/"

    response = rest_client.get(
        endpoint,
        headers=valid_headers
    )

    user_data = assert_success(response)
    
    account = user_data["account"]

    assert isinstance(account["id"], int) and account["id"] > 0
    assert account["fullname"].strip()
    assert "@" in account["email"]

    logger.info("=== STU-CHM-01-001 테스트 완료 ===")

# 테스트 케이스: STU-CHM-01-002 (토큰 없이 사용자 정보 조회 시 에러 발생)
def test_get_user_not_access_token(rest_client):
    logger.info("=== STU-CHM-01-002: 토큰 없이 사용자 정보 조회 시 에러 발생 ===")
    endpoint = "/global/account/get/"

    response = rest_client.get(endpoint)
    
    assert_business_error1(response, 403, "not_found_sessionkey")
    
    logger.info("=== STU-CHM-01-002 테스트 완료 ===")
    
# 테스트 케이스: STU-CHM-01-003 (만료된 토큰 사용 시 에러 발생)
def test_get_user_invalid_token(rest_client, invalid_headers):
    logger.info("=== STU-CHM-01-003: 만료된 토큰 사용 시 에러 발생 ===")
    endpoint = "/global/account/get/"

    response = rest_client.get(
        endpoint,
        headers=invalid_headers
    )

    assert_business_error1(response, 403, "no_account_api_session")
    
    logger.info("=== STU-CHM-01-003 테스트 완료 ===")

# 테스트 케이스: STU-CHM-02-001(수강생이 이어서 해야하는 학습 내용과 정상적으로 연결이 되는지 확인)
def test_get_contiune_learning_lecture(dashboard_client, valid_headers, classroom_id):
    logger.info("=== STU-CHM-02-001: 수강생이 이어서 해야하는 학습 내용과 정상적으로 연결이 되는지 확인 ===")
    endpoint = f"/classroom/{classroom_id}/next_lecture_page"
    
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers
        )
    
    lecture_data = assert_success(response)

    assert isinstance(lecture_data.get("lecture_page_id"), int) and lecture_data["lecture_page_id"] > 0, \
        f"lecture_page_id={lecture_data.get('lecture_page_id')}"

    assert isinstance(lecture_data.get("course_title"), str) and lecture_data["course_title"].strip(), \
        f"course_title={lecture_data.get('course_title')}"
    logger.info("=== STU-CHM-02-001 테스트 완료 ===")

# 테스트 케이스: STU-CHM-02-002(필수 path 파라미터 누락시 에러 발생 확인)
def test_get_continue_learning_lecture_without_classroom_id(dashboard_client, valid_headers):
    logger.info("=== STU-CHM-02-002: 필수 path 파라미터 누락시 에러 발생 확인 ===")
    endpoint = "/next_lecture_page"
    
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers)  
    
    assert_error(response, 404, "Not Found")
    
    logger.info("=== STU-CHM-02-002 테스트 완료 ===")
    
# 테스트 케이스: STU-CHM-02-003(잘못된 classroom_id 사용 시 에러 발생 확인)  
def test_get_continue_learning_lecture_invalid_classroom_id(dashboard_client, valid_headers, classhome_params):
    logger.info("=== STU-CHM-02-003: 잘못된 classroom_id 사용 시 에러 발생 확인 ===")
    endpoint = f"/classroom/{classhome_params['invalid_classroom_id']}/next_lecture_page"
    
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers)  
    
    assert_error(response, 409, "model_not_found")
    
    logger.info("=== STU-CHM-02-003 테스트 완료 ===")
    
# 테스트 케이스: STU-CHM-03-001(수강생의 수업 일정 정보를 정상적으로 조회하는지 확인)

def test_get_class_schedule(
    classroom_client,
    valid_headers,
    classhome_params,
    classhome_schedule_common,
    classhome_schedule_cases
    ):
    logger.info("=== STU-CHM-03-001: 수강생의 수업 일정 정보를 정상적으로 조회 ===")
    endpoint = "/schedule/ics"
    
    params = { 
        "classroom_id": classhome_params["classroom_id"],
        **classhome_schedule_common,
        **classhome_schedule_cases["STU-CHM-03-001"]
    }
    response = classroom_client.get(
        endpoint, 
        headers=valid_headers, 
        params=params
        )
        
    ics_text = assert_success_text(response)

    assert ics_text.startswith("BEGIN:VCALENDAR"), "BEGIN:VCALENDAR 없음"
    assert "END:VCALENDAR" in ics_text, "END:VCALENDAR 없음"
    assert "BEGIN:VEVENT" in ics_text and "END:VEVENT" in ics_text, "VEVENT 블록 없음"
    assert f"X-ELICE-CLASSROOM-ID:{classhome_params['classroom_id']}" in ics_text, "classroom_id 없음"

    logger.info("=== STU-CHM-03-001 테스트 완료 ===")

# 테스트 케이스: STU-CHM-03-002(수강일정이 없는 날짜 조회 시 해당 날짜에 실제 일정이 없음을 확인)
def test_get_no_class_schedule(
    classroom_client,
    valid_headers,
    classhome_params,
    classhome_schedule_common,
    classhome_schedule_cases
    ):
    logger.info("=== STU-CHM-03-002: 수강일정이 없는 날짜 조회 시 해당 날짜에 실제 일정이 없음을 확인 ===")
    endpoint = "/schedule/ics"
    
    params = {
        "classroom_id": classhome_params["classroom_id"],
        **classhome_schedule_common,
        **classhome_schedule_cases["STU-CHM-03-002"]
        }
    
    response = classroom_client.get(
        endpoint, 
        headers=valid_headers, 
        params=params
    )
    
    ics_text = assert_success_text(response)
    
    assert "RRULE" in ics_text, "RRULE 없음"
    assert "DTSTART;TZID=KST:20260131" not in ics_text, "제외되어야 할 날짜 포함됨"
   
    logger.info("=== STU-CHM-03-002 테스트 완료 ===")

# 테스트 케이스: STU-CHM-03-003(유효 토큰 없이 수강일정 조회 시 에러 발생 확인)
def test_get_class_schedule_no_token(
    classroom_client,
    classhome_params,
    classhome_schedule_common,
    classhome_schedule_cases
    ):
    logger.info("=== STU-CHM-03-003: 유효 토큰 없이 수강일정 조회 시 에러 발생 확인 ===")
    endpoint = "/schedule/ics"
    
    params = {
        "classroom_id": classhome_params["classroom_id"],
        **classhome_schedule_common,
        **classhome_schedule_cases["STU-CHM-03-003"]
        }
    
    response = classroom_client.get(
        endpoint, 
        headers=None, 
        params=params
    )
    
    assert_error(response, 403, "no_access_token")
    
    logger.info("=== STU-CHM-03-003 테스트 완료 ===")
    
# 테스트 케이스: STU-CHM-03-004(날짜 파라미터 누락 시 에러 발생 확인)
def test_get_schedule_fails_when_date_parameters_missing(
    classroom_client,
    valid_headers,
    classhome_params,
    classhome_schedule_common,
    classhome_schedule_cases
    ):
    logger.info("=== STU-CHM-03-004: 날짜 파라미터 누락 시 에러 발생 확인 ===")
    endpoint = "/schedule/ics"
    
    # dt_start_ge 파라미터 누락
    params = {
        "classroom_id": classhome_params["classroom_id"],
        **classhome_schedule_common,
        **classhome_schedule_cases["STU-CHM-03-004"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    assert_error(response, 422, "missing")

    logger.info("=== STU-CHM-03-004 테스트 완료 ===")

# 테스트 케이스: STU-CHM-03-005(잘못된 날짜 포맷 입력시 에러 발생 확인)
def test_get_schedule_fails_when_date_format_invalid(
    classroom_client,
    valid_headers,
    classhome_params,
    classhome_schedule_common,
    classhome_schedule_cases
    ):
    logger.info("=== STU-CHM-03-005: 잘못된 날짜 포맷 입력시 에러 발생 확인 ===")
    endpoint = "/schedule/ics"
    
    # dt_start_ge 파라미터 잘못된 포맷
    params = {
        "classroom_id": classhome_params["classroom_id"],
        **classhome_schedule_common,
        **classhome_schedule_cases["STU-CHM-03-005"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    assert_error(response, 422, "datetime_from_date_parsing")

    logger.info("=== STU-CHM-03-005 테스트 완료 ===")
    
# 테스트 케이스: STU-CHM-04-001(수강생이 강의실의 위치를 정상 조회할 수 있는지 확인)
def test_get_lectureroom_location(
    rest_client,
    valid_headers,
    classhome_params
    ):
    logger.info("=== STU-CHM-04-001: 수강생이 강의실의 위치를 정상 조회할 수 있는지 확인 ===")
    endpoint = f"/org/qatrack/course/lectureroom/get/"
    
    params = {
        "lectureroom_id": classhome_params["lectureroom_id"]
        }
    
    response = rest_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    lectureroom_data = assert_success(response)

    lectureroom = lectureroom_data.get("lectureroom", {})

    assert isinstance(lectureroom.get("id"), int) and lectureroom["id"] > 0
    assert isinstance(lectureroom.get("title"), str) and lectureroom["title"].strip()

    logger.info("=== STU-CHM-04-001 테스트 완료 ===")
    
# 테스트 케이스 : STU-CHM-04-002(필수 파라미터 값 누락시 에러 발생 확인)
def test_get_lectureroom_location_fails_when_parameter_missing(
    rest_client,
    valid_headers
    ):
    logger.info("=== STU-CHM-04-002: 필수 파라미터 값 누락시 에러 발생 확인 ===")
    endpoint = f"/org/qatrack/course/lectureroom/get/"
    
    response = rest_client.get(
        endpoint,
        headers=valid_headers
    )
    
    assert_business_error1(response, 400, "invalid_parameter")
    
    logger.info("=== STU-CHM-04-002 테스트 완료 ===")

# 테스트 케이스 : STU-CHM-04-003(인증 토큰이 없는 경우)
def test_get_lectureroom_location_no_token(rest_client, classhome_params):
    logger.info("=== STU-CHM-04-003: 인증 토큰이 없는 경우 누락시 에러 발생 확인 ===")
    endpoint = f"/org/qatrack/course/lectureroom/get/"
    
    params = {"lectureroom_id":classhome_params["lectureroom_id"]}
    
    response = rest_client.get(endpoint, params=params)
    
    assert_business_error1(response, 403, "not_found_sessionkey")

    logger.info("=== STU-CHM-04-003 테스트 완료 ===")
    
# 테스트 케이스 : STU-CHM-04-004(강의실의 아이디가 존재하지 않을경우)
def test_get_lectureroom_location_no_lectureroom_id(
    rest_client,
    valid_headers,
    classhome_params
    ):
    logger.info("=== STU-CHM-04-004: 강의실의 아이디가 존재하지 않을경우 ===")
    endpoint = f"/org/qatrack/course/lectureroom/get/"
    
    params = {"lectureroom_id": classhome_params["invalid_lectureroom_id"]}
    
    response = rest_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    assert_business_error1(response, 400, "resource_not_found")
    
    logger.info("=== STU-CHM-04-004 테스트 완료 ===")
     
# 테스트 케이스 : STU-CHM-05-001(해당 수강생의 전체 학습 진행률 조회)
def test_get_classhome_student_overall_progress(
    dashboard_client, 
    valid_headers, 
    classhome_params
):
    logger.info("=== STU-CHM-05-001: 해당 수강생의 전체 학습 진행률 조회 ===")
    endpoint = f"/student/{classhome_params['student_id']}"
    
    params = {"classroom_id":classhome_params["classroom_id"]}
    
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers,
        params=params
    )
    
    progress_data = assert_success(response)
    
    account_id = progress_data.get("account", {}).get("id")
    assert account_id == int(classhome_params["student_id"]), f"account_id={account_id}"

    learning_progress = progress_data.get("learning_progress")
    progress_value = float(learning_progress) if learning_progress is not None else None
    assert progress_value is not None and 0.0 <= progress_value <= 100.0, \
        f"learning_progress={learning_progress}"
        
    logger.info("=== STU-CHM-05-001 테스트 완료 ===")

# 테스트 케이스 : STU-CHM-05-002(classroom_id 파라미터를 누락했을 시)
def test_get_classhome_student_overall_progress_no_params(
    dashboard_client, 
    valid_headers, 
    classhome_params
):
    logger.info("=== STU-CHM-05-002: classroom_id 파라미터를 누락했을 시 ===")
    endpoint = f"/student/{classhome_params['student_id']}"
    
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers,
    )
    assert_error(response, 422, "missing")
    
    logger.info("=== STU-CHM-05-002 테스트 완료 ===")
    
# 테스트 케이스 : STU-CHM-06-001 ~ 004(슬라이드 학습 현황 내용 확인)
@pytest.mark.parametrize("offset", [0, 5, 10, 15])
def test_get_student_course_slides(
    dashboard_client, 
    valid_headers, 
    classhome_params, 
    offset,
    classhome_student_course_case
    ):
    logger.info("=== STU-CHM-06-001 ~ 004: 슬라이드 학습 현황 내용 확인 ===")
    endpoint = f"/student/{classhome_params['student_id']}/course"
    
    params = {
        "classroom_id": classhome_params['classroom_id'],
        "offset": offset,
        **classhome_student_course_case["STU-CHM-06"]
    }
    
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params = params
    )
    
    slide_data = assert_success(response)
    
    assert isinstance(slide_data, list), "응답이 리스트가 아님"
    assert len(slide_data) > 0, "데이터가 비어 있음"

    item = slide_data[0]

    assert "course" in item, "course 없음"
    assert "title" in item["course"], "course.title 없음"
    assert "learning_progress" in item, "learning_progress 없음"
    assert "test_score" in item, "test_score 없음"
    assert "practice_score" in item, "practice_score 없음"
    
    logger.info("=== STU-CHM-06-001 ~ 004 테스트 완료 ===")
    
# 테스트 케이스 : STU-CHM-06-005(필수 파라미터 값 누락시 학습 현황 조회 차단 확인)
def test_get_student_course_slides_no_params(
    dashboard_client, 
    valid_headers, 
    classhome_params, 
    classhome_student_course_case
 ):
    logger.info("=== STU-CHM-06-005: 필수 파라미터 값 누락시 학습 현황 조회 차단 확인 ===")
    endpoint = f"/student/{classhome_params['student_id']}/course"
    
    params = {**classhome_student_course_case["STU-CHM-06-005"]}
    
    response = dashboard_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    assert_error(response, 422, "missing")
    
    logger.info("=== STU-CHM-06-005 테스트 완료 ===")
    

# 테스트 케이스 : STU-CHM-06-006(offset/count 값 오류시 학습 현황 조회 차단 확인)
def test_get_learning_status_invalid_offset_count(
    dashboard_client, 
    valid_headers, 
    classhome_params,
    classhome_student_course_case
 ):
    logger.info("=== STU-CHM-06-006: offset/count 값 오류시 학습 현황 조회 차단 확인 ===")
    endpoint = f"/student/{classhome_params['student_id']}/course"
    
    params = {
        "classroom_id":classhome_params["classroom_id"],
        **classhome_student_course_case["STU-CHM-06-006"]
    }
    
    response = dashboard_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    assert_error(response, 422, "greater_than_equal")
    
    logger.info("=== STU-CHM-06-006 테스트 완료 ===")
    
# 테스트 케이스 : STU-CHM-06-007(path 파라미터에 타인의 student_id 입력시 학습 현황 조회 차단 확인)
def test_get_learning_status_unauthorized_user(
    dashboard_client, 
    valid_headers, 
    classhome_params,
    classhome_student_course_case
 ):
    logger.info("=== STU-CHM-06-007: path 파라미터에 타인의 student_id 입력시 학습 현황 조회 차단 확인 ===")
    endpoint = f"/student/{classhome_params['other_student_id']}/course"
    
    params = {
        "classroom_id":classhome_params["classroom_id"],
        **classhome_student_course_case["STU_CHM-06-007"]
    }
    
    response = dashboard_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    status = response.status_code

    if status == 200:
        body = response.json()
        logger.error(f"IDOR 취약점 발생 | status=200 | body={body}")
        pytest.fail(f"IDOR 취약점: 타인 데이터 노출됨 {body}")

    assert status in [403, 404], \
        f"보안 오류: 접근이 차단되지 않음 (status={status}, body={response.text})"

    logger.info("=== STU-CHM-06-007 테스트 완료 ===")

# 테스트 케이스 : STU-CHM-07-001(최신 게시판 공지 정상 조회)    
def test_get_latest_board_articles(
    classroom_client,
    valid_headers,
    classhome_params,
    classhome_board_case
    ):
    
    logger.info("=== STU-CHM-07-001: 최신 게시판 공지 정상 조회 ===")
    endpoint = f"/classroom/{classhome_params['classroom_id']}/article"
    
    params = {
       **classhome_board_case["STU-CHM-07-001"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
        
    board_data = assert_success(response)[0]

    assert isinstance(board_data.get("title"), str) and board_data["title"].strip(), \
        f"title={board_data.get('title')}"
    assert isinstance(board_data.get("content"), str) and board_data["content"].strip(), \
        f"content={board_data.get('content')}"
    
    logger.info("=== STU-CHM-07-001 테스트 완료 ===")

# 테스트 케이스 : STU-CHM-07-002(필수 파라미터 누락시 조회 차단)    
def test_get_board_articles_no_classroom_id(
    classroom_client,
    valid_headers,
    classhome_params,
    classhome_board_case
    ):
    
    logger.info("=== STU-CHM-07-002: 필수 파라미터 누락시 게시판 조회 차단 ===")
    endpoint = f"/classroom/{classhome_params['classroom_id']}/article"
    
    params = {
        **classhome_board_case["STU-CHM-07-002"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    assert_error(response, 422, "missing")
    
    logger.info("=== STU-CHM-07-002 테스트 완료 ===")

# 테스트 케이스 : STU-CHM-07-003(skip/conut 값 오류시 조회 차단)
def test_get_board_articles_with_invalid_skip_count(
    classroom_client,
    valid_headers,
    classhome_params,
    classhome_board_case
):
    logger.info("=== STU-CHM-07-003: skip/conut 값 오류시 게시판 조회 차단 확인 ===")
    endpoint = f"/classroom/{classhome_params['classroom_id']}/article"
    
    params = {
        **classhome_board_case["STU-CHM-07-003"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers = valid_headers,
        params = params
    )
    assert_error(response, 422, "greater_than_equal")

    logger.info("=== STU-CHM-07-003 테스트 완료 ===")

# 테스트 케이스 : STU-CHM-08-001(수강생들의 감정상태 조회 확인)    
def test_get_emotion(
    classroom_client,
    valid_headers,
    classhome_params,
    classhome_emotion_case):
    
    logger.info("=== STU-CHM-08-001: 수강생의 감정 상태 조회 확인 ===")
    endpoint = f"/emotion"
    
    params = {
       "classroom_id":classhome_params["classroom_id"],
       **classhome_emotion_case["STU-CHM-08-001"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    emotion_data = assert_success(response)
    
    assert isinstance(emotion_data, list), "응답이 리스트가 아님"
    emotion_item = emotion_data[0]
    assert isinstance(emotion_item.get("emoji"), str), f"emoji={emotion_item.get('emoji')}"

    logger.info("=== STU-CHM-08-001 테스트 완료 ===")
    
# 테스트 케이스 : STU-CHM-08-002("수강생 감정상태 설정 확인")
def test_post_emotion(
    classroom_client,
    valid_headers,
    classhome_params): 
    logger.info("=== STU-CHM-08-002: 수강생 감정상태 설정 확인 ===")
    
    endpoint = f"/emotion"
    today = datetime.now().strftime("%Y-%m-%d")
    
    params ={
        "classroom_id":classhome_params["classroom_id"],
       "filter_record_date": today
    }
    
    # Body 추가 (Postman에서 사용한 값)
    payload = {
        "classroom_id": classhome_params["classroom_id"],
        "emoji": "bad"
    }
    
    response = classroom_client.post(
        endpoint,
        headers=valid_headers,
        params=params,
        json_body = payload
    )
    
    # 하루 1회 제한 대응
    if response.status_code in [400, 409]:
        pytest.skip("오늘 이미 감정 상태가 설정되어 있어 테스트 스킵")

    assert_success(response)

    logger.info("=== STU-CHM-08-002 테스트 완료 ===")
    
# 테스트 케이스 : STU-CHM-08-003("수강생들이 감정상태를 선택하지 않았을 경우 응답 바디가 빈 값으로 출력되는지 확인")    
def test_get_emotion_empty_list(
    classroom_client,
    valid_headers,
    classhome_params,
    classhome_emotion_case):
    
    logger.info("=== STU-CHM-08-003: 감정 상태 미 설정시 응답 body가 빈 값인지 확인 ===")
    endpoint = f"/emotion"
    
    params = {
       "classroom_id":classhome_params["classroom_id"],
       **classhome_emotion_case["STU-CHM-08-002~3"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    assert_success_and_empty_list(response)
    
    logger.info("=== STU-CHM-08-003 테스트 완료 ===")
    
# 테스트 케이스 : STU-CHM-08-004("보유한 토큰이 없거나 로그아웃 상태일시 감정 조회 차단")    
def test_get_emotion_no_token(
    classroom_client,
    classhome_params,
    classhome_emotion_case):
    
    logger.info("=== STU-CHM-08-004: 보유한 토큰이 없을 시 감정 조회 차단 ===")
    endpoint = f"/emotion"
    
    params = {
       "classroom_id":classhome_params["classroom_id"],
       **classhome_emotion_case["STU-CHM-08-002~3"]
    }
    
    response = classroom_client.get(
        endpoint,
        params=params
    )
    assert_error(response, 403, "no_access_token")

    logger.info("=== STU-CHM-08-004 테스트 완료 ===")
