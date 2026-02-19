import pytest
import json
import logging
from utils.test_helpers import assert_success, assert_equal_value, assert_title_contains, assert_status_code, assert_success, assert_business_status, assert_business_code, assert_equal_value, assert_id_match

logger = logging.getLogger(__name__)
# ---------------- STU_BOARD_01 ----------------

def test_get_article_list(rest_client, valid_headers, board_id, test_board_data):
    """STU_BOARD_01-001: 게시글 목록 조회"""
    logger.info("=== STU_BOARD_01-001: 게시글 목록 조회 시작 ===")
    query = test_board_data["queries"]["article_list"]
    logger.debug(f"파라미터: {query}")
    
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/list/",
        headers=valid_headers,
        params={**query, "board_id": board_id}
    )
    
    body = assert_success(response)
    
    assert_equal_value("board_articles" in body, True, "게시글 목록 필드 포함 여부")
    logger.info("게시글 목록 조회 완료")

@pytest.mark.parametrize("query_key, sort_field", [
    ("sort_latest", "created"),
    ("sort_likes", "like_count")
])
def test_articles_sorting_latest_likes(classroom_client, valid_headers, classroom_id, test_board_data,
                                      query_key, sort_field):
    """
    STU_BOARD_01-002: 게시글 최신순 정렬 조회
    STU_BOARD_01-003: 게시글 좋아요순 정렬 조회
    """
    logger.info(f"=== 게시글 정렬 조회 테스트 시작 ===")

    query = test_board_data["queries"][query_key]
    logger.debug(f"요청 쿼리: {query}")

    response = classroom_client.get(
        endpoint=f"/classroom/{classroom_id}/article",
        headers=valid_headers,
        params=query
    )
    
    articles = assert_success(response)
    logger.info(f"조회된 게시글 수: {len(articles)}")

    if len(articles) >= 2:
        for i in range(len(articles) - 1):
            assert articles[i][sort_field] >= articles[i+1][sort_field], \
                f"정렬 오류: {articles[i][sort_field]} < {articles[i+1][sort_field]}"
    else:
        logger.warning("검증 데이터 부족")

@pytest.mark.parametrize("keyword_key, expected_count_min", [
    ("valid", 1),  # 1. 검색 결과가 있어야 하는 케이스
    ("invalid", 0)    # 2. 검색 결과가 없어야 하는 케이스
])
def test_get_article_list_by_filter(
    rest_client,
    valid_headers,
    board_id,
    keyword_key,
    expected_count_min,
    test_board_data
):
    """
    STU_BOARD_01-004: 제목 키워드 검색
    STU_BOARD_01-005: 제목 키워드 일치하는 검색 결과 없음
    """
    
    keyword = test_board_data["search_keywords"][keyword_key]
    query = test_board_data["queries"]["article_list"]
    
    logger.info(f"=== 제목 키워드 검색 테스트 시작 ===")
    
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/list/",
        headers=valid_headers,
        params={**query, "board_id": board_id, "filter_title": keyword}
    )
    body = assert_success(response)
    articles = body.get("board_articles", [])
    
    article_count = body.get("board_article_count", 0)
    logger.info(f"검색 결과 수: {len(articles)} (기대 최소값: {expected_count_min})")
    
    if expected_count_min > 0:
        # 결과가 있어야 하는 경우
        assert len(articles) >= expected_count_min, f"'{keyword}' 검색 결과 부족"
        # 헬퍼 활용: 제목 키워드 포함 검증
        for article in articles:
            assert_title_contains(article['title'], keyword.replace("%", ""))
    else:
        # 헬퍼 활용: 결과 0건 검증
        assert_equal_value(len(articles), 0, "검색 결과 0건 확인")
        assert_equal_value(body.get("board_article_count"), 0, "카운트 0 확인")

# ---------------- STU_BOARD_02 ----------------

def test_create_article_success(rest_client, valid_headers, classroom_id, create_article_data):
    """STU_BOARD_02_001: 게시글 작성"""
    logger.info("=== STU_BOARD_02_001: 게시글 작성 테스트 시작 ===")
    
    payload = {
        **create_article_data,
        "classroom_id": classroom_id
    }
    
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        form_data=payload
    )

    body = assert_success(response)
    assert_business_status(body["_result"], "ok", step="게시글 작성 완료")
    
    article_id = body.get("board_article_id")
    assert_equal_value(bool(article_id), True, "게시글 ID 생성 여부")
    
    delete_response = rest_client.post(
        endpoint="/org/qatrack/board/article/delete/",
        headers=headers,
        form_data={"board_article_id": article_id}
    )
    
    assert_business_status(delete_response.json()["_result"], "ok", step="테스트 데이터 정리")

