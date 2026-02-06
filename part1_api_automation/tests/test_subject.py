import logging

logger = logging.getLogger(__name__)

def test_fetch_sbj_list(classroom_client, valid_headers, subject_params):
    """STU-SBJ-01-001: 클래스 학습 목록 정상 조회"""
    logger.info("=== STU-SBJ-01-001: 클래스 학습 목록 정상 조회 ===")
    classroom_id = subject_params['classroom_id']
    count = 10
    endpoint = f"/classroom/{classroom_id}/course"

    logger.info(f"API 요청 시작: {classroom_client.base_url}{endpoint}")
    response = classroom_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={
            "skip": 0,
            "count": count
        }
    )
    logger.debug(f"응답 헤더: {response.headers}")
    logger.debug(f"응답 바디: {response.text}")
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

    logger.info(f"API 요청 시작: {classroom_client.base_url}{endpoint}")
    response = classroom_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params={
            "skip" : 0,
            "count": count
        }
    )
    logger.debug(f"응답 헤더: {response.headers}")
    logger.debug(f"응답 바디: {response.text}")
    data = response.json()

    if response.status_code == 403:
        logger.info(f"Step 1 성공: 예상대로 403 Forbidden 반환됨.")
    else:
        logger.error(f"Step 1 실패: 403을 기대했으나 {response.status_code} 반환됨.")

    if "permission" in data["code"]:
        logger.info(f"Step 2 성공: 응답 코드에 'permission' 키워드 확인됨 (응답값: {data['code']})")
    else:
        logger.error(f"Step 2 실패: 응답 코드에 'permission'이 없음 (실제 응답: {data.get('code')})")

    assert response.status_code == 403
    assert "permission" in data["code"] 
    logger.info("=== STU-SBJ-01-002 테스트 완료 ===")

def test_fetch_sbj_list_without_parameter(classroom_client, valid_headers, subject_params):
    """STU-SBJ-01-003: 필수 파라미터가 제공되지 않았을 때 학습 목록 조회"""
    classroom_id = subject_params['classroom_id']

    response = classroom_client.get(
        endpoint=f"/classroom/{classroom_id}/course",
        headers=valid_headers
    )
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "Field required"

def test_fetch_sbj_detail(classroom_client, valid_headers, subject_params):
    """STU-SBJ-02-001: 학습 과목 상세 내용 정상 조회"""
    classroom_id = subject_params['classroom_id']
    course_id = subject_params['course_id']

    response = classroom_client.get(
        endpoint=f"/classroom/{classroom_id}/course/{course_id}",
        headers=valid_headers
    )
    data = response.json()

    assert response.status_code == 200, f"요청이 올바르게 처리되지 않았습니다. 상태 코드: {response.status_code}"
    assert data["course_id"] == course_id

def test_fetch_sbj_map(dashboard_client, valid_headers, subject_params):
    """STU-SBJ-03-001: 학습 맵 정상 조회"""
    response = dashboard_client.get(
        endpoint=f"/student/{subject_params['student_id']}/lecture",
        headers=valid_headers,
        params={
            "classroom_id" : subject_params['classroom_id'],
            "offset":0,
            "count":40
        }
    )
    assert response.status_code == 200, f"요청이 올바르게 처리되지 않았습니다. 상태 코드: {response.status_code}"
    
def test_fetch_sbj_map_without_parameter(dashboard_client, valid_headers, subject_params):
    """STU-SBJ-03-002: 필수 파라미터가 제공되지 않았을 때 학습 맵 조회"""
    response = dashboard_client.get(
        endpoint=f"/student/{subject_params['student_id']}/lecture",
        headers=valid_headers,
        params={
            "classroom_id" : subject_params['classroom_id'],
        }
    )
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["msg"] == "Field required"

def test_fetch_child_lectures():
    """STU-SBJ-05-001: 특정 과목의 하위 강의 목록 조회"""
