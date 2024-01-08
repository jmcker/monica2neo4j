import urllib.parse

import requests

DEFAULT_URL = "https://app.monicahq.com"
DEFAULT_VERSION = "1.0"


class MonicaApiError(Exception):
    pass


class MonicaApiClient:
    def __init__(self, token, base_url=DEFAULT_URL, version=DEFAULT_VERSION):
        self.token = token
        self.base_url = urllib.parse.urljoin(base_url + "/", "api/")
        self.version = version

    def test(self):
        try:
            self.me()
        except Exception as e:
            raise MonicaApiError(
                "Could not access the Monica API. Is your login correct?", e
            )

    def headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def process_json(self, resp):
        if len(resp.history) > 0 and "api" not in resp.url:
            raise MonicaApiError(
                "Monica redirected away from /api. Login information may be invalid"
            )

        content_type = resp.headers.get("Content-Type", "")
        if "json" not in content_type:
            raise MonicaApiError(f"Endpoint did not return JSON (got {content_type})")

        try:
            resp_json = resp.json()
        except Exception as e:
            raise MonicaApiError(f"JSON parse failed: {e}", e)

        if "error" in resp_json:
            e = resp_json["error"]

            code = e["error_code"]
            msg = e["message"]

            raise MonicaApiError(f"API error code {code}: {msg}")

        return resp_json

    def paged_resp(self, next_page_callback):
        page = 1
        total_pages = 1
        while page <= total_pages:
            page_resp = next_page_callback(page)

            if "meta" not in page_resp or "last_page" not in page_resp["meta"]:
                raise MonicaApiError(
                    "Paged result did not contain paging meta information"
                )

            yield page_resp

            total_pages = page_resp["meta"]["last_page"]
            page += 1

    def get(self, endpoint, **kwargs):
        url = urllib.parse.urljoin(self.base_url, endpoint)
        param_str = urllib.parse.urlencode(kwargs)

        print(f"GET {url}?{param_str}")

        try:
            resp = requests.get(url, headers=self.headers(), params=kwargs)
        except Exception as e:
            raise MonicaApiError(f"Request failed: {e}", e)

        return self.process_json(resp)

    def me(self):
        return self.get("me")

    def contacts(self, use_iter=True):
        if use_iter:
            return self.contacts_iter()

        return list(self.contacts_iter())

    def tags(self, use_iter=True):
        if use_iter:
            return self.tags_iter()

        return list(self.tags_iter())

    def contacts_iter(self):
        next_page_callback = lambda page_num: self.get("contacts", page=page_num)

        for page in self.paged_resp(next_page_callback):
            yield from page["data"]

    def tags_iter(self):
        next_page_callback = lambda page_num: self.get("tags", page=page_num)

        for page in self.paged_resp(next_page_callback):
            yield from page["data"]