@pytest.mark.parametrize("case_key, expected_status", [
    ("classroom_id_missing", 400),
    ("title_missing", 400),
    ("content_missing", 400)
])
def test_create_article_fail_by_missing_param(
    rest_client, 
    valid_headers, 
    classroom_id, 
    create_article_data, 
    case_key,
    expected_status,
    test_board_data
):
    """STU_BOARD_02_002: 게시글 작성 필수값 누락 검증"""
    case_data = test_board_data["article_data"]["create_fail_cases"][case_key]
    missing_key = case_data["missing_key"]
    
    logger.info(f"=== STU_BOARD_02_002: 필수값 누락 검증 시작 (누락 키: {case_key}) ===")
    payload = {
        **create_article_data,
        "classroom_id": classroom_id
    }
    payload.pop(missing_key, None) 

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=valid_headers,
        form_data=payload
    )

    body = response.json()
    assert_business_status(body["_result"], "fail", step=f"{missing_key} 누락 케이스")
    assert_business_code(body["_result"], {"status_code": expected_status}, step="에러 코드 검증")
    assert_equal_value(body.get("board_article_id"), None, "ID 미생성 확인")
        
def test_get_linked_courses(classroom_client, valid_headers, classroom_id, test_board_data):
    """STU_BOARD_02_003: 게시글 작성 연결 과목 조회"""
    logger.info("=== STU_BOARD_02_003: 연결 과목 조회 시작 ===")

    endpoint = f"/classroom/{classroom_id}/course"
    query = test_board_data["queries"]["course_query"]

    response = classroom_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params=query
    )

    courses = assert_success(response)
    
    assert_equal_value(isinstance(courses, list), True, "응답 데이터 리스트 형식 여부")
    logger.info(f"조회된 과목 수: {len(courses)}")
    
    if len(courses) > 0:
        # 첫 번째 과목에 필수 필드가 있는지 확인
        assert_equal_value("id" in courses[0], True, "과목 ID 필드 존재 여부")
        assert_equal_value("title" in courses[0], True, "과목 제목 필드 존재 여부")
        logger.debug(f"샘플 데이터 확인: {courses[0]}")

@pytest.mark.parametrize("case_key", [
    "valid_article", 
    "not_found_article"
])
def test_get_article_detail_cases(
    rest_client, 
    valid_headers,
    case_key,
    test_board_data,
    created_article_id
):
    """
    STU_BOARD_02_004: 특정 게시글 조회
    STU_BOARD_02_005: 존재하지 않는 게시글 상세 조회
    """
    
    case_data = test_board_data["article_data"]["detail_cases"][case_key]
    article_id = created_article_id if case_key == "valid_article" else case_data["article_id"]
    
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/get/",
        headers=valid_headers,
        params={"board_article_id": article_id}
    )
    
    body = response.json()
    assert_business_status(body["_result"], case_data["expected_result"], step=f"상세 조회({case_key})")
    assert_business_code(body["_result"], {"status_code": case_data["expected_status"]}, step="상태 코드 검증")
    
    if case_data["expected_result"] == "ok":
        # 응답받은 ID가 요청한 ID와 일치하는지 확인
        assert_id_match(body["board_article"]["id"], article_id, target_name="게시글 ID")
    else:
        # 실패 코드 키워드 포함 여부 확인
        assert_equal_value(body.get("fail_code"), case_data["expected_fail_code"], "실패 코드 일치 확인")

@pytest.mark.parametrize("case_key", [
    "others_private_a", 
    "others_private_b"
])
@pytest.mark.xfail(reason="보안 버그: 타인의 비밀글이 권한 체크 없이 조회됨")
def test_get_others_private_article_security_bug(rest_client, valid_headers, case_key, test_board_data):
    """
    STU_BOARD_02_006: 타인 비밀글 조회
    기대 결과: status 'fail', fail_code 'insufficient_permission' 반환하며 차단되어야 함
    현재 현상: 200 OK와 함께 게시글 내용이 반환됨
    """
    case_data = test_board_data["article_data"]["security_cases"][case_key]
    article_id = case_data["article_id"]
    description = case_data["description"]
    
    logger.info(f"=== STU_BOARD_02_006 타인 비밀글 테스트 시작 ({case_key}: {description}) ===")
    
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/get/",
        headers=valid_headers,
        params={"board_article_id": article_id}
    )
    
    body = response.json()
    
    if body["_result"]["status"] == "ok":
        logger.critical(f"🔥 보안 경고: 비밀글(ID: {article_id})이 권한 없이 조회되었습니다!")

    # 기대 결과(실패) 검증
    # 기대값: status 'fail', status_code 409(혹은 403), fail_code 'insufficient_permission'
    assert_business_status(body["_result"], "fail", step="비밀글 접근 차단 확인")
    
    # 403 혹은 409 둘 중 하나면 통과
    assert_business_code(body["_result"], {"status_code": [403, 409]}, step="보안 에러 코드 검증")
    
    # 구체적인 에러 키워드(fail_code) 검증
    assert_equal_value(body.get("fail_code"), "insufficient_permission", "권한 부족 에러코드 일치 여부")

