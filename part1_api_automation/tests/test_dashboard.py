import pytest
import logging

logger = logging.getLogger(__name__)

#------------------ 테스트 시나리오 STU-DAB-01 : 학습 대시보드 메뉴의 전체 과목 학습 현황과 관련된 API 테스트 ------------------------------------
# STU-DAB-01-001
def test_all_courses_learning_page_success(dashboard_client,valid_headers,dash_params):
    logger.info("=== STU-DAB-01-001: 전체 과목 학습 현황 페이지 정상 조회 ===")
    
    endpoint = f"/student/{dash_params['student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers=valid_headers,
        params={"classroom_id": dash_params["classroom_id"]}
    )
    body = response.json()

    try:
        assert response.status_code == 200, "Step 1 실패: status_code != 200"
        logger.info("Step 1 성공: 200 OK 반환됨")
        assert body["account"]["id"] == int(dash_params["student_id"]), "Step 2 실패: account id 불일치"
        logger.info("Step 2 성공: 올바른 account id 반환됨")
        assert len(body["learning_progress"]) > 0, "Step 3 실패: learning_progress 데이터 존재하지 않음"
        logger.info("Step 3 성공: learning_progress 데이터 존재")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise

    logger.info("=== STU-DAB-01-001 테스트 완료 ===")
   
# STU-DAB-01-002 
def test_all_courses_first_page(dashboard_client,valid_headers,dash_params, dash_page):
    logger.info("=== STU-DAB-01-002: 1 페이지 과목 리스트 조회 ===")
    
    valid_course_ids = set(dash_page["one_course_ids"])
    endpoint = f"/student/{dash_params['student_id']}/course"
    response = dashboard_client.get(
        endpoint,
        headers=valid_headers,
        params={
            "classroom_id": dash_params["classroom_id"],
            "offset": 0,
            "count": 5
        }
    )
    body = response.json()
    invalid_ids = []
    for item in body:
        course_id = item["course"]["id"]
        if course_id not in valid_course_ids:
            invalid_ids.append(course_id)

    try :
        assert response.status_code == 200, "Step 1 실패: status_code != 200"
        logger.info("Step 1 성공: 예상대로 200 OK 반환됨")
        assert not invalid_ids, f"Step 2 실패: 유효하지 않은 course_id 발견 - {invalid_ids}"
        logger.info("Step 2 성공: 1 페이지 과목 리스트 정상 반환됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise

    logger.info("=== STU-DAB-01-002 테스트 완료 ===")
    
# STU-DAB-01-003
def test_all_courses_second_page(dashboard_client,valid_headers,dash_params, dash_page):
    logger.info("=== STU-DAB-01-003: 2 페이지 과목 리스트 조회 ===")
    
    valid_course_ids = set(dash_page["two_course_ids"])
    endpoint = f"/student/{dash_params['student_id']}/course"
    response = dashboard_client.get(
        endpoint,
        headers=valid_headers,
        params={
            "classroom_id": dash_params["classroom_id"],
            "offset": 5,
            "count": 5
        }
    )
    body = response.json()
    invalid_ids = []
    for item in body:
        course_id = item["course"]["id"]
        if course_id not in valid_course_ids:
            invalid_ids.append(course_id)

    try :
        assert response.status_code == 200, "Step 1 실패: status_code != 200"
        logger.info("Step 1 성공: 예상대로 200 OK 반환됨")
        assert not invalid_ids, f"Step 2 실패: 유효하지 않은 course_id 발견 - {invalid_ids}"
        logger.info("Step 2 성공: 2 페이지 과목 리스트 정상 반환됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-01-003 테스트 완료 ===")
   
# STU-DAB-01-004 
def test_all_courses_page_with_invalid_token(dashboard_client,invalid_headers,dash_params):
    logger.info("=== STU-DAB-01-004: 만료된 토큰으로 전체 과목 학습 현황 조회 ===")
    
    endpoint = f"/student/{dash_params['student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = invalid_headers,
        params={
            "classroom_id": dash_params["classroom_id"]
        }
    )
    body = response.json()
    
    try :
        assert response.status_code == 403, "Step 1 실패: status_code != 403"
        logger.info("Step 1 성공: 예상대로 403 Forbidden 반환됨")
        assert "permission" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-01-004 테스트 완료 ===")
    
