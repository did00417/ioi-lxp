import logging
import pytest
from utils.config_loader import load_test_data
from utils.test_helpers import assert_status_code, assert_response_match, assert_business_code, assert_business_status, assert_equal_value

logger = logging.getLogger(__name__)

def test_fetch_sbj_list(classroom_client, valid_headers, subject_params):
    test_id = "STU-SBJ-01-001"
    classroom_id = subject_params['classroom_id']
    count = 10
    endpoint = f"/classroom/{classroom_id}/course"

    logger.info(f"=== {test_id} 시작 ===")

    response = classroom_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={
            "skip": 0,
            "count": count
        }
    )
    data = response.json()
    assert_status_code(response.status_code, 200, 1)
    response_count = len(data)

    assert response_count <= count, f"Step 2 실패: 응답 데이터 갯수({response_count})가 요청한 count({count})보다 많음."
    logger.info(f"Step 2 성공: 응답 데이터 갯수({response_count})가 요청한 count({count})보다 작거나 같음.")

    logger.info(f"=== {test_id} 테스트 완료 ===")

@pytest.mark.parametrize("case", load_test_data("subject")["sbj_list_failure_cases"])
def test_fetch_sbj_list_failure_cases(classroom_client, valid_headers, subject_params, case):
    test_id, classroom_id_key, query_params, exp_status, exp_content = case["test_id"], case["classroom_id_key"], case["query_params"], case["expected_status"], case["expected_content"]

    classroom_id = subject_params[classroom_id_key]
    endpoint = f"/classroom/{classroom_id}/course"
    logger.info(f"=== {test_id} 시작 ===")

    response = classroom_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params=query_params
    )
    data = response.json()
    assert_status_code(response.status_code, exp_status, 1)

    target_key = exp_content["key"]
    expected_val = exp_content["value"]

    if target_key == "detail":
        # 422 에러
        detail = data.get("detail", [])
        actual_val = detail[0].get("msg") if isinstance(detail, list) and detail else data.get("detail")
    else:
        # 일반 에러 코드 처리
        actual_val = data.get(target_key, "")

    assert_response_match(actual_val, expected_val, 2)

    logger.info(f"=== {test_id} 테스트 완료 ===")

@pytest.mark.parametrize("case", load_test_data("subject")["sbj_detail_cases"])
def test_fetch_sbj_detail(classroom_client, valid_headers, subject_params, case):
    test_id, cls_id, crs_id, exp_status = case["test_id"], subject_params[case["classroom_id_key"]], subject_params[case["course_id_key"]], case["expected_status"]

    endpoint = f"/classroom/{cls_id}/course/{crs_id}"
    logger.info(f"=== {test_id} 시작 ===")

    response = classroom_client.get(
        endpoint=endpoint,
        headers=valid_headers
    )
    data = response.json()
    assert_status_code(response.status_code, exp_status, 1)

    exp_info = case.get("expected_content")
    if exp_info:
        target_key = exp_info["key"]
        
        if "value_from_params" in exp_info:
            expected_val = subject_params[exp_info["value_from_params"]]
        else:
            expected_val = exp_info["value"]

        actual_val = data.get(target_key)
        assert_response_match(actual_val, expected_val, 2)

    if exp_status == 409:
        assert "ClassroomCourse" in data.get("detail", {}), "실패 상세 정보(ClassroomCourse)가 누락됨"
        logger.info("Step 3 성공: 에러 상세 모델명 확인 완료.")

    logger.info(f"=== {test_id} 테스트 완료 ===")

@pytest.mark.parametrize("case", load_test_data("subject")["sbj_map_cases"])
def test_fetch_sbj_map_integrated(dashboard_client, valid_headers, subject_params, case):
    test_id, student_id = case["test_id"], subject_params[case["student_id_key"]]
    endpoint = f"/student/{student_id}/lecture"

    actual_params = {}
    for k, v in case["query_params"].items():
        actual_params[k] = subject_params.get(v, v) if isinstance(v, str) else v

    logger.info(f"=== {test_id} 시작 ===")

    response = dashboard_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params=actual_params
    )
    
    data = response.json()

    assert_status_code(response.status_code, case["expected_status"], 1)

    if case["validate_type"] == "content_check":
        # 정상 조회 시: 데이터 구조 및 제목 확인
        first_item = data[0] if isinstance(data, list) and len(data) > 0 else {}
        actual_title = first_item.get('lecture', {}).get('title')
        
        assert actual_title is not None and len(actual_title) > 0, "제목이 비어있음"
        logger.info(f"Step 2 성공: 학습 맵 제목 확인 완료 ({actual_title})")

    elif case["validate_type"] == "error_check":
        # 에러 발생 시: 에러 메시지 확인
        error_msg = data.get("detail", [{}])[0].get("msg")
        assert error_msg == case["expected_msg"], f"에러 메시지 불일치: {error_msg}"
        logger.info(f"Step 2 성공: 예상된 에러 메시지 확인 완료 ({error_msg})")

    logger.info(f"=== {test_id} 테스트 완료 ===")