def test_update_article_success(rest_client, valid_headers, classroom_id, created_article_id, test_board_data):
    """STU_BOARD_02_007: 게시글 수정"""
    logger.info("=== STU_BOARD_02_007: 게시글 수정 테스트 시작 ===")

    headers = valid_headers.copy()
    headers.pop("Content-Type", None)
    
    edit_content = test_board_data["edit_article"]["update_payload"]
    update_payload = {
        "board_article_id": created_article_id,
        **edit_content,
        "classroom_id": classroom_id
    }
    
    response = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        form_data=update_payload
    )

    body = assert_success(response)
    
    assert_business_status(body["_result"], "ok", step="게시글 수정 요청")
    assert_business_code(body["_result"], {"status_code": 200}, step="수정 응답 코드 확인")

    assert_id_match(body.get("board_article_id"), created_article_id, target_name="수정 게시글 ID")
    
def test_update_others_article_fail(rest_client, valid_headers, classroom_id, test_board_data):
    """STU_BOARD_02_008: 타인 게시글 수정 시도"""
    logger.info("=== STU_BOARD_02_008: 타인 게시글 수정 시도 테스트 시작 ===")

    edit_data = test_board_data["edit_others_article"]
    article_id = edit_data["board_article_id"]
    
    payload = {
        "board_article_id": article_id,
        **edit_data["update_payload"],
        "classroom_id": classroom_id
    }
    
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        form_data=payload
    )

    body = response.json()
    logger.debug(f"타인 글 수정 시도 응답: {body}")

    assert_business_status(body["_result"], "fail", step="타인 게시글 수정 차단")
    assert_business_code(body["_result"], {"status_code": 400}, step="에러 코드 검증")
    assert_equal_value(body.get("fail_code"), "resource_not_found", "실패 코드(fail_code) 일치 여부")

def test_delete_article_success(rest_client, valid_headers, created_article_id):
    """STU_BOARD_02_009: 게시글 삭제"""
    logger.info("=== STU_BOARD_02_009: 게시글 삭제 테스트 시작 ===")

    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/delete/",
        headers=headers,
        form_data={"board_article_id": created_article_id}
    )

    body = assert_success(response)
    assert_business_status(body["_result"], "ok", step="게시글 삭제 요청")
    assert_business_code(body["_result"], {"status_code": 200}, step="삭제 완료 응답 확인")

@pytest.mark.xfail(reason="보안 버그: 타인의 게시글이 권한 체크 없이 삭제됨")
def test_delete_others_article_xfail(rest_client, valid_headers, board_id, test_board_data):
    """
    STU_BOARD_02_010: 타인 게시글 삭제 시도
    기대 결과: status 'fail', fail_code 'insufficient_permission' 반환하며 차단되어야 함
    현재 현상: 200 OK와 함께 타인의 게시글이 삭제됨 (보안 취약점)
    """
    logger.info("=== STU_BOARD_02_010 타인 게시글 삭제 시도 ===")

    # 1. 게시글 목록 조회
    query = test_board_data["queries"]["article_list"]
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/list/",
        headers=valid_headers,
        params={**query, "board_id": board_id}
    )
    
    body = assert_success(response)
    articles = body.get("board_articles", [])

    # 2. JSON에서 설정한 타인 리스트 가져오기
    others_list = test_board_data["security_test"]["others_list"]
    
    # 목록 중 작성자 이름이 others_list에 포함된 게시글 찾기
    target_article = next(
        (a for a in articles if a.get("user", {}).get("fullname") in others_list), 
        None
    )

    if not target_article:
        logger.warning("테스트 가능한 타인이 작성한 게시글이 목록에 없어 테스트를 건너띔.")
        pytest.skip("테스트 가능한 타인의 게시글이 목록에 없습니다.")

    target_id = target_article.get("id") 
    target_writer = target_article.get("user", {}).get("fullname")
    
    logger.info(f"타겟 게시글 확인 - ID: {target_id}, 작성자: {target_writer}, 제목: {target_article.get('title')}")

    # 3. 삭제 시도
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    # 현재 로그인된 유효 토큰으로 타인의 글 삭제 요청
    response = rest_client.post(
        endpoint="/org/qatrack/board/article/delete/",
        headers=headers,
        form_data={"board_article_id": target_id}
    )

    res_data = response.json()

    if body["_result"]["status"] == "ok":
        logger.critical(f"보안 경고: 타인의 게시글(ID: {target_id})이 권한 없이 삭제됨!")

    # 실패해야 정상 (삭제가 성공하면 AssertionError 발생 -> xfail 처리)
    assert_business_status(res_data["_result"], "fail", step="타인 게시글 삭제 차단")
    assert_business_code(res_data["_result"], {"status_code": [403, 409]}, step="보안 에러 코드 검증")
    assert_equal_value(res_data.get("fail_code"), "insufficient_permission", "권한 부족 에러코드 일치 여부")
    
    logger.info("=== STU_BOARD_02_010: 타인 게시글 삭제 시도 종료 ===")

