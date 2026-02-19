import pytest
import json
import logging

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
    
    if response.status_code != 200:
        logger.error(f"요청 실패! 상태 코드: {response.status_code} | 응답: {response.text}")
    
    assert response.status_code == 200

    body = response.json()
    assert "board_articles" in body, "응답에 게시글 목록(board_articles)이 포함되어 있지 않습니다."
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
    
    assert response.status_code == 200, f"조회 실패: {response.status_code}"
    articles = response.json()
    logger.info(f"조회된 게시글 수: {len(articles)}")

    if len(articles) >= 2:
        for i in range(len(articles) - 1):
            current_val = articles[i][sort_field]
            next_val = articles[i+1][sort_field]
            
            logger.debug(f"[{current_val} >= {next_val}")
            
            # 내림차순 검증 (최신순은 문자열 날짜 비교, 좋아요순은 숫자 비교)
            assert current_val >= next_val, f"정렬 오류 발견: {current_val} < {next_val}"
    else:
        logger.warning(f"검증할 게시글이 충분하지 않습니다. (현재 {len(articles)}개)")

    logger.info(f"=== 게시글 정렬 테스트 완료 ===")

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
    assert response.status_code == 200
    
    body = response.json()
    articles = body.get("board_articles", [])
    article_count = body.get("board_article_count", 0)
    logger.info(f"검색 결과 수: {len(articles)} (기대 최소값: {expected_count_min})")
    
    if expected_count_min > 0:
        # 결과가 있어야 하는 경우
        assert len(articles) >= expected_count_min, f"'{keyword}' 검색 결과가 없습니다."
        # 모든 결과에 키워드가 포함되어 있는지
        for article in articles:
            clean_keyword = keyword.replace("%", "") # % 제거 후 실제 텍스트만 비교
            assert clean_keyword in article['title'], f"제목에 '{clean_keyword}'가 포함되어 있지 않습니다: {article['title']}"
    else:
        # 결과가 없어야 하는 경우
        assert len(articles) == 0, f"'{keyword}' 검색 결과가 없어야 하는데 {len(articles)}개가 발견되었습니다."
        assert article_count == 0, "board_article_count가 0이 아닙니다."
    logger.info(f"'{keyword}' 검색 테스트 완료")

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

    assert response.status_code == 200, f"작성 실패: {response.status_code}"
    
    res_data = response.json()
    assert res_data["_result"]["status"] == "ok"
    
    article_id = res_data.get("board_article_id")
    logger.info(f"게시글 작성 성공! 생성된 ID: {res_data.get('board_article_id')}")
    assert article_id is not None, "게시글 ID가 생성되지 않았습니다."
    
    delete_response = rest_client.post(
        endpoint="/org/qatrack/board/article/delete/",
        headers=headers,
        form_data={"board_article_id": article_id}
    )
    
    delete_res_data = delete_response.json()
    assert delete_res_data["_result"]["status"] == "ok", f"테스트 후 데이터 삭제 실패 (ID: {article_id})"
    logger.info(f"테스트 종료 전 생성된 데이터 정리: ID {article_id} 삭제 완료")

