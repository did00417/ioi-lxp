import pytest
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# 테스트 케이스: STU-CHM-01-001(유효한 토큰 사용 시 사용자 정보 조회)
def test_get_user_details(rest_client,valid_headers):
    logger.info("=== STU-CHM-01-001: 유효한 토큰 사용 시 사용자 정보 조회 ===")
    
    endpoint = "/global/account/get/"

    response = rest_client.get(
        endpoint,
        headers=valid_headers
    )

    assert response.status_code == 200, f"status = {response.status_code}"

    user_data = response.json()
    account = user_data["account"]

    try:
        assert isinstance(account.get("id"), int) and account["id"] > 0, f"id={account.get('id')}"
        assert isinstance(account.get("fullname"), str) and account["fullname"].strip(), f"fullname={account.get('fullname')}"
        assert "@" in account.get("email", ""), f"email={account.get('email')}"
    except AssertionError as e:
        logger.error(f"Account 검증 실패 | {e} | response={account}")
        raise

    logger.info("=== STU-CHM-01-001 테스트 완료 ===")

# 테스트 케이스: STU-CHM-01-002 (토큰 없이 사용자 정보 조회 시 에러 발생)
def test_get_user_not_access_token(rest_client):
    logger.info("=== STU-CHM-01-002: 토큰 없이 사용자 정보 조회 시 에러 발생 ===")
    endpoint = "/global/account/get/"

    response = rest_client.get(
        endpoint,
    )

    error_data = response.json()
    
    try:
        result = error_data.get("_result", {})
        assert result.get("status_code") == 403, f"status={result.get('status_code')}"
        assert error_data.get("fail_code") == "not_found_sessionkey", f"fail_code={error_data.get('fail_code')}"
        assert error_data.get("fail_message") == "authorization failed", f"fail_message={error_data.get('fail_message')}"
    except AssertionError as e:
        logger.error(f"403 인증 검증 실패 | {e} | response={error_data}")
        raise
    
    logger.info("=== STU-CHM-01-002 테스트 완료 ===")
    
# 테스트 케이스: STU-CHM-01-003 (만료된 토큰 사용 시 에러 발생)
def test_get_user_invalid_token(rest_client, invalid_headers):
    logger.info("=== STU-CHM-01-003: 만료된 토큰 사용 시 에러 발생 ===")
    endpoint = "/global/account/get/"

    response = rest_client.get(
        endpoint,
        headers=invalid_headers
    )

    error_data = response.json()

    try:
        result = error_data.get("_result", {})
        assert result.get("status_code") == 403, f"status={result.get('status_code')}"
        assert error_data.get("fail_code") == "no_account_api_session", f"fail_code={error_data.get('fail_code')}"
        assert error_data.get("fail_message") == "authorization failed", f"fail_message={error_data.get('fail_message')}"
    except AssertionError as e:
        logger.error(f"403 인증 검증 실패 | {e} | response={error_data}")
        raise
    
    logger.info("=== STU-CHM-01-003 테스트 완료 ===")

# 테스트 케이스: STU-CHM-02-001(수강생이 이어서 해야하는 학습 내용과 정상적으로 연결이 되는지 확인)
def test_get_contiune_learning_lecture(dashboard_client, valid_headers, classroom_id):
    logger.info("=== STU-CHM-02-001: 수강생이 이어서 해야하는 학습 내용과 정상적으로 연결이 되는지 확인 ===")
    endpoint = f"/classroom/{classroom_id}/next_lecture_page"
    
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers
        )
    
    lecture_data = response.json()

    try:
        assert response.status_code == 200, f"status={response.status_code}"
        assert isinstance(lecture_data.get("lecture_page_id"), int) and lecture_data["lecture_page_id"] > 0, \
            f"lecture_page_id={lecture_data.get('lecture_page_id')}"
        assert isinstance(lecture_data.get("course_title"), str) and lecture_data["course_title"].strip(), \
            f"course_title={lecture_data.get('course_title')}"
    except AssertionError as e:
        logger.error(f"Lecture 응답 검증 실패 | {e} | response={lecture_data}")
        raise
    logger.info("=== STU-CHM-02-001 테스트 완료 ===")

