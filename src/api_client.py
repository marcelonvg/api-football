import time
import logging
from typing import Dict, Any, Optional
import requests
from requests import Response


class ApiFootballClient:
    
    def __init__(self, api_key: str, base_url: str = "https://v3.football.api-sports.io", timeout: int = 30):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "x-apisports-key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def _request_with_retry(self, method: str, path: str, params: Optional[Dict[str, Any]] = None,
                            max_retries: int = 5, backoff_base: float = 1.5) -> Response:
        url = f"{self.base_url}{path}"
        attempt = 0
        while True:
            attempt += 1
            resp = self.session.request(method, url, params=params, timeout=self.timeout)
            # Sucesso
            if 200 <= resp.status_code < 300:
                return resp

            # Requisitar retry para limites/erros transitórios
            if resp.status_code in (429, 500, 502, 503, 504) and attempt <= max_retries:
                wait = backoff_base ** attempt
                logging.warning(f"[retry] {method} {path} params={params} status={resp.status_code} "
                                f"tentativa={attempt}/{max_retries}, aguardando {wait:.1f}s")
                time.sleep(wait)
                continue

            # Falha final
            resp.raise_for_status()

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resp = self._request_with_retry("GET", path, params=params)
        return resp.json()

    def get_paginated(self, path: str, params: Optional[Dict[str, Any]] = None):

        if params is None:
            params = {}
        page = 1
        while True:
            qp = dict(params)
            qp["page"] = page
            data = self.get(path, qp)
            yield page, data

            paging = data.get("paging") or {}
            cur = int(paging.get("current") or page)
            tot = int(paging.get("total") or 1)
            if cur >= tot:
                break
            page += 1