@pytest.mark.parametrize("case_key, expected_status", [
    ("classroom_id_missing", 409),
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

    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        form_data=payload
    )

    res_data = response.json()
    logger.debug(f"응답 데이터: {res_data}")
    
    if res_data["_result"]["status_code"] != expected_status:
        logger.error(f"상태 코드 불일치! 기대: {expected_status}, 실제: {res_data['_result']['status_code']}")

    assert res_data["_result"]["status"] == "fail"
    assert res_data["_result"]["status_code"] == expected_status
    assert res_data.get("board_article_id") is None
    
    logger.info(f"=== STU_BOARD_02_002: {missing_key} 누락 케이스 검증 완료 ===")
        
def test_get_linked_courses(classroom_client, valid_headers, classroom_id, test_board_data):
    """STU_BOARD_02_003: 게시글 작성 연결 과목 조회"""
    logger.info("=== STU_BOARD_02_003: 연결 과목 조회 시작 ===")

    endpoint = f"/classroom/{classroom_id}/course"
    query = test_board_data["queries"]["course_query"]
    logger.debug(f"API 요청 경로: {endpoint} | 파라미터: {query}")

    response = classroom_client.get(
        endpoint=endpoint,
        headers=valid_headers,
        params=query
    )

    assert response.status_code == 200, f"조회 실패: {response.status_code}"
    courses = response.json()
    logger.info(f"조회된 과목 수: {len(courses)}")
    assert isinstance(courses, list), "응답 형식이 리스트가 아닙니다."
    
    if len(courses) > 0:
        # 첫 번째 과목에 필수 필드가 있는지 확인
        assert "id" in courses[0], "과목 ID 필드가 없습니다."
        assert "title" in courses[0], "과목 제목 필드가 없습니다."
        logger.debug(f"첫 번째 과목 데이터 확인: {courses[0]}")
    logger.info("=== STU_BOARD_02_003: 테스트 완료 ===")

@pytest.mark.parametrize("case_key", [
    "valid_article", 
    "not_found_article"
])
def test_get_article_detail_cases(
    rest_client, 
    valid_headers,
    case_key,
    test_board_data
):
    """
    STU_BOARD_02_004: 특정 게시글 조회
    STU_BOARD_02_005: 존재하지 않는 게시글 상세 조회
    """
    
    case_data = test_board_data["article_data"]["detail_cases"][case_key]
    article_id = case_data["article_id"]
    expected_status = case_data["expected_status"]
    expected_result = case_data["expected_result"]
    expected_fail_code = case_data["expected_fail_code"]
    
    logger.info(f"=== 상세 조회 테스트 시작 ({case_key} ID: {article_id}) ===")
    
    response = rest_client.get(
        endpoint="/org/qatrack/board/article/get/",
        headers=valid_headers,
        params={"board_article_id": article_id}
    )
    
    body = response.json()
    logger.debug(f"[{case_key}] 응답 결과: {body}")
    
    assert body["_result"]["status"] == expected_result
    assert body["_result"]["status_code"] == expected_status
    
    if expected_result == "ok":
        logger.info(f"정상 조회 성공: {body['board_article']['title']}")
        assert body["board_article"]["id"] == article_id
        assert "title" in body["board_article"]
    else:
        logger.info(f"에러 케이스 검증 (결과: {expected_fail_code})")
        assert body["fail_code"] == expected_fail_code
        assert body["fail_message"] == "bad request"
        assert "board_article" not in body
    
    logger.info(f"=== 상세 조회 케이스(ID: {article_id}) 완료 ===")

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
        logger.critical(f"보안 경고: 비밀글(ID: {article_id})이 타인에게 노출됨!")
    
    # 실패해야 정상
    # 현재는 AssertionError가 발생하여 xfail 처리
    assert body["_result"]["status"] == "fail", f"보안 취약점: ID {article_id} 비밀글이 조회됨"
    assert body["_result"]["status_code"] == 409
    assert body["fail_code"] == "insufficient_permission"
    logger.info("=== 타인 비밀글 테스트 시나리오 종료 ===")

def test_update_article_success(rest_client, valid_headers, classroom_id, create_article_data, test_board_data):
    """
    STU_BOARD_02_007: 게시글 수정
    테스트용 게시글 생성 -> 해당 ID로 내용 수정 -> 테스트 종료 후 삭제
    """
    logger.info("=== STU_BOARD_02_007: 게시글 수정 테스트 시작 ===")

    headers = valid_headers.copy()
    headers.pop("Content-Type", None)
    
    # 1. 수정을 위한 임시 게시글 생성
    create_payload = {**create_article_data, "classroom_id": classroom_id}
    create_res = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        form_data=create_payload
    )
    article_id = create_res.json().get("board_article_id")
    logger.info(f"수정 테스트를 위한 임시 게시글 생성 완료 (ID: {article_id})")

    try:
        # 2. 방금 생성한 ID를 사용하여 게시글 수정
        edit_content = test_board_data["edit_article"]["update_payload"]
        update_payload = {
            "board_article_id": article_id,
            **edit_content,
            "classroom_id": classroom_id
        }
        
        response = rest_client.post(
            endpoint="/org/qatrack/board/article/edit/",
            headers=headers,
            form_data=update_payload
        )

        res_data = response.json()
        logger.debug(f"수정 API 응답 데이터: {res_data}")
        
        assert res_data["_result"]["status"] == "ok"
        assert res_data["_result"]["status_code"] == 200
        assert res_data["board_article_id"] == article_id
        logger.info(f"게시글 ID {article_id} 수정 검증 완료")

    finally:
        # 3. 테스트 종료 후 임시 게시글 삭제
        delete_payload = {"board_article_id": article_id}
        delete_res = rest_client.post(
            endpoint="/org/qatrack/board/article/delete/",
            headers=headers,
            form_data=delete_payload
        )
        if delete_res.json()["_result"]["status"] == "ok":
            logger.info(f"임시 테스트 데이터 삭제 완료 (ID: {article_id})")
        else:
            logger.error(f"임시 데이터 삭제 실패 (ID: {article_id})")

    logger.info("=== STU_BOARD_02_007: 테스트 종료 ===")

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

    res_data = response.json()
    logger.debug(f"타인 글 수정 시도 응답: {res_data}")

    assert res_data["_result"]["status"] == "fail", f"보안 취약점: 타인의 게시글({article_id})이 수정되었습니다!"

    assert res_data["_result"]["status_code"] == 400
    assert res_data["fail_code"] == "resource_not_found"

    logger.info(f"=== STU_BOARD_03_002: 타인 게시글({article_id}) 수정 차단 확인 완료 ===")