# 테스트 케이스: STU-CHM-02-002(필수 path 파라미터 누락시 에러 발생 확인)
def test_get_continue_learning_lecture_without_classroom_id(dashboard_client, valid_headers):
    logger.info("=== STU-CHM-02-002: 필수 path 파라미터 누락시 에러 발생 확인 ===")
    endpoint = "/next_lecture_page"
    
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers)  
    
    assert response.status_code == 404, f"status={response.status_code}"

    error_data = response.json()
    try:
        assert error_data.get("detail") == "Not Found", f"detail={error_data.get('detail')}"
    except AssertionError as e:
        logger.error(f"404 응답 검증 실패 | {e} | response={error_data}")
        raise
    
    logger.info("=== STU-CHM-02-002 테스트 완료 ===")
    
# 테스트 케이스: STU-CHM-02-003(잘못된 classroom_id 사용 시 에러 발생 확인)  
def test_get_continue_learning_lecture_invalid_classroom_id(dashboard_client, valid_headers, classhome_params):
    logger.info("=== STU-CHM-02-003: 잘못된 classroom_id 사용 시 에러 발생 확인 ===")
    endpoint = f"/classroom/{classhome_params['invalid_classroom_id']}/next_lecture_page"
    
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers)  
    
    assert response.status_code == 409, f"status={response.status_code}"

    error_data = response.json()

    try:
        assert error_data.get("code") == "model_not_found", f"code={error_data.get('code')}"
        assert error_data.get("message") == \
            "Failed to find target model.Check specific information in detail.", \
            f"message={error_data.get('message')}"

        classroom_detail = error_data.get("detail", {}).get("Classroom", [])
        assert "id" in classroom_detail, f"Classroom={classroom_detail}"

    except AssertionError as e:
        logger.error(f"409 응답 검증 실패 | {e} | response={error_data}")
        raise
    
    logger.info("=== STU-CHM-02-003 테스트 완료 ===")
    
# 테스트 케이스: STU-CHM-03-001(수강생의 수업 일정 정보를 정상적으로 조회하는지 확인)

def test_get_class_schedule(
    classroom_client,
    valid_headers,
    classhome_params,
    schedule_common,
    schedule_cases
    ):
    logger.info("=== STU-CHM-03-001: 수강생의 수업 일정 정보를 정상적으로 조회 ===")
    endpoint = "/schedule/ics"
    
    params = { 
        "classroom_id": classhome_params["classroom_id"],
        **schedule_common,
        **schedule_cases["STU-CHM-03-001"]
    }
    response = classroom_client.get(
        endpoint, 
        headers=valid_headers, 
        params=params
        )
        
    assert response.status_code == 200, f"status={response.status_code}"

    ics_text = response.text

    try:
        assert ics_text.startswith("BEGIN:VCALENDAR"), "BEGIN:VCALENDAR 없음"
        assert "END:VCALENDAR" in ics_text, "END:VCALENDAR 없음"
        assert "BEGIN:VEVENT" in ics_text and "END:VEVENT" in ics_text, "VEVENT 블록 없음"
        assert f"X-ELICE-CLASSROOM-ID:{classhome_params['classroom_id']}" in ics_text, "classroom_id 없음"
    except AssertionError as e:
        logger.error(f"iCalendar 응답 검증 실패 | {e} | body={ics_text[:500]}")
        raise
    
    logger.info("=== STU-CHM-03-001 테스트 완료 ===")