@pytest.mark.parametrize("case", load_test_data("subject")["child_lectures_cases"])
def test_fetch_child_lecture_integrated(rest_client, hyojin_headers, subject_params, case):
    test_id, course_id, user_id = case["test_id"], subject_params[case["course_id_key"]], str(subject_params[case["user_id_key"]])
    endpoint = "/org/qatrack/dashboard/user/lecture_page/list/"
    
    logger.info(f"=== {test_id} 시작 ===")

    response = rest_client.get(
        endpoint=endpoint,
        headers=hyojin_headers,
        params={"course_id": course_id, "user_id": user_id}
    )
    
    data = response.json()
    assert_status_code(response.status_code, case["expected_http_status"], 1)

    if case["validate_type"] == "success":
        data_user_id = str(data.get("user", {}).get("id"))
        lectures = data.get("lectures", [])
        
        assert_equal_value(data_user_id, user_id, "User ID", 2)
        assert len(lectures) > 0, "Lectures 데이터가 비어 있음"
        
        first_lecture = lectures[0]
        assert "lecture_pages" in first_lecture and len(first_lecture["lecture_pages"]) > 0, "상세 페이지 구조 누락"
        logger.info(f"Step 3: 성공 데이터 구조 확인 완료 (강의명: {first_lecture.get('title')})")

    elif case["validate_type"] == "fail":
        result = data.get("_result", {})
        exp_res = case["expected_result"]
        
        assert_business_status(result, exp_res["status"], 2)
        assert_business_code(result, exp_res, 3)

    logger.info(f"=== {test_id} 완료 ===")

@pytest.mark.parametrize("case", load_test_data("subject")["lecture_cases"])
def test_fetch_material_unified(rest_client, valid_headers, subject_params, case):
    """통합 강의 콘텐츠(퀴즈/과제/실습) 조회 테스트"""
    test_id, endpoint, param_key, id_key, expected_status_code, expected_result = case["test_id"], case["endpoint"], case["param_key"], case["id_key"], case["expected_status_code"], case["expected_result"]

    logger.info(f"=== {test_id} 시작 ===")
    
    request_id = subject_params[id_key]
    
    response = rest_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={param_key: request_id}
    )
    
    data = response.json()
    result = data.get("_result", {})
    actual_status_code = result.get('status_code')

    assert_status_code(response.status_code, 200, 1)
    assert_status_code(actual_status_code, expected_status_code, 2)

    if expected_status_code == 200:
        # 응답 key가 'material_quiz', 'material_assignment' 식으로 들어오므로 이를 동적으로 파싱
        resource_key = endpoint.split('/')[-3]
        result_data = data.get(resource_key, {})
        result_id = result_data.get('id')
        
        assert request_id == result_id
        logger.info(f"Step 3 성공: 요청 ID와 응답 ID({result_id}) 일치 확인.")
    else:
        assert_business_status(result, expected_result, 3)
    
    logger.info(f"=== {test_id} 테스트 완료 ===")

