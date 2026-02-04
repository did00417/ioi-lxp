import requests

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def request(self, method, endpoint, headers=None, params=None, payload=None):
        url = f"{self.base_url}{endpoint}"

        response = self.session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=payload
        )
        return response

    def get(self, endpoint, headers=None, params=None):
        return self.request(
            method="GET",
            endpoint=endpoint,
            headers=headers,
            params=params
        )

    def post(self, endpoint, headers=None, params=None, payload=None):
        return self.request(
            method="POST",
            endpoint=endpoint,
            headers=headers,
            params=params,
            payload=payload
        )

    def patch(self, endpoint, headers=None, params=None, payload=None):
        return self.request(
            method="PATCH",
            endpoint=endpoint,
            headers=headers,
            params=params,
            payload=payload
        )

    def delete(self, endpoint, headers=None, params=None):
        return self.request(
            method="DELETE",
            endpoint=endpoint,
            headers=headers,
            params=params
        )