def test_delete_article_success(rest_client, valid_headers, classroom_id, create_article_data):
    """
    STU_BOARD_02_009: 게시글 삭제
    반복 테스트를 위해 게시글 생성 후 삭제 로직
    """
    logger.info("=== STU_BOARD_02_009: 게시글 삭제 테스트 시작 ===")

    # 1. ID 확보용 게시글 생성
    create_payload = {**create_article_data, "classroom_id": classroom_id}
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    create_res = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        form_data=create_payload
    )
    
    # 생성된 글의 ID를 가져옵니다.
    article_id = create_res.json().get("board_article_id")
    logger.info(f"삭제 테스트를 위한 임시 게시글 생성 완료 (ID: {article_id})")

    # 2. 방금 생성된 ID로 삭제 요청
    delete_payload = {"board_article_id": article_id}

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/delete/",
        headers=headers,
        form_data=delete_payload
    )

    res_data = response.json()
    assert res_data["_result"]["status"] == "ok"
    assert res_data["_result"]["status_code"] == 200
    
    logger.info(f"=== STU_BOARD_02_009: 게시글 삭제 테스트 ID {article_id} 삭제 검증 완료 ===")

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
    
    body = response.json()
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

    body = response.json()
    logger.debug(f"API 응답 데이터: {body}")

    if body["_result"]["status"] == "ok":
        logger.critical(f"보안 경고: 타인의 게시글(ID: {target_id})이 권한 없이 삭제됨!")

    # 실패해야 정상 (삭제가 성공하면 AssertionError 발생 -> xfail 처리)
    assert body["_result"]["status"] == "fail", f"보안 취약점: 타인의 글(ID: {target_id})이 삭제됨"
    assert body["_result"]["status_code"] in [403, 409]  # 차단 시 발생해야 할 코드
    assert body["fail_code"] == "insufficient_permission"
    
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

    res_data = response.json()
    logger.debug(f"서버 응답: {res_data}")

    assert res_data["_result"]["status"] == "fail", "글자수 초과 제목이 차단되지 않았습니다."
    assert res_data["_result"]["status_code"] == 400
    assert res_data["fail_code"] == "invalid_parameter"
    
    logger.info("=== STU_BOARD_02_011: 글자수 제한 정책 적용 확인 완료 ===")

# ---------------- STU_BOARD_03 ----------------

def test_article_like_add_and_delete_flow(rest_client, valid_headers, classroom_id, test_board_data):
    """
    STU_BOARD_03-001: 게시글 좋아요 정상 동작
    STU_BOARD_03-002: 게시글 좋아요 취소 확인
    순서: 새 글 작성 -> 좋아요 추가 -> 좋아요 취소
    """
    logger.info("=== STU_BOARD_03-001,002: 좋아요 추가/취소 테스트 시작 ===")

    like_test_data = test_board_data["like_article_data"]["like_test"]
    
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    create_res = rest_client.post(
        endpoint="/org/qatrack/board/article/edit/",
        headers=headers,
        form_data={
            "classroom_id": classroom_id,
            **like_test_data 
        }
    )
    article_id = create_res.json().get("board_article_id")
    logger.info(f"테스트용 게시글 생성 완료 (ID: {article_id})")

    # 좋아요 추가
    like_add_res = rest_client.post(
        endpoint="/org/qatrack/board/article/like/add/",
        headers=headers,
        form_data={"board_article_id": article_id}
    )
    
    like_add_body = like_add_res.json()
    assert like_add_body["_result"]["status"] == "ok"
    assert like_add_body["_result"]["status_code"] == 200
    logger.info(f"ID {article_id} 게시글 좋아요 추가 성공")

    # 좋아요 취소
    like_del_res = rest_client.post(
        endpoint="/org/qatrack/board/article/like/delete/",
        headers=headers,
        form_data={"board_article_id": article_id}
    )
    
    like_del_body = like_del_res.json()
    assert like_del_body["_result"]["status"] == "ok"
    assert like_del_body["_result"]["status_code"] == 200
    logger.info(f"ID {article_id} 게시글 좋아요 취소 성공")

    logger.info("=== STU_BOARD_03-001,002: 모든 좋아요 시나리오 검증 완료 ===")

