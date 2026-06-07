import requests


class GoogleRoutesProvider:
    def __init__(self, api_key, url):
        self.api_key = api_key
        self.url = url

    def compute_routes(self, headers, body, timeout):
        return requests.post(
            self.url,
            headers=headers,
            json=body,
            timeout=timeout
        )