# STU-DAB-01-005
def test_all_courses_page_with_invalid_classroom(dashboard_client,valid_headers,dash_params):
    logger.info("=== STU-DAB-01-005: 소속되지 않은 클래스의 전체 과목 학습 현황 조회 ===")
    
    endpoint = f"/student/{dash_params['student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": dash_params["invalid_classroom_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-01-005 테스트 완료 ===")
    
# STU-DAB-01-006
def test_all_courses_page_with_invalid_student(dashboard_client,valid_headers,dash_params):
    logger.info("=== STU-DAB-01-006: 유효하지 않은 student id로 전체 과목 학습 현황 조회 ===")
    
    endpoint = f"/student/{dash_params['invalid_student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": dash_params["classroom_id"]
        }
    )
    body = response.json()
    
    try :
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-01-006 테스트 완료 ===")
    
# STU-DAB-01-007
def test_all_courses_delete_with_student_account(classroom_client,valid_headers,dash_params):
    logger.info("=== STU-DAB-01-007: 학생 권한으로 전체 과목 학습 현황 삭제 ===")
    
    endpoint = f"/classroom/{dash_params['classroom_id']}"
    response = classroom_client.delete(
        endpoint,
        headers = valid_headers
    )
    body = response.json()
    
    try :
        assert response.status_code == 403, "Step 1 실패: status_code != 403"
        logger.info("Step 1 성공: 예상대로 403 Forbidden 반환됨")
        assert "permission" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-01-007 테스트 완료 ===")
    
#-------------------- 테스트 시나리오 STU-DAB-02 : 학습 대시보드 메뉴의 과목별 학습 현황과 관련된 API 테스트 ------------------------------------
# STU-DAB-02-001
def test_course_learning_page_success(dashboard_client,valid_headers,dash_params):
    logger.info("=== STU-DAB-02-001: 과목 선택 후 학습 현황 페이지 정상 조회 ===")
    
    endpoint = f"/student/{dash_params['student_id']}/lecture" 
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "filter_parent_lecture_id" : "null",
            "offset" : 0,
            "count" : 40
        }
    )
    body = response.json()
    
    try :
        assert response.status_code == 200, "Step 1 실패: status_code != 200"
        logger.info("Step 1 성공: 예상대로 200 OK 반환됨")
        assert body[0]["lecture"]["course_id"] == dash_params["course_id"], "Step 2 실패: course id 불일치"
        logger.info("Step 2 성공: 올바른 course id 반환됨")
        assert len(body[0]["learning_progress"]) > 0, "Step 3 실패: learning_progress 데이터 존재하지 않음"
        logger.info("Step 3 성공: learning_progress 데이터 존재")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-02-001 테스트 완료 ===")
    