@pytest.mark.parametrize("data_key, expected_status, expected_code, expected_fail_code", [
    ("valid_comment", "ok", 200, None),
    ("invalid_article_comment", "fail", 400, "resource_not_found")
])
def test_create_comment(rest_client, valid_headers, test_board_data, 
                                    data_key, expected_status, expected_code, expected_fail_code):
    """
    STU_BOARD_03-003: 댓글 작성 가능 확인
    STU_BOARD_03-004: 존재하지 않는 게시글 댓글 작성
    """
    logger.info(f"=== 댓글 작성 테스트 시작 ===")

    payload = test_board_data["comment_data"][data_key]
    
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    response = rest_client.post(
        endpoint="/org/qatrack/board/article/comment/edit/",
        headers=headers,
        form_data=payload
    )

    res_data = response.json()
    logger.debug(f"응답 데이터: {res_data}")

    assert res_data["_result"]["status"] == expected_status
    assert res_data["_result"]["status_code"] == expected_code

    if expected_fail_code:
        assert res_data["fail_code"] == expected_fail_code
        assert res_data["_result"]["reason"] == "param"
        logger.info(f"예상대로 {expected_fail_code} 에러 발생 확인")
    else:
        assert "article_comment_id" in res_data
        logger.info(f"댓글 작성 성공 (ID: {res_data['article_comment_id']})")

    logger.info(f"=== STU_BOARD_03-003, 004 댓글 테스트 종료 ===")

def test_comment_like_add_and_delete(rest_client, valid_headers, test_board_data):
    """
    STU_BOARD_03-005: 댓글 좋아요 정상 동작
    STU_BOARD_03-006: 댓글 좋아요 취소 확인
    """
    logger.info("=== 댓글 좋아요 및 취소 테스트 시작 ===")

    comment_data = test_board_data["comment_data"]["like_test"]
    comment_id = comment_data["article_comment_id"]
    
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)
    
    logger.debug(f"테스트 대상 댓글 ID: {comment_id}")

    # 1. 댓글 좋아요 추가
    endpoint_add = "/org/qatrack/board/article/comment/like/add/"
    logger.debug(f"좋아요 추가 요청 엔드포인트: {endpoint_add}")
    
    like_add_res = rest_client.post(
        endpoint=endpoint_add,
        headers=headers,
        form_data={"article_comment_id": comment_id}
    )
    
    like_add_body = like_add_res.json()
    logger.debug(f"좋아요 추가 응답: {like_add_body}")

    assert like_add_body["_result"]["status"] == "ok"
    assert like_add_body["_result"]["status_code"] == 200
    logger.info(f"ID {comment_id} 댓글 좋아요 추가 성공")

    # 2. 댓글 좋아요 취소
    endpoint_del = "/org/qatrack/board/article/comment/like/delete/"
    logger.debug(f"좋아요 취소 요청 엔드포인트: {endpoint_del}")
    
    like_del_res = rest_client.post(
        endpoint=endpoint_del,
        headers=headers,
        form_data={"article_comment_id": comment_id}
    )
    
    like_del_body = like_del_res.json()
    logger.debug(f"좋아요 취소 응답: {like_del_body}")

    assert like_del_body["_result"]["status"] == "ok"
    assert like_del_body["_result"]["status_code"] == 200
    logger.info(f"ID {comment_id} 댓글 좋아요 취소 성공")

    logger.info("=== STU_BOARD_03-005, 006: 댓글 좋아요 시나리오 검증 완료 ===")