# 테스트 케이스: STU-CHM-03-002(수강일정이 없는 날짜 조회 시 해당 날짜에 실제 일정이 없음을 확인)
def test_get_no_class_schedule(
    classroom_client,
    valid_headers,
    classhome_params,
    schedule_common,
    schedule_cases
    ):
    logger.info("=== STU-CHM-03-002: 수강일정이 없는 날짜 조회 시 해당 날짜에 실제 일정이 없음을 확인 ===")
    endpoint = "/schedule/ics"
    
    params = {
        "classroom_id": classhome_params["classroom_id"],
        **schedule_common,
        **schedule_cases["STU-CHM-03-002"]
        }
    
    response = classroom_client.get(
        endpoint, 
        headers=valid_headers, 
        params=params
    )
    
    try:
        assert response.status_code == 200, f"status={response.status_code}"
        ics_text = response.text
        assert "RRULE" in ics_text, "RRULE 없음"
        assert "DTSTART;TZID=KST:20260131" not in ics_text, "제외되어야 할 날짜 포함됨"
    except AssertionError as e:
        logger.error(f"ICS 검증 실패 | {e} | body={ics_text[:500]}")
        raise
        
    logger.info("=== STU-CHM-03-002 테스트 완료 ===")

# 테스트 케이스: STU-CHM-03-003(유효 토큰 없이 수강일정 조회 시 에러 발생 확인)
def test_get_class_schedule_no_token(
    classroom_client,
    classhome_params,
    schedule_common,
    schedule_cases
    ):
    logger.info("=== STU-CHM-03-003: 유효 토큰 없이 수강일정 조회 시 에러 발생 확인 ===")
    endpoint = "/schedule/ics"
    
    params = {
        "classroom_id": classhome_params["classroom_id"],
        **schedule_common,
        **schedule_cases["STU-CHM-03-003"]
        }
    
    response = classroom_client.get(
        endpoint, 
        headers=None, 
        params=params
    )
    
    assert response.status_code == 403, f"status={response.status_code}"

    error_data = response.json()
    try:
        assert error_data.get("code") == "no_access_token", f"code={error_data.get('code')}"
    except AssertionError as e:
        logger.error(f"403 인증 검증 실패 | {e} | response={error_data}")
        raise
    
    logger.info("=== STU-CHM-03-003 테스트 완료 ===")
    