# STU-DAB-02-002
def test_course_page_with_invalid_token(dashboard_client,invalid_headers,dash_params):
    logger.info("=== STU-DAB-02-002: 만료된 토큰으로 한 과목의 학습 현황 조회 ===")
    
    endpoint = f"/student/{dash_params['student_id']}/lecture"
    response = dashboard_client.get(
        endpoint,
        headers = invalid_headers,
        params={
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "filter_parent_lecture_id" : "null",
            "offset" : 0,
            "count" : 40
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 403, "Step 1 실패: status_code != 403"
        logger.info("Step 1 성공: 예상대로 403 Forbidden 반환됨")
        assert "permission" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-02-002 테스트 완료 ===")
    
# STU-DAB-02-003
def test_course_page_with_invalid_classroom(dashboard_client,valid_headers,dash_params):
    logger.info("=== STU-DAB-02-003: 소속되지 않은 클래스 홈으로 한 과목의 학습 현황 조회 ===")
    
    endpoint = f"/student/{dash_params['student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": dash_params["invalid_classroom_id"],
            "course_id" : dash_params["course_id"],
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-02-003 테스트 완료 ===")
    
# STU-DAB-02-004
def test_course_page_with_invalid_student(dashboard_client,valid_headers,dash_params):
    logger.info("=== STU-DAB-02-004: 유효하지 않은 student id로 한 과목의 학습 현황 조회 ===")
    
    endpoint = f"/student/{dash_params['invalid_student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-02-004 테스트 완료 ===")
    
# STU-DAB-02-005
def test_course_page_with_invalid_course(dashboard_client,valid_headers,dash_params):
    logger.info("=== STU-DAB-02-005: 소속된 클래스 홈과 맞지 않는 과목의 학습 현황 조회 ===")
    
    endpoint = f"/student/{dash_params['student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params={
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["invalid_course_id"],
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-02-005 테스트 완료 ===")
    
# STU-DAB-02-006
def test_course_page_delete_with_student_account(classroom_client,valid_headers,dash_params):
    logger.info("=== STU-DAB-02-006: 학생 권한으로 한 과목 학습 현황 삭제 ===")
    
    endpoint = f"/classroom/{dash_params['classroom_id']}/course/{dash_params['course_id']}"
    response = classroom_client.delete(
        endpoint,
        headers = valid_headers
    )
    body = response.json()
    
    try : 
        assert response.status_code == 403, "Step 1 실패: status_code != 403"
        logger.info("Step 1 성공: 예상대로 403 Forbidden 반환됨")
        assert "permission" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-02-006 테스트 완료 ===")
    
#------------------- 테스트 시나리오 STU-DAB-03 : 학습 대시보드 메뉴의 수업별 학습 현황과 관련된 API 테스트 ------------------------------------
# STU-DAB-03-001
def test_lecture_learning_page_success(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-03-001: 수업 선택 후 학습 현황 페이지 정상 조회 ===")
    
    endpoint = f"/lecture/{dash_params['lecture_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "elice_course_id" : dash_params["course_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 200, "Step 1 실패: status_code != 200"
        logger.info("Step 1 성공: 예상대로 200 OK 반환됨")
        assert body["lecture"]["id"] == int(dash_params["lecture_id"]), "Step 2 실패: lecture id 불일치"
        logger.info("Step 2 성공: 올바른 lecture id 반환됨")
        assert len(body["lecture"]["title"]) > 0, "Step 3 실패: 수업 title 데이터 존재하지 않음"
        logger.info("Step 3 성공: 수업 title 데이터 존재")
        assert len(body["learning_progress"]) > 0, "Step 4 실패: learning_progress 데이터 존재하지 않음"
        logger.info("Step 4 성공: learning_progress 데이터 존재")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-03-001 테스트 완료 ===")
    
# STU-DAB-03-002
def test_lecture_page_with_invalid_token(dashboard_client, invalid_headers, dash_params) :
    logger.info("=== STU-DAB-03-002: 만료된 토큰으로 수업 현황 페이지 조회 ===")
    
    endpoint = f"/lecture/{dash_params['lecture_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = invalid_headers,
        params= {
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "elice_course_id" : dash_params["course_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 403, "Step 1 실패: status_code != 403"
        logger.info("Step 1 성공: 예상대로 403 Forbidden 반환됨")
        assert "permission" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-03-002 테스트 완료 ===")
    
# STU-DAB-03-003
def test_lecture_page_with_invalid_classroom(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-03-003: 소속되지 않은 클래스의 수업 현황 페이지 조회 ===")
    
    endpoint = f"/student/{dash_params['student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "classroom_id": dash_params["invalid_classroom_id"],
            "course_id" : dash_params["course_id"],
            "lecture_id" : dash_params["lecture_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-03-003 테스트 완료 ===")
    
# STU-DAB-03-004
def test_lecture_page_with_invalid_student_id(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-03-004: 유효하지 않은 student id로 수업 현황 페이지 조회 ===")
    
    endpoint = f"/student/{dash_params['invalid_student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "lecture_id" : dash_params["lecture_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-03-004 테스트 완료 ===")
    
# STU-DAB-03-005
def test_lecture_page_with_invalid_lecture_id(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-03-005: 과목과 매칭되지 않는 수업 현황 페이지 조회 ===")
    
    endpoint = f"/student/{dash_params['student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "lecture_id" : dash_params["invalid_lecture_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-03-005 테스트 완료 ===")
    
# STU-DAB-03-006
def test_lecture_page_with_no_course_id(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-03-006: 수업 현황 페이지 조회 시 필수 파라미터인 course_id 누락 ===")
    
    endpoint = f"/student/{dash_params['student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "classroom_id": dash_params["invalid_classroom_id"],
            "lecture_id" : dash_params["lecture_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-03-006 테스트 완료 ===")
    
#-------------------- 테스트 시나리오 STU-DAB-04 : 학습 대시보드 메뉴의 챕터 테스트 현황과 관련된 API 테스트 ------------------------------------
# STU-DAB-04-001
def test_chapter_test_page_success(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-04-001: 챕터 테스트 선택 후 학습 현황 페이지 정상 조회 ===")
    
    endpoint = f"/lecture/{dash_params['chapter_test_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "elice_course_id" : dash_params["course_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 200, "Step 1 실패: status_code != 200"
        logger.info("Step 1 성공: 예상대로 200 OK 반환됨")
        assert body["lecture"]["id"] == int(dash_params["chapter_test_id"]), "Step 2 실패: 챕터 테스트 lecture id 불일치"
        logger.info("Step 2 성공: 올바른 챕터 테스트 lecture id 반환됨")
        assert "챕터 테스트" in body["lecture"]["title"], "Step 3 실패: 챕터 테스트 title 데이터 존재하지 않음"
        logger.info("Step 3 성공: 챕터 테스트 title 데이터 존재")
        assert len(body["learning_progress"]) > 0, "Step 4 실패: learning_progress 데이터 존재하지 않음"
        logger.info("Step 4 성공: learning_progress 데이터 존재")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-04-001 테스트 완료 ===")
    
# STU-DAB-04-002
def test_chapter_test_page_with_invalid_token(dashboard_client, invalid_headers, dash_params) :
    logger.info("=== STU-DAB-04-002: 만료된 토큰으로 챕터 테스트 학습 현황 페이지 조회 ===")
    
    endpoint = f"/lecture/{dash_params['chapter_test_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = invalid_headers,
        params= {
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "elice_course_id" : dash_params["course_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 403, "Step 1 실패: status_code != 403"
        logger.info("Step 1 성공: 예상대로 403 Forbidden 반환됨")
        assert "permission" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-04-002 테스트 완료 ===")
    
# STU-DAB-04-003
def test_chapter_test_page_with_invalid_classroom(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-04-003: 소속되지 않은 클래스의 챕터 테스트 학습 현황 페이지 조회 ===")
    
    endpoint = f"/student/{dash_params['student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "classroom_id": dash_params["invalid_classroom_id"],
            "course_id" : dash_params["course_id"],
            "lecture_id" : dash_params["chapter_test_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-04-003 테스트 완료 ===")
    
# STU-DAB-04-004
def test_chapter_test_page_with_invalid_student_id(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-04-004: 유효하지 않은 student id로 챕터 테스트 학습 현황 페이지 조회 ===")
    
    endpoint = f"/student/{dash_params['invalid_student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "lecture_id" : dash_params["chapter_test_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-04-004 테스트 완료 ===")
    
# STU-DAB-04-005
def test_chapter_test_page_with_invalid_lecture_id(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-04-005: 과목과 매칭되지 않는 챕터 테스트 학습 현황 페이지 조회 ===")
    
    endpoint = f"/student/{dash_params['student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "lecture_id" : dash_params["invalid_chapter_test_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-04-005 테스트 완료 ===")
    
# STU-DAB-04-006
def test_chapter_test_page_with_no_classroom_id(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-04-006: 챕터 테스트 현황 페이지 조회 시 필수 파라미터인 classroom_id 누락 ===")
    
    endpoint = f"/student/{dash_params['student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "course_id" : dash_params["course_id"],
            "lecture_id" : dash_params["chapter_test_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 422, "Step 1 실패: status_code != 422"
        logger.info("Step 1 성공: 예상대로 422 Unprocessable Entity 반환됨")
        assert "missing" in body["detail"][0]["type"], "Step 2 실패: 적절한 요청 거부 이유가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 이유가 제공됨")
        assert "classroom_id" in body["detail"][0]["loc"], "Step 3 실패: 누락된 파라미터 field id가 제공되지 않음"
        logger.info("Step 3 성공: 누락된 파라미터 field id가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-04-006 테스트 완료 ===")
    
#-------------------- 테스트 시나리오 STU-DAB-05 : 학습 대시보드 메뉴의 복습 테스트 현황과 관련된 API 테스트 ------------------------------------
# STU-DAB-05-001
def test_review_test_page_success(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-05-001: 복습 테스트 선택 후 학습 현황 페이지 정상 조회 ===")
    
    endpoint = f"/lecture/{dash_params['review_test_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "elice_course_id" : dash_params["course_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 200, "Step 1 실패: status_code != 200"
        logger.info("Step 1 성공: 예상대로 200 OK 반환됨")
        assert body["lecture"]["id"] == int(dash_params["review_test_id"]), "Step 2 실패: 복습 테스트 lecture id 불일치"
        logger.info("Step 2 성공: 올바른 복습 테스트 lecture id 반환됨")
        assert "복습 테스트" in body["lecture"]["title"], "Step 3 실패: 복습 테스트 title 데이터 존재하지 않음"
        logger.info("Step 3 성공: 복습 테스트 title 데이터 존재")
        assert len(body["learning_progress"]) > 0, "Step 4 실패: learning_progress 데이터 존재하지 않음"
        logger.info("Step 4 성공: learning_progress 데이터 존재")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-05-001 테스트 완료 ===")
    
# STU-DAB-05-002
def test_review_test_page_with_invalid_token(dashboard_client, invalid_headers, dash_params) :
    logger.info("=== STU-DAB-05-002: 만료된 토큰으로 복습 테스트 학습 현황 페이지 조회 ===")
    
    endpoint = f"/lecture/{dash_params['review_test_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = invalid_headers,
        params= {
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "elice_course_id" : dash_params["course_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 403, "Step 1 실패: status_code != 403"
        logger.info("Step 1 성공: 예상대로 403 Forbidden 반환됨")
        assert "permission" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-05-002 테스트 완료 ===")
    
# STU-DAB-05-003
def test_review_test_page_with_invalid_classroom(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-05-003: 소속되지 않은 클래스의 복습 테스트 학습 현황 페이지 조회 ===")
    
    endpoint = f"/student/{dash_params['student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "classroom_id": dash_params["invalid_classroom_id"],
            "course_id" : dash_params["course_id"],
            "lecture_id" : dash_params["review_test_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-05-003 테스트 완료 ===")
    
# STU-DAB-05-004
def test_review_test_page_with_invalid_student_id(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-05-004: 유효하지 않은 student id로 복습 테스트 학습 현황 페이지 조회 ===")
    
    endpoint = f"/student/{dash_params['invalid_student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "lecture_id" : dash_params["review_test_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-05-004 테스트 완료 ===")
    
# STU-DAB-05-005
def test_review_test_page_with_invalid_lecture_id(dashboard_client, valid_headers, dash_params) :
    logger.info("=== STU-DAB-05-005: 과목과 매칭되지 않는 복습 테스트 학습 현황 페이지 조회 ===")
    
    endpoint = f"/student/{dash_params['student_id']}"
    response = dashboard_client.get(
        endpoint,
        headers = valid_headers,
        params= {
            "classroom_id": dash_params["classroom_id"],
            "course_id" : dash_params["course_id"],
            "lecture_id" : dash_params["invalid_review_test_id"]
        }
    )
    body = response.json()
    
    try : 
        assert response.status_code == 409, "Step 1 실패: status_code != 409"
        logger.info("Step 1 성공: 예상대로 409 Conflict 반환됨")
        assert "model" in body["message"], "Step 2 실패: 적절한 요청 거부 메시지가 제공되지 않음"
        logger.info("Step 2 성공: 적절한 요청 거부 메시지가 제공됨")
    except AssertionError as e:
        logger.error(f"❌ 테스트 실패 : {e}")
        raise
    
    logger.info("=== STU-DAB-05-005 테스트 완료 ===")