def test_create_article_max_title_over_fail(rest_client, valid_headers, classroom_id, test_board_data):
    """STU_BOARD_02_011: 제목 최대 글자수 초과 테스트"""
    logger.info("=== STU_BOARD_02_011: 제목 최대 글자수 초과 테스트 시작 ===")

    invalid_data = test_board_data["invalid_articles"]["max_title_over"]
    
    payload = {
        "classroom_id": classroom_id,
        **invalid_data
    }

    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        form_data=payload
    )

    body = response.json()
    logger.debug(f"서버 응답: {body}")

    assert_business_status(body["_result"], "fail", step="글자수 제한 검증")
    assert_business_code(body["_result"], {"status_code": 400}, step="에러 코드 400 확인")
    assert_equal_value(body.get("fail_code"), "invalid_parameter", "실패 코드(fail_code) 일치 여부")

# ---------------- STU_BOARD_03 ----------------

def test_article_like_add_and_delete_flow(rest_client, valid_headers, created_article_id):
    """
    STU_BOARD_03-001: 게시글 좋아요 정상 동작
    STU_BOARD_03-002: 게시글 좋아요 취소 확인
    """
    logger.info("=== STU_BOARD_03-001,002: 좋아요 추가/취소 테스트 시작 ===")
    
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    # 좋아요 추가
    logger.info("단계 1: 좋아요 추가 요청")
    like_add_res = rest_client.post(
        endpoint="/org/qatrack/board/article/like/add/",
        headers=headers,
        form_data={"board_article_id": created_article_id}
    )
    
    body_add = assert_success(like_add_res)
    assert_business_status(body_add["_result"], "ok", step="게시글 좋아요 추가")

    # 좋아요 취소
    logger.info("단계 2: 좋아요 취소 요청")
    like_del_res = rest_client.post(
        endpoint="/org/qatrack/board/article/like/delete/",
        headers=headers,
        form_data={"board_article_id": created_article_id}
    )
    
    body_del = assert_success(like_del_res)
    assert_business_status(body_del["_result"], "ok", step="게시글 좋아요 취소")

@pytest.mark.parametrize("data_key, expected_status, expected_code, expected_fail_code", [
    ("valid_comment", "ok", 200, None),
    ("invalid_article_comment", "fail", 400, "resource_not_found")
])
def test_create_comment(rest_client, valid_headers, test_board_data, created_article_id,
                                    data_key, expected_status, expected_code, expected_fail_code):
    """
    STU_BOARD_03-003: 댓글 작성 가능 확인
    STU_BOARD_03-004: 존재하지 않는 게시글 댓글 작성
    """
    logger.info(f"=== 댓글 작성 테스트 시작 ===")
    
    payload = test_board_data["comment_data"][data_key].copy()
    
    if data_key == "valid_comment":
        payload["board_article_id"] = created_article_id

    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/comment/edit/",
        headers=headers,
        form_data=payload
    )

    body = response.json()
    assert_business_status(body["_result"], expected_status, step=f"댓글 작성({data_key})")
    assert_business_code(body["_result"], {"status_code": expected_code}, step="응답 코드 검증")

    if expected_fail_code:
        assert_equal_value(body.get("fail_code"), expected_fail_code, "에러 코드 일치 확인")
    else:
        assert_equal_value("article_comment_id" in body, True, "댓글 ID 생성 확인")

