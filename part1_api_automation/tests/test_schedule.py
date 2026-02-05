import pytest

def test_weekly_schedule_load_success(classroom_client, test_schedule_data, valid_headers):
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
    assert "VERSION:2.0" in content
    
    print(f"\n[성공] 캘린더 데이터를 정상적으로 수신했습니다.")
    print(f"[데이터 샘플]\n{content[:200]}...") 