@pytest.mark.parametrize("case", load_test_data("subject")["adjacent_lecture_data"])
def test_fetch_adjacent_lecture(course_client, valid_headers, subject_params, case):
    test_id, lecture_key, direction, offset, is_null = case["test_id"], case["lecture_key"], case["direction"], int(case["offset"]), case.get("is_null", False)

    course_key = f"course_id_test_{direction}"

    base_lecture_id = subject_params[lecture_key]
    course_id = subject_params[course_key]

    endpoint = f"/lecture/{base_lecture_id}/{direction}"

    logger.info(f"=== {test_id} 시작 ===")

    response = course_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={
            "elice_course_id": course_id
        }
    )
    data = response.json()
    status_code = response.status_code

    assert_status_code(status_code, 200, 1)

    if is_null:
        assert data is None, f"Step 2 실패: 결과가 null이어야 합니다."
        logger.info(f"Step 2 성공: 기대한 대로 null 반환됨")
    else:
        result_course_id = data.get("course_id")
        result_id = data.get("id")
        expected_id = base_lecture_id + offset

        assert result_id == expected_id, f"Step 2 실패: 기대값({expected_id}) != 결과값({result_id})"
        logger.info(f"Step 2 성공: Lecture ID 일치 ({result_id})")

        assert result_course_id == course_id, f"Step 3 실패: 기대값({course_id}) != 결과값({result_course_id})"
        logger.info(f"Step 3 성공: Course ID 일치 ({result_course_id})")

    logger.info(f"=== {test_id} 테스트 완료 ===")

@pytest.mark.parametrize("case", load_test_data("subject")["lecture_details_data"])
def test_fetch_lectures(course_client, valid_headers ,subject_params, case):
    test_id = case["test_id"]
    course_id = subject_params[case["course_id_key"]]
    endpoint = f"/lecture_page"
    
    logger.info(f"=== {test_id} 시작 ===")
    
    actual_params = {}
    for k, v in case["query_params"].items():
        actual_params[k] = subject_params.get(v, v) if v in subject_params else v

    response = course_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params=actual_params
    )
    data = response.json()
    status_code = response.status_code

    assert_status_code(status_code, case["expected_status"], 1)

    if case["validate_type"] == "success":
        assert isinstance(data, list) and len(data) > 0, "응답 데이터가 비어있거나 리스트가 아님"

        first_lecture = data[0].get("lecture", {})
        actual_title = first_lecture.get("title")
        
        assert actual_title is not None, "강의 제목(title)을 찾을 수 없음"
        logger.info(f"Step 2 성공: 강의 제목 확인 완료 ({actual_title})")

    elif case["validate_type"] == "error":
        detail = data.get("detail", {})
        actual_msg = detail.get("msg")
        actual_loc = detail.get("loc", [])
        actual_message_text = data.get("message", "")

        assert_equal_value(actual_msg.lower(), case["expected_msg"].lower(), "상세 메시지", 2)
        exp_loc = case["expected_loc"]
        assert exp_loc in actual_loc, f"에러 위치(loc) 불일치: 기대값 '{exp_loc}'가 {actual_loc}에 없음"
        assert exp_loc in actual_message_text, f"전체 메시지에 '{exp_loc}' 정보가 누락됨"
        logger.info(f"Step 3 성공: {exp_loc} 누락에 대한 422 에러 및 상세 정보 확인 완료")

    logger.info(f"=== {test_id} 테스트 완료 ===")

def test_quiz_request_success(rest_client, hyojin_headers, subject_params):
    endpoint = "/org/qatrack/material_quiz/response/add/"
    headers = hyojin_headers.copy()
    if "Content-Type" in headers:
        del headers["Content-Type"]

    logger.info(f"=== STU-SBJ-10-001 시작 ===")
    response = rest_client.post(
        endpoint=endpoint,
        headers=headers,
        form_data={
            "material_quiz_id": subject_params["material_quiz_id"],
            "answer": str(subject_params["answer"])
        }
    )
    data = response.json()

    assert_status_code(response.status_code, 200, 1)

    assert "quiz_response_id" in data, f"Step 2 실패: 응답 값에 quiz_response_id가 포함되지 않음."
    logger.info(f"Step 2 성공: 응답 값에 quiz_response_id가({data.get('quiz_response_id')}) 포함됨.")
    logger.info("=== STU-SBJ-10-001 테스트 완료 ===")

