import pytest

#---------------------------- 테스트 시나리오 1 ---------------------------------
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
    assert response.status_code == 200
    assert body["account"]["id"] == int(params["student_id"])
    assert len(body["learning_progress"]) > 0
    
def test_all_courses_second_page(dashboard_client,valid_headers,params):
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
    assert response.status_code == 200
    
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
    
