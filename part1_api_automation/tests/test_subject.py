import logging
import pytest
from utils.config_loader import load_test_data

logger = logging.getLogger(__name__)

def test_fetch_sbj_list(classroom_client, valid_headers, subject_params):
    """STU-SBJ-01-001: 클래스 학습 목록 정상 조회"""
    logger.info("=== STU-SBJ-01-001: 클래스 학습 목록 정상 조회 ===")
    classroom_id = subject_params['classroom_id']
    count = 10
    endpoint = f"/classroom/{classroom_id}/course"

    response = classroom_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={
            "skip": 0,
            "count": count
        }
    )
    response_count = len(response.json())

    if response.status_code == 200:
        logger.info(f"Step 1 성공: 예상대로 200 OK 반환됨.")
    else:
        logger.error(f"Step 1 실패: 200을 기대했으나 {response.status_code} 반환됨.")

    if response_count <= count:
        logger.info(f"Step 2 성공: 응답 데이터 갯수({response_count})가 요청한 count({count})보다 작거나 같음.")
    else:
        logger.error(f"Step 2 실패: 응답 데이터 갯수({response_count})가 요청한 count({count})보다 많음.")
    
    assert response.status_code == 200
    assert response_count <= count
    logger.info("=== STU-SBJ-01-001 테스트 완료 ===")

def test_fetch_sbj_list_invalid_classid(classroom_client, valid_headers, subject_params):
    """STU-SBJ-01-002: 올바르지 않은 클래스 id로 학습 목록 조회"""
    logger.info("=== STU-SBJ-01-002: 올바르지 않은 클래스 id로 학습 목록 조회 ===")
    invalid_classroom_id = subject_params['invalid_classroom_id']
    count = 10
    endpoint=f"/classroom/{invalid_classroom_id}/course"

    response = classroom_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={
            "skip" : 0,
            "count": count
        }
    )
    data = response.json()
    result_code = data.get('code', "")
    if response.status_code == 403:
        logger.info(f"Step 1 성공: 예상대로 403 Forbidden 반환됨.")
    else:
        logger.error(f"Step 1 실패: 403을 기대했으나 {response.status_code} 반환됨.")

    if "permission" in result_code:
        logger.info(f"Step 2 성공: 응답 코드에 'permission' 키워드 확인됨 (응답값: {result_code})")
    else:
        logger.error(f"Step 2 실패: 응답 코드에 'permission'이 없음 (실제 응답: {result_code})")

    assert response.status_code == 403
    assert "permission" in result_code
    logger.info("=== STU-SBJ-01-002 테스트 완료 ===")

def test_fetch_sbj_list_without_parameter(classroom_client, valid_headers, subject_params):
    """STU-SBJ-01-003: 필수 파라미터가 제공되지 않았을 때 학습 목록 조회"""
    logger.info("=== STU-SBJ-01-003: 필수 파라미터가 제공되지 않았을 때 학습 목록 조회 ===")
    classroom_id = subject_params['classroom_id']
    endpoint=f"/classroom/{classroom_id}/course"

    response = classroom_client.get(
        endpoint=endpoint,
        headers=valid_headers
    )
    data = response.json()
    detail = data.get("detail", [{}])
    error_msg = detail[0].get("msg") if detail else None
    if response.status_code == 422:
        logger.info(f"Step 1 성공: 예상대로 422 Unprocessable Entity 반환됨.")
    else:
        logger.error(f"Step 1 실패: 422를 기대했으나 {response.status_code} 반환됨.")

    if error_msg == "Field required":
        logger.info(f"Step 2 성공: 응답 내용에 'Field required' 키워드가 포함됨.")
    else:
        logger.warning(f"Step 2 실패: 응답 내용에 'Field required' 키워드가 포함되지 않음.")

    assert response.status_code == 422
    assert error_msg == "Field required"
    logger.info("=== STU-SBJ-01-003 테스트 완료 ===")

