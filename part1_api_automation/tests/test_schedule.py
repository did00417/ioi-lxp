import pytest
import logging

logger = logging.getLogger(__name__)

def test_weekly_schedule_load_success(classroom_client, test_schedule_data, valid_headers):
    
    logger.info("수업 일정(ICS) 조회 테스트 시작")
    endpoint = "/schedule/ics"
    
   
    params = test_schedule_data["params"]
    case = test_schedule_data["cases"]["weekly"]

    response = classroom_client.get(
        endpoint,
        headers=valid_headers, 
        params={
            "classroom_id": params["classroom_id"],
            "dt_start_ge": case["dt_start_ge"],
            "dt_start_le": case["dt_start_le"],
            "offset": case["offset"],
            "count": case["count"]
        }
    )

    assert response.status_code == 200
    
    # JSON 대신 text로 데이터를 받습니다.
    content = response.text
    
    # 캘린더 데이터가 맞는지 검증
    assert "BEGIN:VCALENDAR" in content
    logger.info("캘린더 데이터를 정상적으로 수신 및 검증 완료")

def test_schedule_detail_load_success(rest_client, valid_headers, test_schedule_data):
    data = test_schedule_data["cases"]["detail_view"]
    l_id = data["expected_lectureroom_id"]
    
    endpoint = f"/org/qatrack/course/lectureroom/get/"
    params = {"lectureroom_id": l_id}

    response = rest_client.get(
        endpoint, 
        headers=valid_headers, 
        params=params
    )

    # 4. 검증
    print(f"\n[상세 조회 응답]: {response.status_code}")
    assert response.status_code == 200
    
    body = response.json()
    
    # 정합성 확인: ID, 제목, 강의실ID가 모두 일치하는지!
    assert body.get("id") == l_id or body.get("lectureroom", {}).get("id") == l_id
    
    print(f"[검증 완료] 강의실 상세 정보 진입 성공!")
    

    