def test_comment_update_delete(rest_client, valid_headers, test_board_data):
    """
    STU_BOARD_03-007: 댓글 수정 반영 확인
    STU_BOARD_03-008: 댓글 삭제 확인
    흐름: 댓글 작성 -> 작성된 댓글 수정 -> 해당 댓글 삭제
    """
    logger.info("=== STU_BOARD_03-007,008: 댓글 수정, 삭제 테스트 시작 ===")
    
    test_data = test_board_data["comment_data"]["update_delete_test"]
    board_article_id = test_data["board_article_id"]
    
    headers = valid_headers.copy()
    headers.pop("Content-Type", None)

    # --- 1. 댓글 작성 ---
    create_payload = {
        "board_article_id": board_article_id,
        "content": test_data["create_content"]
    }
    logger.debug(f"댓글 작성 요청: {create_payload}")
    
    create_res = rest_client.post(
        endpoint="/org/qatrack/board/article/comment/edit/",
        headers=headers,
        form_data=create_payload
    )
    
    create_body = create_res.json()
    assert create_body["_result"]["status"] == "ok"
    comment_id = create_body["article_comment_id"]
    logger.info(f"댓글 작성 성공 (ID: {comment_id})")

    # --- 2. 댓글 수정 ---
    update_payload = {
        "board_article_id": board_article_id,
        "article_comment_id": comment_id,
        "content": test_data["update_content"]
    }
    logger.debug(f"댓글 수정 요청: {update_payload}")
    
    update_res = rest_client.post(
        endpoint="/org/qatrack/board/article/comment/edit/",
        headers=headers,
        form_data=update_payload
    )
    
    assert update_res.json()["_result"]["status"] == "ok"
    logger.info(f" ID {comment_id} 댓글 수정 완료")

    # --- 3. 댓글 삭제 ---
    delete_payload = {
        "article_comment_id": comment_id
    }
    logger.debug(f"댓글 삭제 요청: {delete_payload}")
    
    delete_res = rest_client.post(
        endpoint="/org/qatrack/board/article/comment/delete/",
        headers=headers,
        form_data=delete_payload
    )
    
    assert delete_res.json()["_result"]["status"] == "ok"
    logger.info(f" ID {comment_id} 댓글 삭제 완료")

    logger.info("=== STU_BOARD_03-007,008: 댓글 수정, 삭제 검증 완료 ===")

def test_get_comment_list_success(rest_client, valid_headers, test_board_data):
    """STU_BOARD_03-009: 특정 게시글 댓글 목록 조회"""
    logger.info("=== STU_BOARD_03-009: 댓글 목록 조회 테스트 시작 ===")

    params = test_board_data["comment_data"]["list_params"]
    logger.debug(f"조회 조건: {params}")

    response = rest_client.get(
        endpoint="/org/qatrack/board/article/comment/list/",
        headers=valid_headers,
        params=params
    )

    res_data = response.json()
    logger.debug(f"조회 응답 데이터 요약: {res_data.get('_result')}")

    assert res_data["_result"]["status"] == "ok"
    assert res_data["_result"]["status_code"] == 200

    assert isinstance(res_data.get("article_comments"), list)

    if res_data["article_comments"]:
        first_comment = res_data["article_comments"][0]
        logger.info(f"조회 성공: 첫 번째 댓글 ID -> {first_comment.get('id')}")
    else:
        logger.warning("조회는 성공했으나 댓글이 비어있습니다.")

    logger.info("=== STU_BOARD_03-009 댓글 목록 조회 테스트 종료 ===")

@pytest.mark.parametrize("sort_key, expected_status, expected_code", [
    ("valid_desc", "ok", 200),
    ("valid_asc", "ok", 200),
    ("invalid_key", "fail", 400),
    ("invalid_order", "fail", 400),
    ("missing_field", "fail", 400)
])
def test_get_comment_list_sort_parametrize(rest_client, valid_headers, test_board_data,
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
        "board_article_id": sort_config["board_article_id"],
        "sort_by": json.dumps(sort_value)
    }

    response = rest_client.get(
        endpoint="/org/qatrack/board/article/comment/list/",
        headers=valid_headers,
        params=params
    )

    res_data = response.json()
    logger.debug(f"응답 데이터: {res_data}")

    assert res_data["_result"]["status"] == expected_status
    assert res_data["_result"]["status_code"] == expected_code

    if expected_status == "fail":
        assert res_data["fail_code"] == "invalid_parameter"
        assert res_data["_result"]["reason"] == "param"
    else:
        assert "article_comments" in res_data
        logger.info(f"정렬 조회 성공: {len(res_data['article_comments'])}개의 댓글 반환")

    logger.info(f"=== STU_BOARD_03-010,011,012 테스트 종료 ===")