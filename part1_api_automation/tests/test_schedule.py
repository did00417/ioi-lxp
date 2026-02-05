import pytest


# 주간 일정 데이터 호출 및 출력 검증 테스트
def test_weekly_schedule_load_success(classroom_client, valid_headers, params):
    endpoint = "/schedule/ics"

    response = classroom_client.get(
        endpoint,
        headers=valid_headers,
        params={
            "classroom_id": params["classroom_id"],
            "dt_start_ge": "2026-01-17T15:00:00.000Z", # 시작 범위
            "dt_start_le": "2026-03-14T14:59:59.999Z", # 종료 범위
            "offset": 0,
            "count": 40
        }
    )
    
    #응답 검증
    body = response.json()
    assert response.status_code == 200
    assert "events" in body
    
    print(f"\n[성공] 조회된 일정 개수: {len(body['events'])}개")
    if len(body['events']) > 0:
        print(f"[데이터 샘플] 첫 번째 일정 제목: {body['events'][0].get('summary')}")