def test_comment_like_add_and_delete(rest_client, valid_headers, created_comment_id):
    """
    STU_BOARD_03-005: 댓글 좋아요 정상 동작
    STU_BOARD_03-006: 댓글 좋아요 취소 확인
    """
    logger.info("=== 댓글 좋아요 및 취소 테스트 시작 (ID: {created_comment_id}) ===")
    
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    logger.info("단계 1: 댓글 좋아요 추가 요청")
    like_add_res = rest_client.post(
        endpoint="/org/qatrack/board/article/comment/like/add/",
        headers=headers,
        form_data={"article_comment_id": created_comment_id}
    )
    
    assert_business_status(assert_success(like_add_res)["_result"], "ok", step="댓글 좋아요 추가")

    # 2. 댓글 좋아요 취소
    logger.info("단계 2: 댓글 좋아요 취소 요청")
    like_del_res = rest_client.post(
        endpoint="/org/qatrack/board/article/comment/like/delete/",
        headers=headers,
        form_data={"article_comment_id": created_comment_id}
    )
    
    assert_business_status(assert_success(like_del_res)["_result"], "ok", step="댓글 좋아요 취소")

def test_comment_update_delete(rest_client, valid_headers, created_article_id, created_comment_id, test_board_data):
    """
    STU_BOARD_03-007: 댓글 수정 반영 확인
    STU_BOARD_03-008: 댓글 삭제 확인
    """
    logger.info(f"=== STU_BOARD_03-007,008: 댓글 수정, 삭제 테스트 시작 (ID: {created_comment_id}) ===")
    
    test_data = test_board_data["comment_data"]["update_delete_test"]
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    # 1. 댓글 수정
    logger.info("단계 1: 댓글 수정 요청")
    update_payload = {
        "board_article_id": created_article_id,
        "article_comment_id": created_comment_id,
        "content": test_data["update_content"]
    }
    
    update_res = rest_client.post(
        endpoint="/org/qatrack/board/article/comment/edit/",
        headers=headers,
        form_data=update_payload
    )
    
    assert_business_status(assert_success(update_res)["_result"], "ok", step="댓글 수정")

    # 2. 댓글 삭제
    logger.info("단계 2: 댓글 삭제 요청")
    delete_res = rest_client.post(
        endpoint="/org/qatrack/board/article/comment/delete/",
        headers=headers,
        form_data={"article_comment_id": created_comment_id}
    )
    
    assert_business_status(assert_success(delete_res)["_result"], "ok", step="댓글 삭제")

def test_get_comment_list_success(rest_client, valid_headers, test_board_data, created_article_id):
    """STU_BOARD_03-009: 특정 게시글 댓글 목록 조회"""
    logger.info("=== STU_BOARD_03-009: 댓글 목록 조회 테스트 시작 ===")

    params = test_board_data["comment_data"]["list_params"].copy()
    params["board_article_id"] = created_article_id
    logger.debug(f"조회 조건: {params}")

    response = rest_client.get(
        endpoint="/org/qatrack/board/article/comment/list/",
        headers=valid_headers,
        params=params
    )

    body = assert_success(response)
    assert_business_status(body["_result"], "ok", step="댓글 목록 조회")
    assert_equal_value(isinstance(body.get("article_comments"), list), True, "댓글 리스트 형식 확인")

@pytest.mark.parametrize("sort_key, expected_status, expected_code", [
    ("valid_desc", "ok", 200),
    ("valid_asc", "ok", 200),
    ("invalid_key", "fail", 400),
    ("invalid_order", "fail", 400),
    ("missing_field", "fail", 400)
])
def test_get_comment_list_sort_parametrize(rest_client, valid_headers, test_board_data,created_article_id,
                                           sort_key, expected_status, expected_code):
    """
    STU_BOARD_03-010: 댓글 최신순 정렬 조회
    STU_BOARD_03-011: 댓글 작성순 정렬 조회
    STU_BOARD_03-012: 댓글 정렬 비정상 입력 검증
    """
    logger.info(f"=== STU_BOARD_03-010,011,012 테스트 시작 ===")

    base_query = test_board_data["queries"]["article_list"] 
    sort_config = test_board_data["comment_data"]["sort_test"]
    sort_value = sort_config["cases"][sort_key]
    
    params = {
        **base_query, 
        "board_article_id": created_article_id,
        "sort_by": json.dumps(sort_value)
    }

    response = rest_client.get(
        endpoint="/org/qatrack/board/article/comment/list/",
        headers=valid_headers,
        params=params
    )

    body = response.json()
    assert_business_status(body["_result"], expected_status, step=f"정렬 테스트({sort_key})")
    assert_business_code(body["_result"], {"status_code": expected_code}, step="응답 코드 검증")

    if expected_status == "fail":
        assert_equal_value(body.get("fail_code"), "invalid_parameter", "에러 코드 일치 확인")