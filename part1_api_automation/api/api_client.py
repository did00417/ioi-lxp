import requests
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str, timeout: int = 10):
        """
        base_url: 서비스 base URL
        timeout: 기본 타임아웃 (초)
        """
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self.session = requests.Session()

    def _build_url(self, endpoint: str) -> str:
        """
        base_url / endpoint 이중 슬래시 방지
        """
        return urljoin(self.base_url, endpoint.lstrip("/"))

    def request(
        self,
        method: str,
        endpoint: str,
        headers=None,
        params=None,
        payload=None,
        data=None,
        timeout=None,
    ):
        url = self._build_url(endpoint)
        request_timeout = timeout or self.timeout

        logger.info(f"API 요청 시작: {method} {url}")
        logger.debug(
            f"Headers={headers}, Params={params}, Payload={payload}, Data={data}"
        )

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=payload,
                data=data,
                timeout=request_timeout,
            )

            logger.info(f"API 응답 완료: {method} {url}")
            logger.info(f"Status code = {response.status_code}")
            
            logger.debug(
                f"Headers={headers}, Params={params}, Payload={payload}, Data={data}"
            )
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

    def get(self, endpoint, headers=None, params=None, timeout=None):
        return self.request(
            method="GET",
            endpoint=endpoint,
            headers=headers,
            params=params,
            timeout=timeout,
        )

    def post(self, endpoint, headers=None, params=None, payload=None, data=None, timeout=None):
        return self.request(
            method="POST",
            endpoint=endpoint,
            headers=headers,
            params=params,
            payload=payload,
            data=data,
            timeout=timeout,
        )

    def patch(self, endpoint, headers=None, params=None, payload=None, timeout=None):
        return self.request(
            method="PATCH",
            endpoint=endpoint,
            headers=headers,
            params=params,
            payload=payload,
            timeout=timeout,
        )

    def delete(self, endpoint, headers=None, params=None, timeout=None):
        return self.request(
            method="DELETE",
            endpoint=endpoint,
            headers=headers,
            params=params,
            timeout=timeout,
        )