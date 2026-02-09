import pytest
import logging


logger = logging.getLogger(__name__)

# [LDB_INIT_001] 주간 단위 일정 데이터 호출 및 출력 검증
def test_weekly_schedule_load_success(classroom_client, valid_headers, schedule_params, weekly_case):
    
    logger.info("수업 일정(ICS) 조회 테스트 시작")
    
    response = classroom_client.get(
        "/schedule/ics",
        headers=valid_headers,
        params={
            "classroom_id": schedule_params["classroom_id"],
            "dt_start_ge": weekly_case["dt_start_ge"],
            "dt_start_le": weekly_case["dt_start_le"],
            "offset": weekly_case["offset"],
            "count": weekly_case["count"]
        }
    )
    assert response.status_code == 200
    
    # JSON 대신 text로 데이터를 받습니다.
    content = response.text
    
    # 캘린더 데이터가 맞는지 검증
    assert "BEGIN:VCALENDAR" in content
    logger.info("캘린더 데이터를 정상적으로 수신 및 검증 완료")

# [LDB_INIT_002] 강의실/회의실 상세 페이지 진입 정합성
def test_schedule_detail_load_success(rest_client, valid_headers, test_schedule_data):
    
    logger.info("강의실 상세 정보 조회 테스트 시작")
    
    data = test_schedule_data["cases"]["detail_view"]
    l_id = data["expected_lectureroom_id"]
    expected_title = data["expected_title"] # 바꾼 제목을 검증하기 위해 가져옴
    
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
    
    actual_id = body.get("id") or body.get("lectureroom", {}).get("id")
    assert actual_id == l_id, f"ID 불일치! 실제: {actual_id}, 예상: {l_id}"
    
    # 정합성 확인: 제목 일치
    actual_title = body.get("title") or body.get("lectureroom", {}).get("title")
    assert actual_title == expected_title, f"제목 불일치! 실제: {actual_title}, 예상: {expected_title}"
    
    print(f"[검증 완료] 강의실 상세 정보 진입 성공! (ID: {actual_id}, 제목: {actual_title})")
    logger.info(f"상세 정보 정합성 검증 완료: {actual_title}")
  
# [LDB_INIT_003] 더보기(+N more)' 확장 데이터 로드 검증   
def test_schedule_all_data_loaded(classroom_client, valid_headers, schedule_params, weekly_case):
    logger.info("전체 데이터 일괄 로드 검증 테스트 시작")
    


    response = classroom_client.get(
        "/schedule/ics",
        headers=valid_headers,
        params={
            "classroom_id":schedule_params["classroom_id"],
            "dt_start_ge": weekly_case["dt_start_ge"],
            "dt_start_le": weekly_case["dt_start_le"],
            "offset": 0,
            "count": 100 
        }
    )

    assert response.status_code == 200
    content = response.text

    # 1. 일정 단위인 'VEVENT'가 몇 개 들어있는지 세어보기
    event_count = content.count("BEGIN:VEVENT")
    logger.info(f"조회된 전체 일정 개수: {event_count}개")
    
    # 최소 1개 이상의 일정이 있어야 함
    assert event_count > 0

    # 2. '더보기'를 눌러야 나오는 특정 일정이 포함되어 있는지 확인
    expected_hidden_title = "🦁 [코치]이상엽 메인코치님 상주 강의실" 
    if expected_hidden_title in content:
        logger.info(f"숨겨진 일정 '{expected_hidden_title}'이(가) 응답에 포함되어 있습니다.")
    else:
        logger.warning("특정 일정을 찾지 못했습니다. 제목을 다시 확인해주세요.")

    assert "BEGIN:VCALENDAR" in content
    
def test_schedule_date_update_on_move(classroom_client, valid_headers, schedule_params, test_schedule_data):
    logger.info("증분 이동(12월) 시 날짜 파라미터 갱신 및 데이터 로드 테스트 시작")
    
    # 1. 12월 이동 케이스 데이터 가져오기
    dec_case = test_schedule_data["cases"]["december_move"]
    
    response = classroom_client.get(
        "/schedule/ics",
        headers=valid_headers,
        params={
            "classroom_id": schedule_params["classroom_id"],
            "dt_start_ge": dec_case["dt_start_ge"], 
            "dt_start_le": dec_case["dt_start_le"], 
            "offset": 0,
            "count": 40
        }
    )

    # 3. 검증
    assert response.status_code == 200
    content = response.text
    
    # 응답 데이터에 성탄절이 포함되어 있는지 확인
    assert dec_case["expected_event_keyword"] in content
    
    # 12월 날짜 정보 확인
    assert "202512" in content or "202601" in content

    logger.info(f"검증 성공: 12월 이동 시 파라미터가 정상 반영되어 '{dec_case['expected_event_keyword']}' 데이터를 수신했습니다.") 
    

    