def test_fetch_sbj_detail(classroom_client, valid_headers, subject_params):
    """STU-SBJ-02-001: 학습 과목 상세 내용 정상 조회"""
    logger.info("=== STU-SBJ-02-001: 학습 과목 상세 내용 정상 조회 ===")
    classroom_id = subject_params['classroom_id']
    course_id = subject_params['course_id']
    endpoint = f"/classroom/{classroom_id}/course/{course_id}"

    response = classroom_client.get(
        endpoint=endpoint,
        headers=valid_headers
    )
    data = response.json()
    result_course_id = data.get('course_id', '')

    if response.status_code == 200:
        logger.info(f"Step 1 성공: 예상대로 200 OK 반환됨.")
    else:
        logger.error(f"Step 1 실패: 200을 기대했으나 {response.status_code} 반환됨.")

    if result_course_id == course_id:
        logger.info(f"Step 2 성공: 요청한 course_id({course_id})와 응답 값의 course_id({result_course_id})가 일치함.")
    else:
        logger.error(f"Step 2 실패: 요청한 course_id({course_id})와 응답 값의 course_id({result_course_id})가 일치하지 않음.")

    assert response.status_code == 200
    assert result_course_id == course_id
    logger.info("=== STU-SBJ-02-001 테스트 완료 ===")

def test_fetch_sbj_map(dashboard_client, valid_headers, subject_params):
    """STU-SBJ-03-001: 학습 맵 정상 조회"""
    logger.info("=== STU-SBJ-03-001: 학습 맵 정상 조회 ===")
    endpoint=f"/student/{subject_params['student_id']}/lecture"

    response = dashboard_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={
            "classroom_id" : subject_params['classroom_id'],
            "offset":0,
            "count":40
        }
    )

    data = response.json()
    first_item = data[0] if isinstance(data, list) and len(data) > 0 else {}
    lecture_data = first_item.get('lecture', {})
    actual_title = lecture_data.get('title')

    if response.status_code == 200:
        logger.info(f"Step 1 성공: 예상대로 200 OK 반환됨.")
    else:
        logger.error(f"Step 1 실패: 200을 기대했으나 {response.status_code} 반환됨.")
    if actual_title:
        logger.info(f"성공: 학습 맵 제목을 확인했습니다. ({actual_title})")
    else:
        logger.error(f"실패: 'title' 키가 없거나 값이 비어있습니다. (데이터: {lecture_data})")
    assert response.status_code == 200
    assert actual_title is not None
    assert len(actual_title) > 0

    logger.info("=== STU-SBJ-03-001 테스트 완료 ===")   
    
def test_fetch_sbj_map_without_parameter(dashboard_client, valid_headers, subject_params):
    """STU-SBJ-03-002: 필수 파라미터가 제공되지 않았을 때 학습 맵 조회"""
    logger.info("=== STU-SBJ-03-002: 필수 파라미터가 제공되지 않았을 때 학습 맵 조회 ===")
    endpoint=f"/student/{subject_params['student_id']}/lecture"

    response = dashboard_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={
            "classroom_id" : subject_params['classroom_id'],
        }
    )
    data = response.json()

    if response.status_code == 422:
        logger.info(f"Step 1 성공: 예상대로 422 Unprocessable Entity 반환됨.")
    else:
        logger.error(f"Step 1 실패: 422를 기대했으나 {response.status_code} 반환됨.")

    if data["detail"][0]["msg"] == "Field required":
        logger.info(f"Step 2 성공: 응답 내용에 'Field required' 키워드가 포함됨.")
    else:
        logger.warning(f"Step 2 실패: 응답 내용에 'Field required' 키워드가 포함되지 않음.")

    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "Field required"
    logger.info("=== STU-SBJ-03-002 테스트 완료 ===")