@pytest.mark.parametrize("case", load_test_data("subject")["quiz_missing_params_data"])
def test_quiz_request_fail_missing_params(rest_client, valid_headers, case):
    endpoint = "/org/qatrack/material_quiz/response/add/"
    headers = valid_headers.copy()
    if "Content-Type" in headers:
        del headers["Content-Type"]

    test_id, missing_data, expected_fields = case["test_id"], case["missing_data"], case["expected_missing_field"]

    logger.info(f"=== {test_id} 시작 ===")
    response = rest_client.post(
        endpoint=endpoint,
        headers=headers,
        form_data=missing_data
    )
    data = response.json()
    result = data.get("_result", {})
    status_code = result.get("status_code")
    assert_status_code(status_code, 400, 1)

    status = result.get("status")
    assert status == "fail"
    fail_code = data.get("fail_code")
    assert fail_code == "invalid_parameter"
    logger.info(f"Step 2 성공: 실패 메시지가 정상적으로 확인됨.")
    invalid_params = data.get("fail_detail", {}).get("invalid_params")

    for field in expected_fields:
        assert field in invalid_params, f"에러 상세 내용에 {field} 필드가 누락되었습니다."
        logger.info(f"Step 3 성공: 오류 메시지에서 {field}가 누락됨을 확인.")
        assert invalid_params[field] == "required", f"{field}의 에러 사유가 'required'가 아닙니다."
    logger.info(f"=== {test_id} 테스트 완료 ===")

@pytest.mark.parametrize("case", load_test_data("subject")["quiz_response_cases"])
def test_quiz_response(rest_client, hyojin_headers, subject_params, case):
    test_id, title, quiz_response_key, expected_status_code, expected_is_completed = case["test_id"], case["title"], case["quiz_response_key"], case["expected_status_code"], case["expected_is_completed"]

    logger.info(f"=== {test_id}: {title} 시작 ===")  
    endpoint = "/org/qatrack/material_quiz/response/get/"
    response = rest_client.get(
        endpoint=endpoint,
        headers=hyojin_headers,
        params={
            "quiz_response_id": subject_params.get(quiz_response_key)
        }
    )
    data = response.json()
    result = data.get("_result", {})

    result_status_code = result.get("status_code")
    is_completed = data.get("quiz_response", {}).get("is_completed")

    assert_status_code(result_status_code, expected_status_code, 1)
    assert_equal_value(is_completed, expected_is_completed, "퀴즈 제출 결과", 2)

    logger.info(f"=== {test_id} 테스트 완료 ===")

def test_exercise_submit_success(rest_client, hyojin_headers, subject_params):
    test_id="STU-SBJ-13-001"
    endpoint="/org/qatrack/material_exercise/exercise_running/list/"
    exercise_room_id, user_id = subject_params["exercise_room_id"], subject_params["hyojin_id"]

    logger.info(f"=== {test_id} 시작 ===")
    response = rest_client.get(
        endpoint=endpoint,
        headers=hyojin_headers,
        params={
            "offset": subject_params["offset"],
            "count": subject_params["count"],
            "exercise_room_id": exercise_room_id,
            "user_id": user_id
        }
    )

    data = response.json()
    result = data.get("_result", {})
    status_code = result.get("status_code")
    running_result = data.get("exercise_runnings", {})[0]
    result_exercise_room_id = running_result.get("exercise_room_id")
    result_user_id = running_result.get("user").get("id")

    assert_status_code(status_code, 200, 1)
    assert_equal_value(str(result_exercise_room_id), str(exercise_room_id), "exercise_room_id", 2)
    assert_equal_value(str(result_user_id), str(user_id), "user_id", 3)

    logger.info(f"=== {test_id} 테스트 완료 ===")

@pytest.mark.parametrize("case", load_test_data("subject")["exercise_submit_fail_cases"])
def test_exercise_submit_fail(rest_client, valid_headers, subject_params, case):
    test_id, title, expected_status_code, fail_reason, fail_code = case["test_id"], case["title"], case["expected_status_code"], case["fail_reason"], case["fail_code"]
    endpoint="/org/qatrack/material_exercise/exercise_running/list/"
    params, user_id_key = case["params"], case["user_id_key"]

    if user_id_key != "":
        params["user_id"]=subject_params.get(user_id_key)

    logger.info(f"=== {test_id}: {title} 시작 ===")
    response = rest_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params=params
    )
    data = response.json()
    result = data.get("_result", {})
    result_status_code = result.get("status_code")
    result_fail_reason = result.get("reason")
    result_fail_code = data.get("fail_code")
    assert_status_code(result_status_code, expected_status_code, 1)
    assert_equal_value(result_fail_reason, fail_reason, "실패 원인", 2)
    assert_status_code(result_fail_code, fail_code, 3)

    logger.info(f"=== {test_id} 테스트 완료 ===")