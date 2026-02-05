import pytest

# 테스트 케이스: STU-CHM-01-001(유효한 토큰 사용 시 사용자 정보 조회)

def test_get_user_details(rest_client,valid_headers):
    endpoint = "/global/account/get/"

    response = rest_client.get(
        endpoint,
        headers=valid_headers
    )

    assert response.status_code == 200

    user_data = response.json()
    account = user_data["account"]
    # print(user_data)

    # 핵심 필드 존재 여부
    assert "id" in account
    assert isinstance(account["id"], int)
    assert account["id"] > 0

    assert "fullname" in account
    assert isinstance(account["fullname"], str)
    assert account["fullname"]

    assert "email" in account
    assert "@" in account["email"]

# 테스트 케이스: STU-CHM-01-002 (토큰 없이 사용자 정보 조회 시 에러 발생)

def test_get_user_not_access_token(rest_client):
    endpoint = "/global/account/get/"

    response = rest_client.get(
        endpoint,
    )

    error_data = response.json()
    assert "_result" in error_data
    assert error_data["_result"]["status_code"] == 403
    assert error_data["fail_code"] == "not_found_sessionkey"
    assert error_data["fail_message"] == "authorization failed"
    
# 테스트 케이스: STU-CHM-01-003 (만료된 토큰 사용 시 에러 발생)
    
def test_get_user_invalid_token(rest_client, invalid_headers):
    endpoint = "/global/account/get/"

    response = rest_client.get(
        endpoint,
        headers=invalid_headers
    )

    error_data = response.json()
    assert "_result" in error_data
    assert error_data["_result"]["status_code"] == 403
    assert error_data["fail_code"] == "no_account_api_session"
    assert error_data["fail_message"] == "authorization failed"

# 테스트 케이스: STU-CHM-02-001(수강생이 이어서 해야하는 학습 내용과 정상적으로 연결이 되는지 확인)

def test_get_contiune_learning_lecture(dashboard_client, valid_headers, classroom_id):
    endpoint = f"/classroom/{classroom_id}/next_lecture_page"
    
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers
        )
    
    lecture_data = response.json()
    assert response.status_code == 200
    assert "lecture_page_id" in lecture_data
    assert isinstance(lecture_data["lecture_page_id"], int)
    assert lecture_data["lecture_page_id"] > 0
    assert "course_title" in lecture_data
    assert isinstance(lecture_data["course_title"], str)

# 테스트 케이스: STU-CHM-02-002(필수 path 파라미터 누락시 에러 발생 확인)
  
def test_get_continue_learning_lecture_without_classroom_id(dashboard_client, valid_headers):
    endpoint = "/next_lecture_page"
    
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers)  
    
    assert response.status_code == 404
    
    error_data = response.json()
    
    assert "detail" in error_data
    assert error_data["detail"] == "Not Found"
    
# 테스트 케이스: STU-CHM-02-003(잘못된 classroom_id 사용 시 에러 발생 확인)
    
def test_get_continue_learning_lecture_invalid_classroom_id(dashboard_client, valid_headers, classhome_data):
    endpoint = f"/classroom/{classhome_data['classhome']['invalid_classroom_id']}/next_lecture_page"
    
    response = dashboard_client.get(
        endpoint, 
        headers=valid_headers)  
    
    assert response.status_code == 409
    
    error_data = response.json()
    
    assert error_data["code"] == "model_not_found"
    assert error_data["message"] == "Failed to find target model.Check specific information in detail."
    assert "detail" in error_data
    assert "Classroom" in error_data["detail"]
    classroom_detail = error_data["detail"]["Classroom"]
    assert "id" in classroom_detail

import pytest

# 테스트 케이스: STU-CHM-03-001(수강생의 수업 일정 정보를 정상적으로 조회하는지 확인)