def test_fetch_child_lectures(rest_client, valid_headers, subject_params):
    """STU-SBJ-05-001: 특정 과목의 하위 강의 목록 조회"""
    logger.info("=== STU-SBJ-05-001: 특정 과목의 하위 강의 목록 조회 ===")
    endpoint = "/org/qatrack/dashboard/user/lecture_page/list/"
    course_id = int(subject_params['course_id'])
    user_id = int(subject_params['user_id'])

    response = rest_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={
            "course_id" : course_id,
            "user_id" : user_id,
        }
    )
    data = response.json()
    data_user_id = int(data.get("user", {}).get("id"))
    lectures = data.get("lectures", [])
    if response.status_code == 200:
        logger.info(f"Step 1 성공: 예상대로 200 OK 반환됨.")
    else:
        logger.error(f"Step 1 실패: 200을 기대했으나 {response.status_code} 반환됨.")
    if data_user_id == user_id:
        logger.info(f"Step 2 성공: 요청한 user_id({user_id})와 응답 값의 user_id({data_user_id})가 일치함.")
    else:
        logger.error(f"Step 2 실패: 요청한 user_id({user_id})와 응답 값의 user_id({data_user_id})가 일치하지 않음.")
    if not lectures:
        logger.error("Step 3 실패: lectures 데이터가 비어 있습니다.")
    first_lecture = lectures[0]
    if "lecture_pages" in first_lecture and len(first_lecture["lecture_pages"]) > 0:
        logger.info(f"Step 3 성공: 강의 및 상세 페이지 구조 확인 완료 (강의명: {first_lecture.get('title')})")
    else:
        logger.warning(f"Step 3 주의: 강의({first_lecture.get('title')}) 내에 페이지가 없습니다.")

    assert response.status_code == 200
    assert data_user_id == user_id
    assert "lecture_pages" in first_lecture and len(first_lecture["lecture_pages"]) > 0

    logger.info("=== STU-SBJ-05-001 테스트 완료 ===")

def test_fetch_child_lectures_invalid_course_id(rest_client, valid_headers, subject_params):
    """STU-SBJ-05-002: 비정상 course_id로 하위 강의 목록 조회"""
    logger.info("=== STU-SBJ-05-002: 비정상 course_id로 하위 강의 목록 조회 ===")
    endpoint = "/org/qatrack/dashboard/user/lecture_page/list/"
    invalid_course_id = int(subject_params['invalid_course_id'])
    user_id = int(subject_params['user_id'])

    response = rest_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={
            "course_id" : invalid_course_id,
            "user_id" : user_id,
        }
    )
    data = response.json()
    result = data.get("_result", {})
    result_status = result.get('status')
    result_status_code = result.get('status_code')

    if result_status == "fail":
        logger.info(f"Step 1: 응답에서 'fail' 키워드 확인 성공")
    else:
        logger.error(f"Step 1: 응답에서 'fail' 키워드 확인 실패, status={result_status}")
    
    if result_status_code == 400:
        logger.info(f"Step 2: 응답 코드 400 확인 성공")
    else:
        logger.warning(f"Sep 2: 응답 코드 400 확인 실패, status_code={result_status_code}")

    assert response.status_code == 200
    assert result_status == "fail"
    assert result_status_code == 400
    logger.info("=== STU-SBJ-05-002 테스트 완료 ===")


def test_fetch_child_lectures_invalid_user_id(rest_client, valid_headers, subject_params):
    """STU-SBJ-05-003: 비정상 user_id로 하위 강의 목록 조회"""
    logger.info("=== STU-SBJ-05-003: 비정상 user_id로 하위 강의 목록 조회 ===")
    endpoint = "/org/qatrack/dashboard/user/lecture_page/list/"
    course_id = int(subject_params['course_id'])
    invalid_user_id = int(subject_params['invalid_user_id'])

    response = rest_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={
            "course_id" : course_id,
            "user_id" : invalid_user_id,
        }
    )
    data = response.json()
    result = data.get("_result", {})
    result_status = result.get('status')
    result_status_code = result.get('status_code')
    assert response.status_code == 200
    
    if result_status == "fail":
        logger.info(f"Step 1: 응답에서 'fail' 키워드 확인 성공")
    else:
        logger.error(f"Step 1: 응답에서 'fail' 키워드 확인 실패, status={result_status}")
    
    if result_status_code == 409:
        logger.info(f"Step 2: 응답 코드 409 확인 성공")
    else:
        logger.warning(f"Sep 2: 응답 코드 409 확인 실패, status_code={result_status_code}")

    assert response.status_code == 200
    assert result_status == "fail"
    assert result_status_code == 409

    logger.info("=== STU-SBJ-05-003 테스트 완료 ===")

