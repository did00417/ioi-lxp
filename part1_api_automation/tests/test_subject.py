import logging

def test_fetch_sbj_list(classroom_client, valid_headers, subject_params):
    """STU-SBJ-01-001: 클래스 학습 목록 정상 조회"""
    classroom_id = subject_params['classroom_id']
    count = 10

    response = classroom_client.get(
        endpoint=f"/classroom/{classroom_id}/course",
        headers=valid_headers,
        params={
            "skip": 0,
            "count": count
        }
    )
    response_count = len(response.json())
    assert response.status_code == 200, f"요청이 올바르게 처리되지 않았습니다. 상태 코드: {response.status_code}"
    assert response_count <= count, f"요청한 count({count})보다 많은 데이터({response_count})가 반환되었습니다."

def test_fetch_sbj_list_invalid_classid(classroom_client, valid_headers, subject_params):
    """STU-SBJ-01-002: 올바르지 않은 클래스 id로 학습 목록 조회"""
    invalid_classroom_id = subject_params['invalid_classroom_id']
    count = 10

    response = classroom_client.get(
        endpoint=f"/classroom/{invalid_classroom_id}/course",
        headers=valid_headers,
        params={
            "skip" : 0,
            "count": count
        }
    )
    data = response.json()
    assert response.status_code == 403
    assert "permission" in data["code"]

def test_fetch_sbj_list_no_parameter(classroom_client, valid_headers, subject_params):
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
    data = response.json()
    assert response.status_code == 200, f"요청이 올바르게 처리되지 않았습니다. 상태 코드: {response.status_code}"
    