import requests
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str, timeout: int = 10):
        """
        API 통신을 위한 공통 클라이언트
        :param base_url: 서비스 base URL
        :param timeout: 기본 타임아웃 (초)
        """
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.session = requests.Session()

    def _build_url(self, endpoint: str) -> str:
        """base_url / endpoint 이중 슬래시 방지"""
        return urljoin(self.base_url, endpoint.lstrip("/"))

    # 피드백 적용: 파라미터 이름 명확화 (payload -> json_body, data -> form_data) & 타입 힌트 통일
    def request(
        self,
        method: str,
        endpoint: str,
        headers: dict = None,
        params: dict = None,
        json_body: dict = None,  # JSON 요청 시 사용
        form_data: dict = None,  # Form-Data 요청 시 사용
        timeout: int = None,
    ) -> requests.Response:
        
        url = self._build_url(endpoint)
        request_timeout = timeout or self.timeout

        logger.info(f"API 요청 시작: {method} {url}")
        logger.debug(f"Headers={headers}, Params={params}, json_body={json_body}, form_data={form_data}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_body,   # requests 라이브러리의 json 파라미터에 매핑
                data=form_data,   # requests 라이브러리의 data 파라미터에 매핑
                timeout=request_timeout,
            )

            logger.info(f"API 응답 완료: {method} {url}")
            logger.info(f"Status code = {response.status_code}")
            
            # 피드백 적용: 요청 후에는 중복 로그를 지우고, 대신 '응답 헤더'를 로깅
            logger.debug(f"응답 헤더: {response.headers}")
            logger.debug(f"응답 바디: {response.text}")

            return response

        except requests.exceptions.Timeout:
            logger.error(f"[TIMEOUT] {method} {url}")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"[CONNECTION ERROR] {method} {url}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"[REQUEST ERROR] {method} {url} - {e}")
            raise

    # 피드백 적용: Docstring 추가 및 통일된 타입 힌트 적용
    def get(self, endpoint: str, headers: dict = None, params: dict = None, timeout: int = None) -> requests.Response:
        """GET 요청을 전송합니다."""
        return self.request(
            method="GET", 
            endpoint=endpoint, 
            headers=headers, 
            params=params, 
            timeout=timeout
        )

    def post(self, endpoint: str, headers: dict = None, params: dict = None, json_body: dict = None, form_data: dict = None, timeout: int = None) -> requests.Response:
        """
        POST 요청을 전송합니다.
        - JSON 데이터를 보낼 때는 json_body 사용
        - Form-Data를 보낼 때는 form_data 사용
        """
        return self.request(
            method="POST", 
            endpoint=endpoint, 
            headers=headers, 
            params=params, 
            json_body=json_body, 
            form_data=form_data, 
            timeout=timeout
        )

    def patch(self, endpoint: str, headers: dict = None, params: dict = None, json_body: dict = None, form_data: dict = None, timeout: int = None) -> requests.Response:
        """
        PATCH 요청을 전송합니다. (데이터의 일부분만 수정할 때 사용)
        - JSON 데이터를 수정할 때는 json_body 사용
        - 파일, 이미지 등을 수정할 때는 form_data 사용
        """
        return self.request(
            method="PATCH", 
            endpoint=endpoint, 
            headers=headers, 
            params=params, 
            json_body=json_body, 
            form_data=form_data, 
            timeout=timeout
        )

    def delete(self, endpoint: str, headers: dict = None, params: dict = None, timeout: int = None) -> requests.Response:
        """DELETE 요청을 전송합니다."""
        return self.request(
            method="DELETE", 
            endpoint=endpoint, 
            headers=headers, 
            params=params, 
            timeout=timeout
        )