# 테스트 케이스: STU-CHM-03-004(날짜 파라미터 누락 시 에러 발생 확인)
def test_get_schedule_fails_when_date_parameters_missing(
    classroom_client,
    valid_headers,
    classhome_params,
    schedule_common,
    schedule_cases
    ):
    logger.info("=== STU-CHM-03-004: 날짜 파라미터 누락 시 에러 발생 확인 ===")
    endpoint = "/schedule/ics"
    
    # dt_start_ge 파라미터 누락
    params = {
        "classroom_id": classhome_params["classroom_id"],
        **schedule_common,
        **schedule_cases["STU-CHM-03-004"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    assert response.status_code == 422, f"status={response.status_code}"

    error_data = response.json()

    try:
        detail = error_data.get("detail", [])
        assert len(detail) >= 2, f"detail_len={len(detail)}"

        assert detail[0].get("type") == "missing", f"type0={detail[0].get('type')}"
        assert detail[0].get("loc") == ["query", "dt_start_ge"], f"loc0={detail[0].get('loc')}"

        assert detail[1].get("msg") == "Field required", f"msg1={detail[1].get('msg')}"
        assert detail[1].get("loc") == ["query", "dt_start_le"], f"loc1={detail[1].get('loc')}"

    except AssertionError as e:
        logger.error(f"422 파라미터 검증 실패 | {e} | response={error_data}")
        raise
    logger.info("=== STU-CHM-03-004 테스트 완료 ===")

# 테스트 케이스: STU-CHM-03-005(잘못된 날짜 포맷 입력시 에러 발생 확인)
def test_get_schedule_fails_when_date_format_invalid(
    classroom_client,
    valid_headers,
    classhome_params,
    schedule_common,
    schedule_cases
    ):
    logger.info("=== STU-CHM-03-005: 잘못된 날짜 포맷 입력시 에러 발생 확인 ===")
    endpoint = "/schedule/ics"
    
    # dt_start_ge 파라미터 잘못된 포맷
    params = {
        "classroom_id": classhome_params["classroom_id"],
        **schedule_common,
        **schedule_cases["STU-CHM-03-005"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    assert response.status_code == 422, f"status={response.status_code}"
    
    error_data = response.json()
    try:
        detail = error_data.get("detail", [])
        assert detail[0].get("type") == "datetime_from_date_parsing", f"type0={detail[0].get('type')}"
        assert detail[0].get("loc") == ["query", "dt_start_ge"], f"loc0={detail[0].get('loc')}"

        assert detail[1].get("type") == "datetime_from_date_parsing", f"type1={detail[1].get('type')}"
        assert detail[1].get("loc") == ["query", "dt_start_le"], f"loc1={detail[1].get('loc')}"

    except AssertionError as e:
        logger.error(f"422 날짜 형식 검증 실패 | {e} | response={error_data}")
        raise
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
    
    assert response.status_code == 200
    lectureroom_data = response.json()

    try:
        lectureroom = lectureroom_data.get("lectureroom", {})
        
        assert isinstance(lectureroom.get("id"), int) and lectureroom["id"] > 0, \
            f"id={lectureroom.get('id')}"
        
        assert isinstance(lectureroom.get("title"), str) and lectureroom["title"].strip(), \
            f"title={lectureroom.get('title')}"

    except AssertionError as e:
        logger.error(f"lectureroom 검증 실패 | {e} | response={lectureroom_data}")
        raise
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
    
    error_data = response.json()
    try:
        result = error_data.get("_result", {})
        assert result.get("status_code") == 400, f"status_code={result.get('status_code')}"
        assert result.get("status") == "fail", f"status={result.get('status')}"

        invalid_params = error_data.get("fail_detail", {}).get("invalid_params", {})
        assert invalid_params.get("lectureroom_id") == "required", \
            f"lectureroom_id={invalid_params.get('lectureroom_id')}"

    except AssertionError as e:
        logger.error(f"400 파라미터 검증 실패 | {e} | response={error_data}")
        raise
    logger.info("=== STU-CHM-04-002 테스트 완료 ===")

# 테스트 케이스 : STU-CHM-04-003(인증 토큰이 없는 경우)
def test_get_lectureroom_location_no_token(rest_client, classhome_params):
    logger.info("=== STU-CHM-04-003: 인증 토큰이 없는 경우 누락시 에러 발생 확인 ===")
    endpoint = f"/org/qatrack/course/lectureroom/get/"
    
    params = {"lectureroom_id":classhome_params["lectureroom_id"]}
    
    response = rest_client.get(endpoint, params=params)
    
    error_data = response.json()

    try:
        result = error_data.get("_result", {})
        assert result.get("status_code") == 403, f"status_code={result.get('status_code')}"
        assert result.get("status") == "fail", f"status={result.get('status')}"
        assert error_data.get("fail_code") == "not_found_sessionkey", \
            f"fail_code={error_data.get('fail_code')}"
    except AssertionError as e:
        logger.error(f"403 인증 검증 실패 | {e} | response={error_data}")
        raise
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
    
    error_data = response.json()
    try:
        result = error_data.get("_result", {})
        assert result.get("status_code") == 400, f"status_code={result.get('status_code')}"
        assert result.get("status") == "fail", f"status={result.get('status')}"
        assert error_data.get("fail_code") == "resource_not_found", \
            f"fail_code={error_data.get('fail_code')}"
        
        resource_type = error_data.get("fail_detail", {}).get("resource_type")
        assert resource_type == "lectureroom_model", f"resource_type={resource_type}"
    except AssertionError as e:
        logger.error(f"400 리소스 없음 검증 실패 | {e} | response={error_data}")
        raise
    
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
    
    progress_data = response.json()
    
    try:
        assert response.status_code == 200, f"status={response.status_code}"

        account_id = progress_data.get("account", {}).get("id")
        assert account_id == int(classhome_params["student_id"]), f"account_id={account_id}"

        learning_progress = progress_data.get("learning_progress")
        progress_value = float(learning_progress) if learning_progress is not None else None
        assert progress_value is not None and 0.0 <= progress_value <= 100.0, \
            f"learning_progress={learning_progress}"

    except AssertionError as e:
        logger.error(f"progress 검증 실패 | {e} | response={progress_data}")
        raise
    
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
    
    error_data = response.json()
    
    try:
        assert response.status_code == 422, f"status={response.status_code}"

        detail = error_data.get("detail", [])
        assert detail, "detail empty"

        assert detail[0].get("type") == "missing", f"type={detail[0].get('type')}"
        assert detail[0].get("loc") == ["query", "classroom_id"], f"loc={detail[0].get('loc')}"

    except AssertionError as e:
        logger.error(f"422 classroom_id 누락 검증 실패 | {e} | response={error_data}")
        raise
    
    logger.info("=== STU-CHM-05-002 테스트 완료 ===")
    
# 테스트 케이스 : STU-CHM-06-001 ~ 004(슬라이드 학습 현황 내용 확인)
@pytest.mark.parametrize("offset", [0, 5, 10, 15])
def test_get_student_course_slides(
    dashboard_client, 
    valid_headers, 
    classhome_params, 
    offset,
    student_course_case
    ):
    logger.info("=== STU-CHM-06-001 ~ 004: 슬라이드 학습 현황 내용 확인 ===")
    endpoint = f"/student/{classhome_params['student_id']}/course"
    
    params = {
        "classroom_id": classhome_params['classroom_id'],
        "offset": offset,
        **student_course_case["STU-CHM-06"]
    }
    
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params = params
    )
    
    assert response.status_code == 200, f"status={response.status_code}"
    
    slide_data = response.json()
    
    try:
        assert response.status_code == 200, f"status={response.status_code}"
        assert isinstance(slide_data, list), "응답이 리스트가 아님"
        assert len(slide_data) > 0, "데이터가 비어 있음"

        item = slide_data[0]

        assert "course" in item, "course 없음"
        assert "title" in item["course"], "course.title 없음"
        assert "learning_progress" in item, "learning_progress 없음"
        assert "test_score" in item, "test_score 없음"
        assert "practice_score" in item, "practice_score 없음"

    except AssertionError as e:
        logger.error(f"학습 목록 검증 실패 | {e} | sample={slide_data[:1]}")
        raise
    
    logger.info("=== STU-CHM-06-001 ~ 004 테스트 완료 ===")
    
# 테스트 케이스 : STU-CHM-06-005(필수 파라미터 값 누락시 학습 현황 조회 차단 확인)
def test_get_student_course_slides_no_params(
    dashboard_client, 
    valid_headers, 
    classhome_params, 
    student_course_case
 ):
    logger.info("=== STU-CHM-06-005: 필수 파라미터 값 누락시 학습 현황 조회 차단 확인 ===")
    endpoint = endpoint = f"/student/{classhome_params['student_id']}/course"
    
    params = {**student_course_case["STU-CHM-06-005"]}
    
    response = dashboard_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    error_data = response.json()
    
    try:
        assert response.status_code == 422, f"status={response.status_code}"

        detail = error_data.get("detail", [])
        assert detail, "detail 없음"

        assert detail[0].get("type") == "missing", f"type={detail[0].get('type')}"
        assert detail[0].get("loc") == ["query", "classroom_id"], f"loc={detail[0].get('loc')}"

    except AssertionError as e:
        logger.error(f"classroom_id 누락 검증 실패 | {e} | response={error_data}")
        raise
    
    logger.info("=== STU-CHM-06-005 테스트 완료 ===")
    

# 테스트 케이스 : STU-CHM-06-006(offset/count 값 오류시 학습 현황 조회 차단 확인)
def test_get_learning_status_invalid_offset_count(
    dashboard_client, 
    valid_headers, 
    classhome_params,
    student_course_case
 ):
    logger.info("=== STU-CHM-06-006: offset/count 값 오류시 학습 현황 조회 차단 확인 ===")
    endpoint = endpoint = f"/student/{classhome_params['student_id']}/course"
    
    params = {
        "classroom_id":classhome_params["classroom_id"],
        **student_course_case["STU-CHM-06-006"]
    }
    
    response = dashboard_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    error_data = response.json()
    
    try:
        assert response.status_code == 422, f"status={response.status_code}"

        detail = error_data.get("detail", [])
        assert detail[0].get("type") == "greater_than_equal", f"type0={detail[0].get('type')}"
        assert detail[0].get("loc") == ["query", "offset"], f"loc0={detail[0].get('loc')}"

        assert detail[1].get("type") == "greater_than_equal", f"type1={detail[1].get('type')}"
        assert detail[1].get("loc") == ["query", "count"], f"loc1={detail[1].get('loc')}"

    except AssertionError as e:
        logger.error(f"offset/count 범위 검증 실패 | {e} | response={error_data}")
        raise
    
    logger.info("=== STU-CHM-06-006 테스트 완료 ===")

# 테스트 케이스 : STU-CHM-07-001(최신 게시판 공지 정상 조회)    
def test_get_latest_board_articles(
    classroom_client,
    valid_headers,
    classhome_params,
    board_case
    ):
    
    logger.info("=== STU-CHM-07-001: 최신 게시판 공지 정상 조회 ===")
    endpoint = f"/classroom/{classhome_params['classroom_id']}/article"
    
    params = {
       **board_case["STU-CHM-07-001"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    try:
        assert response.status_code == 200, f"status={response.status_code}"
        
        board_data = response.json()[0]
        assert isinstance(board_data.get("title"), str) and board_data["title"].strip(), \
            f"title={board_data.get('title')}"
        assert isinstance(board_data.get("content"), str) and board_data["content"].strip(), \
            f"content={board_data.get('content')}"

    except AssertionError as e:
        logger.error(f"게시판 조회 검증 실패 | {e} | response={board_data}")
        raise
    
    logger.info("=== STU-CHM-07-001 테스트 완료 ===")

# 테스트 케이스 : STU-CHM-07-002(필수 파라미터 누락시 조회 차단)    
def test_get_board_articles_no_classroom_id(
    classroom_client,
    valid_headers,
    classhome_params,
    board_case
    ):
    
    logger.info("=== STU-CHM-07-002: 필수 파라미터 누락시 게시판 조회 차단 ===")
    endpoint = f"/classroom/{classhome_params['classroom_id']}/article"
    
    params = {
        **board_case["STU-CHM-07-002"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    error_data = response.json()
    
    try:
        assert response.status_code == 422, f"status={response.status_code}"

        detail = error_data.get("detail", [])
        assert detail, "detail empty"

        assert detail[0].get("type") == "missing", f"type0={detail[0].get('type')}"
        assert detail[0].get("loc") == ["query", "skip"], f"loc0={detail[0].get('loc')}"
        assert detail[1].get("type") == "missing", f"type1={detail[1].get('type')}"
        assert detail[1].get("loc") == ["query", "count"], f"loc1={detail[1].get('loc')}"
        
    except AssertionError as e:
        logger.error(f"422 skip/count 누락 검증 실패 | {e} | response={error_data}")
        raise
    
    logger.info("=== STU-CHM-07-002 테스트 완료 ===")

# 테스트 케이스 : STU-CHM-07-003(skip/conut 값 오류시 조회 차단)
def test_get_board_articles_with_invalid_skip_count(
    classroom_client,
    valid_headers,
    classhome_params,
    board_case
):
    logger.info("=== STU-CHM-07-003: skip/conut 값 오류시 게시판 조회 차단 확인 ===")
    endpoint = f"/classroom/{classhome_params['classroom_id']}/article"
    
    params = {
        **board_case["STU-CHM-07-003"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers = valid_headers,
        params = params
    )
    
    error_data = response.json()

    try:
        assert response.status_code == 422, f"status={response.status_code}"

        detail = error_data.get("detail", [])

        assert detail[0].get("type") == "greater_than_equal", f"type0={detail[0].get('type')}"
        assert detail[0].get("loc") == ["query", "skip"], f"loc0={detail[0].get('loc')}"

        assert detail[1].get("type") == "greater_than_equal", f"type1={detail[1].get('type')}"
        assert detail[1].get("loc") == ["query", "count"], f"loc1={detail[1].get('loc')}"

    except AssertionError as e:
        logger.error(f"상태 코드 422 검증 실패 | {e} | response={error_data}")
        raise

    logger.info("=== STU-CHM-07-003 테스트 완료 ===")

# 테스트 케이스 : STU-CHM-08-001(수강생들의 감정상태 조회 확인)    
def test_get_emotion(
    classroom_client,
    valid_headers,
    classhome_params,
    emotion_case):
    
    logger.info("=== STU-CHM-08-001: 수강생의 감정 상태 조회 확인 ===")
    endpoint = f"/emotion"
    
    params = {
       "classroom_id":classhome_params["classroom_id"],
       **emotion_case["STU-CHM-08-001"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )

    emotion_data = response.json()
    
    try:
        assert response.status_code == 200, f"status={response.status_code}"
        assert isinstance(emotion_data, list), "응답이 리스트가 아님"
        emotion_item = emotion_data[0]
        assert isinstance(emotion_item.get("emoji"), str), f"emoji={emotion_item.get('emoji')}"
    except AssertionError as e: 
        logger.error(f"감정 상태 조회 검증 실패 | {e} | response={emotion_data}") 
        raise

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
        payload = payload
    )
    
    # 하루 1회 제한 대응 (이미 설정된 경우)
    if response.status_code in [400, 409]:
        pytest.skip("오늘 이미 감정 상태가 설정되어 있어 테스트 스킵")

    assert response.status_code == 200

    logger.info("=== STU-CHM-08-002 테스트 완료 ===")
    
# 테스트 케이스 : STU-CHM-08-003("수강생들이 감정상태를 선택하지 않았을 경우 응답 바디가 빈 값으로 출력되는지 확인")    
def test_get_emotion_empty_list(
    classroom_client,
    valid_headers,
    classhome_params,
    emotion_case):
    
    logger.info("=== STU-CHM-08-003: 감정 상태 미 설정시 응답 body가 빈 값인지 확인 ===")
    endpoint = f"/emotion"
    
    params = {
       "classroom_id":classhome_params["classroom_id"],
       **emotion_case["STU-CHM-08-002~3"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )

    emotion_data = response.json()
    
    try:
        assert response.status_code == 200, f"status={response.status_code}"
        assert emotion_data == []
        
    except AssertionError as e: 
        logger.error(f"응답이 빈 리스트가 아님 | {e} | response={emotion_data}") 
        raise

    logger.info("=== STU-CHM-08-003 테스트 완료 ===")
    
    # 테스트 케이스 : STU-CHM-08-004("보유한 토큰이 없거나 로그아웃 상태일시 감정 조회 차단")    
def test_get_emotion_no_token(
    classroom_client,
    classhome_params,
    emotion_case):
    
    logger.info("=== STU-CHM-08-004: 보유한 토큰이 없을 시 감정 조회 차단 ===")
    endpoint = f"/emotion"
    
    params = {
       "classroom_id":classhome_params["classroom_id"],
       **emotion_case["STU-CHM-08-002~3"]
    }
    
    response = classroom_client.get(
        endpoint,
        params=params
    )

    error_data = response.json()
    
    assert response.status_code == 403, f"status={response.status_code}"

    error_data = response.json()
    try:
        assert error_data.get("code") == "no_access_token", f"code={error_data.get('code')}"
    except AssertionError as e:
        logger.error(f"403 인증 검증 실패 | {e} | response={error_data}")
        raise

    logger.info("=== STU-CHM-08-004 테스트 완료 ===")
