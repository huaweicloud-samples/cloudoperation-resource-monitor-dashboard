import hashlib
import hmac
import logging
import time
from datetime import datetime, timezone
from urllib.parse import urlparse, urlencode

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_INTERVAL = 60


def _sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _hmac_sha256_hex(key: str, data: str) -> str:
    return hmac.new(key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256).hexdigest()


def sign_request(ak: str, sk: str, method: str, url: str, headers: dict, body: str = "") -> dict:
    """华为云 API Gateway SDK-HMAC-SHA256 签名"""
    parsed = urlparse(url)
    host = parsed.netloc
    path = parsed.path or "/"
    query = parsed.query or ""

    if "host" not in {k.lower() for k in headers}:
        headers["host"] = host

    sdk_date = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    headers["X-Sdk-Date"] = sdk_date

    signed_header_keys = sorted(headers.keys(), key=str.lower)
    signed_headers_str = ";".join(k.lower() for k in signed_header_keys)

    canonical_headers = ""
    for k in signed_header_keys:
        canonical_headers += f"{k.lower()}:{headers[k].strip()}\n"

    body_hash = _sha256_hex(body or "")

    canonical_request = f"{method.upper()}\n{path}\n{query}\n{canonical_headers}\n{signed_headers_str}\n{body_hash}"

    string_to_sign = f"SDK-HMAC-SHA256\n{sdk_date}\n{_sha256_hex(canonical_request)}"

    signature = _hmac_sha256_hex(sk, string_to_sign)

    headers["Authorization"] = (
        f"SDK-HMAC-SHA256 Access={ak}, SignedHeaders={signed_headers_str}, Signature={signature}"
    )

    return headers


def _execute_request(method: str, url: str, headers: dict, body: str = None) -> requests.Response:
    if method.upper() == "GET":
        return requests.get(url, headers=headers, verify=False, timeout=120)
    elif method.upper() == "POST":
        return requests.post(url, headers=headers, data=body, verify=False, timeout=120)
    else:
        raise ValueError(f"Unsupported method: {method}")


def _is_retryable_error(e: Exception) -> bool:
    msg = str(e)
    return "429" in msg or "Too Many Requests" in msg or "ces.0429" in msg


def hwcloud_get(ak: str, sk: str, url: str) -> str:
    headers = {"Content-Type": "application/json;charset=utf-8"}
    headers = sign_request(ak, sk, "GET", url, headers)
    response = _execute_request("GET", url, headers)
    logger.info("GET %s 响应状态: %s", url[:80], response.status_code)
    if response.status_code == 429:
        raise RuntimeError("429 Too Many Requests")
    if response.status_code >= 400:
        raise RuntimeError(f"HTTP error: {response.status_code} {response.reason}")
    return response.text


def hwcloud_post(ak: str, sk: str, url: str, body: str) -> str:
    headers = {"Content-Type": "application/json;charset=utf-8"}
    headers = sign_request(ak, sk, "POST", url, headers, body)
    response = _execute_request("POST", url, headers, body)
    logger.info("POST %s 响应状态: %s", url[:80], response.status_code)
    if response.status_code == 429:
        raise RuntimeError("429 Too Many Requests")
    if response.status_code >= 400:
        raise RuntimeError(f"HTTP error: {response.status_code} {response.reason}")
    return response.text


def hwcloud_get_with_retry(ak: str, sk: str, url: str, max_retries: int = MAX_RETRIES, retry_interval: int = RETRY_INTERVAL) -> str:
    for attempt in range(1, max_retries + 1):
        try:
            result = hwcloud_get(ak, sk, url)
            if result:
                return result
        except Exception as e:
            if _is_retryable_error(e):
                logger.warning("触发流控，第%d次重试，等待%ds", attempt, retry_interval)
                if attempt < max_retries:
                    time.sleep(retry_interval)
                    continue
            logger.error("GET请求失败: %s", str(e))
        if attempt < max_retries:
            time.sleep(retry_interval)
    return None


def hwcloud_post_with_retry(ak: str, sk: str, url: str, body: str, max_retries: int = MAX_RETRIES, retry_interval: int = RETRY_INTERVAL) -> str:
    for attempt in range(1, max_retries + 1):
        try:
            result = hwcloud_post(ak, sk, url, body)
            if result:
                return result
        except Exception as e:
            if _is_retryable_error(e):
                logger.warning("触发流控，第%d次重试，等待%ds", attempt, retry_interval)
                if attempt < max_retries:
                    time.sleep(retry_interval)
                    continue
            logger.error("POST请求失败: %s", str(e))
        if attempt < max_retries:
            time.sleep(retry_interval)
    return None
