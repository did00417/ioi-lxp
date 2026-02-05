import pytest

#---------------------------- 테스트 시나리오 1 ---------------------------------
# STU-DAB-01-001
def test_all_courses_success(dashboard_client,valid_headers,params):
    endpoint = f"/student/{params['student_id']}"

    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": params["classroom_id"]
        }
    )
    body = response.json()
    assert response.status_code == 200, "Status code 오류"
    assert body["account"]["id"] == int(params["student_id"]), "student_id가 올바르지 않습니다"
    assert len(body["learning_progress"]) > 0, "learning progress is not found"
   
# STU-DAB-01-001 
def test_all_courses_first_page(dashboard_client,valid_headers,params):
    valid_ids = {762843, 762844, 759075, 763817, 759074}
    
    endpoint = f"/student/{params['student_id']}/course"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": params["classroom_id"],
            "offset" : 0,
            "count" : 5
        }
    )
    body = response.json()
    assert response.status_code == 200, "Status code 오류"
    for item in body:
        course_id = item["course"]["id"]
        assert course_id in valid_ids, f"Invalid course ID found: {course_id}"
    
# STU-DAB-01-002
def test_all_courses_second_page(dashboard_client,valid_headers,params):
    valid_ids = {764580, 764630, 764763, 764632, 765299}
    
    endpoint = f"/student/{params['student_id']}/course"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": params["classroom_id"],
            "offset" : 5,
            "count" : 5
        }
    )
    body = response.json()
    assert response.status_code == 200, "Status code 오류"
    for item in body:
        course_id = item["course"]["id"]
        assert course_id in valid_ids, f"Invalid course ID found: {course_id}"
   
# STU-DAB-01-003 
def test_all_courses_invalid_header(dashboard_client,invalid_headers,params):
    endpoint = f"/student/{params['student_id']}"
    
    response = dashboard_client.get(
        endpoint,
        headers = invalid_headers,
        params={
            "classroom_id": params["classroom_id"]
        }
    )
    body = response.json()
    assert response.status_code == 403
    assert "permission" in body["code"]
    
# STU-DAB-01-004
def test_all_courses_invalid_classroom(dashboard_client,valid_headers,params):
    endpoint = f"/student/{params['student_id']}"

    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": params["invalid_classroom_id"]
        }
    )
    body = response.json()
    assert response.status_code == 409
    assert "model" in body["message"]
    
# STU-DAB-01-005
def test_all_courses_invalid_student(dashboard_client,valid_headers,params):
    endpoint = f"/student/{params['invalid_student_id']}"

    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": params["classroom_id"]
        }
    )
    body = response.json()
    assert response.status_code == 409
    assert "model" in body["message"]
    
# STU-DAB-01-006
def test_all_courses_delete(classroom_client,valid_headers,params):
    endpoint = f"/classroom/{params['classroom_id']}"

    response = classroom_client.delete(
        endpoint,
        headers = valid_headers
    )

    body = response.json()
    assert response.status_code == 403
    assert "permission" in body["code"]
    
# STU-DAB-02-001
def test_one_course(dashboard_client,valid_headers,params):
    endpoint = f"/student/{params['student_id']}/lecture"
    
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": params["classroom_id"],
            "course_id" : params["course_id"],
            "filter_parent_lecture_id" : "null",
            "offset" : 0,
            "count" : 40
        }
    )
    body = response.json()
    assert response.status_code == 200
    assert body[0]["lecture"]["course_id"] == params["course_id"]
    assert len(body[0]["learning_progress"]) > 0
    
# STU-DAB-02-002
def test_one_course_invalid_token(dashboard_client,invalid_headers,params):
    endpoint = f"/student/{params['student_id']}/lecture"
    
    response = dashboard_client.get(
        endpoint,
        headers = invalid_headers,
        params={
            "classroom_id": params["classroom_id"],
            "course_id" : params["course_id"],
            "filter_parent_lecture_id" : "null",
            "offset" : 0,
            "count" : 40
        }
    )
    body = response.json()
    assert response.status_code == 403
    assert "permission" in body["message"]
    
# STU-DAB-02-003
def test_one_course_invalid_classroom(dashboard_client,valid_headers,params):
    endpoint = f"/student/{params['student_id']}"
    
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": params["invalid_classroom_id"],
            "course_id" : params["course_id"],
        }
    )
    body = response.json()
    assert response.status_code == 409
    assert "model" in body["message"]
    
# STU-DAB-02-004
def test_one_course_invalid_student(dashboard_client,valid_headers,params):
    endpoint = f"/student/{params['invalid_student_id']}"
    
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": params["classroom_id"],
            "course_id" : params["course_id"],
        }
    )
    body = response.json()
    assert response.status_code == 409
    assert "model" in body["message"]
    
# STU-DAB-02-005
def test_one_course_invalid_course(dashboard_client,valid_headers,params):
    endpoint = f"/student/{params['student_id']}"
    
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": params["classroom_id"],
            "course_id" : params["invalid_course_id"],
        }
    )
    body = response.json()
    assert response.status_code == 409
    assert "model" in body["message"]