def test_get_class_schedule(
    classroom_client,
    valid_headers,
    params,
    schedule_common,
    schedule_cases
    ):
    
    endpoint = "/schedule/ics"
    params = {
        "classroom_id": params["classroom_id"],
        **schedule_common,
        **schedule_cases["STU-CHM-03-001"]
    }
    response = classroom_client.get(
        endpoint, 
        headers=valid_headers, 
        params=params)
        
    assert response.status_code == 200

# 테스트 케이스: STU-CHM-03-002(수강일정이 없는 날짜 조회 시 해당 날짜에 실제 일정이 없음을 확인)

def test_get_no_class_schedule(
    classroom_client,
    valid_headers,
    params,
    schedule_common,
    schedule_cases
    ):
         
    endpoint = "/schedule/ics"
    
    params = {
        "classroom_id": params["classroom_id"],
        **schedule_common,
        **schedule_cases["STU-CHM-03-002"]
        }
    
    response = classroom_client.get(
        endpoint, 
        headers=valid_headers, 
        params=params
    )
    
    assert response.status_code == 200
    ics_text = response.text
    assert "RRULE" in ics_text
    assert "DTSTART;TZID=KST:20260131" not in ics_text

# 테스트 케이스: STU-CHM-03-003(인정 토큰 없이 수강일정 조회 시 에러 발생 확인)
      
def test_get_class_schedule_no_token(
    classroom_client,
    params,
    schedule_common,
    schedule_cases
    ):
    endpoint = "/schedule/ics"
    
    params = {
        "classroom_id": params["classroom_id"],
        **schedule_common,
        **schedule_cases["STU-CHM-03-003"]
        }
    
    response = classroom_client.get(
        endpoint, 
        headers=None, 
        params=params
    )
    
    assert response.status_code == 403
    
    error_datsa = response.json()
    
    # assert "code" in error_datsa
    assert error_datsa["code"] == "no_access_token"
    

# 테스트 케이스: STU-CHM-03-004(날짜 파라미터 누락 시 에러 발생 확인)


def test_get_schedule_fails_when_date_parameters_missing(
    classroom_client,
    valid_headers,
    params,
    schedule_common,
    schedule_cases
    ):
    endpoint = "/schedule/ics"
    
    # dt_start_ge 파라미터 누락
    params = {
        "classroom_id": params["classroom_id"],
        **schedule_common,
        **schedule_cases["STU-CHM-03-004"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    assert response.status_code == 422
    
    error_data = response.json()
    #detail은 리스트 형태
    detail = error_data["detail"]
    assert detail[0]["type"] == "missing"
    assert detail[0]["loc"] == ["query", "dt_start_ge"]

    assert detail[1]["msg"] == "Field required"
    assert detail[1]["loc"] == ["query", "dt_start_le"]


# 테스트 케이스: STU-CHM-03-005(잘못된 날짜 포맷 입력시 에러 발생 확인)

def test_get_schedule_fails_when_date_format_invalid(
    classroom_client,
    valid_headers,
    params,
    schedule_common,
    schedule_cases
    ):
    endpoint = "/schedule/ics"
    
    # dt_start_ge 파라미터 잘못된 포맷
    params = {
        "classroom_id": params["classroom_id"],
        **schedule_common,
        **schedule_cases["STU-CHM-03-005"]
    }
    
    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params=params
    )
    
    assert response.status_code == 422
    
    error_data = response.json()
    #detail은 리스트 형태
    detail = error_data["detail"]
    assert detail[0]["type"] == "datetime_from_date_parsing"
    assert detail[0]["loc"] == ["query", "dt_start_ge"]

    assert detail[1]["type"] == "datetime_from_date_parsing"
    assert detail[1]["loc"] == ["query", "dt_start_le"]
    
# 테스트 케이스: STU-CHM-04-001(수강생이 강의실의 위치를 정상 조회할 수 있는지 확인)

# def test_get_classroom_location(
#     rest_client,
#     valid_headers,
#     params,
#     lecture_common
#     ):
#     endpoint = f"/org/qatrack/course/lectureroom/get/{lecture_common}"
    
#     }"
#     params = {
        
#     }
    
    