@pytest.mark.parametrize("case", load_test_data("subject")["lecture_cases"])
def test_fetch_material_unified(rest_client, valid_headers, subject_params, case):
    """통합 강의 콘텐츠(퀴즈/과제/실습) 조회 테스트"""
    test_id = case["test_id"]
    endpoint = case["endpoint"]
    param_key = case["param_key"]
    id_key = case["id_key"]
    expected_status_code = case["expected_status_code"]
    expected_result = case["expected_result"]

    logger.info(f"=== {test_id}: 테스트 시작 ===")
    
    request_id = subject_params[id_key]
    
    response = rest_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={param_key: request_id}
    )
    
    data = response.json()
    result = data.get("_result", {})
    actual_status_code = result.get('status_code')
    actual_result = result.get('status')

    if actual_status_code == expected_status_code:
        logger.info(f"Step 1 성공: status_code {actual_status_code} 확인됨.")
    else:
        logger.error(f"Step 1 실패: {expected_status_code}를 기대했으나 {actual_status_code} 반환됨.")

    if expected_status_code == 200:
        # 응답 key가 'material_quiz', 'material_assignment' 식으로 들어오므로 이를 동적으로 파싱
        resource_key = endpoint.split('/')[-3]
        result_data = data.get(resource_key, {})
        result_id = result_data.get('id')
        
        assert request_id == result_id
        logger.info(f"Step 2 성공: 요청 ID와 응답 ID({result_id}) 일치 확인.")
    else:
        assert actual_result == expected_result
        logger.info(f"Step 2 성공: 예상된 실패 상태({expected_result}) 확인.")

    assert response.status_code == 200
    assert actual_status_code == expected_status_code
    
    logger.info(f"=== {test_id} 테스트 완료 ===")

@pytest.mark.parametrize("id, title, direction, offset", [("STU-SBJ-07-001", "이전 강의 목록 조회 성공", "prev", -1), ("STU-SBJ-08-001", "다음 강의 목록 조회 성공", "next", +1)])
def test_fetch_adjacent_lecture(course_client, valid_headers, subject_params, id, title, direction, offset):
    logger.info(f"=== {id}: {title} ===")
    base_lecture_id = subject_params["lecture_id_with_prev"] if direction == "prev" else subject_params["lecture_id_with_next"]
    course_id = subject_params["course_id_test_prev"] if direction == "prev" else subject_params["course_id_test_next"]
    endpoint = f"/lecture/{base_lecture_id}/{direction}"
    expected_id = base_lecture_id + offset

    response = course_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={
            "elice_course_id": course_id
        }
    )
    data = response.json()
    status_code = response.status_code
    result_course_id = data.get("course_id")
    result_id = data.get("id")
    if status_code == 200:
        logger.info(f"Step 1 성공: 예상대로 200 OK 반환됨.")
    else:
        logger.error(f"Step 1 실패: 200을 기대했으나 {response.status_code} 반환됨.")
    if expected_id == result_id:
        logger.info(f"Step 2: 기대값 ({expected_id})와 응답 값이 ({result_id})가 일치함.")
    else:
        logger.error(f"Step 2: 기대값 ({expected_id})와 응답 값이 ({result_id})가 일치하지 않음.")
    if course_id == result_course_id:
        logger.info(f"Step 3: 요청한 course_id({course_id})와 응답 값의 course_id({result_course_id})가 일치함.")
    else:
        logger.error(f"Step 3: 요청한 course_id({course_id})와 응답 값의 course_id({result_course_id})가 일치하지 않음.")
    assert status_code == 200
    assert expected_id == result_id
    assert course_id == result_course_id
    
    logger.info(f"=== {id} 테스트 완료 ===")
