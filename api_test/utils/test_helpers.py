import logging

logger = logging.getLogger(__name__)

def assert_success(response):
    """200 OK 응답을 검증하고 JSON 바디를 반환합니다."""
    assert response.status_code == 200, f"Step 실패 : 예상 200, 실제 {response.status_code}"
    logger.info("Step 성공: 예상대로 200 OK 반환됨")
    return response.json()

def assert_error(response, expected_status, expected_keyword):
    """에러 응답(4xx)의 상태 코드와 에러 키워드를 한 번에 검증합니다."""
    assert response.status_code == expected_status, f"상태 코드 오류: 예상 {expected_status}, 실제 {response.status_code}"
    logger.info(f"Step 성공: 예상대로 {expected_status} 에러 반환됨")
    
    body = response.json()
    if expected_status == 422:
        # 422 Validation Error 구조 대응
        error_detail = str(body.get("detail", []))
        assert expected_keyword in error_detail, f"Step 실패 : '{expected_keyword}' 키워드가 에러 상세(detail)에 없음"
    else:
        # 일반적인 403, 409 등의 에러 구조 대응
        error_msg = (
            str(body.get("message", "")) +
            str(body.get("detail", "")) +
            str(body.get("code", "")) +
            str(body.get("fail_code", ""))
        )
        assert expected_keyword in error_msg, f"Step 실패 : '{expected_keyword}' 키워드가 에러 메시지(message)에 없음"
        
    logger.info(f"Step 성공: 적절한 요청 거부 메시지('{expected_keyword}')가 제공됨")
    
def assert_id_match(actual_id, expected_id, target_name="ID"):
    """응답받은 ID가 요청한 ID와 일치하는지 검증합니다."""
    assert int(actual_id) == int(expected_id), f"Step 실패 : {target_name} 불일치 - 기대값: {expected_id}, 실제값: {actual_id}"
    logger.info(f"Step 성공: 올바른 {target_name}({actual_id}) 반환됨")

def assert_progress_exists(progress_data):
    """학습 진행도(learning_progress) 데이터가 존재하는지 검증합니다."""
    assert len(progress_data) > 0, "Step 실패 : learning_progress 데이터가 존재하지 않음"
    logger.info("Step 성공: learning_progress 데이터 정상 존재")

def assert_title_contains(actual_title, expected_keyword):
    """제목(title)에 특정 키워드가 포함되어 있는지 검증합니다."""
    assert expected_keyword in actual_title, f"Step 실패 : title 데이터 오류 - '{expected_keyword}'가 포함되지 않음 (실제: {actual_title})"
    logger.info(f"Step 성공: title에 '{expected_keyword}' 포함 확인")
    
def assert_valid_course_ids(actual_items, valid_ids_set):
    """리스트 내의 course_id들이 유효한 ID 목록에만 속하는지 검증합니다."""
    invalid_ids = [item["course"]["id"] for item in actual_items if item["course"]["id"] not in valid_ids_set]
    assert not invalid_ids, f"Step 실패 : 유효하지 않은 course_id 발견 - {invalid_ids}"
    logger.info("Step 성공: 요청한 페이지의 과목 리스트 정상 반환됨")
    
def assert_success_and_empty_list(response):
    """200 OK 응답을 검증하고, 반환된 데이터가 빈 배열([])인지 확인합니다."""
    body = assert_success(response)  # 기존에 만든 200 OK 검증 함수 재사용
    assert body == [], f"Step 실패 : 빈 배열([])을 기대했으나 데이터가 존재함"
    logger.info("Step 성공: 예상대로 빈 배열([]) 반환됨")
    return body

def assert_status_code(result_status, exp_status, step=""):
    """응답 코드가 기대한 응답 코드와 일치하는지 확인합니다."""
    assert result_status == exp_status, f"Step {step} 실패: {exp_status} 기대했으나 {result_status} 반환됨"
    logger.info(f"Step {step} 성공: {exp_status} 반환됨")

def assert_response_match(response_data, expected_data, step=""):
    assert str(expected_data) in str(response_data), f"Step {step} 실패: '{expected_data}' 미포함 (실제값: {response_data})"
    logger.info(f"Step {step} 성공: '{response_data}' 확인 완료")

def assert_business_code(result, exp_res, step=""):
    assert result.get("status_code") == exp_res["status_code"], f"Step {step} 실패(비즈니스 코드 불일치): {result.get('status_code')}"
    logger.info(f"Step {step} 성공: 예상된 실패 코드({exp_res['status_code']}) 확인 완료")

def assert_business_status(result, exp_res, step=""):
    assert result.get("status") == exp_res, f"Step {step} 실패(Status 불일치): {result.get('status')}"
    logger.info(f"Step {step} 성공: 예상된 실패 상태({exp_res}) 확인 완료")

def assert_equal_value(res_val, exp_val, key, step="", ):
    assert res_val == exp_val, f"Step {step} 실패: {key} 불일치, 기대값({exp_val}), 결과값({res_val})"
    logger.info(f"Step {step} 성공: {key} 일치 ({res_val})")
    
def assert_success_text(response):
    # ICS 텍스트 응답용
    assert response.status_code == 200, \
        f"상태 코드 오류: 예상 200, 실제 {response.status_code}"
    logger.info("Step 성공: 예상대로 200 OK 반환됨 (text)")
    return response.text

def assert_business_error1(response, expected_status, expected_fail_code):
    #_result 구조 Business Error 검증
    body = response.json()
    result = body.get("_result", {})
    assert result.get("status_code") == expected_status, f"Business 상태코드 오류: 예상 {expected_status}, 실제 {result.get('status_code')}"
    assert body.get("fail_code") == expected_fail_code, f"fail_code 오류: 예상 {expected_fail_code}, 실제 {body.get('fail_code')}"
    logger.info(f"Step 성공: Business Error {expected_status} / {expected_fail_code}"
)