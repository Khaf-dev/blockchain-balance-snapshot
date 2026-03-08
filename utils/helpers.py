# =============================================================
# utils/helpers.py
# Common functions used by all chain modules.
# =============================================================

import time
import requests


def estimate_block(target_ts: int, ref_block: int, ref_ts: int, block_time: int) -> int:
    """
    The block number estimate is based on the time difference from the reference point.
    Formula: target_block = ref_block + (target_ts - ref_ts) / block_time
    """
    return ref_block + int((target_ts - ref_ts) / block_time)


def binary_search_block(get_timestamp_fn, target_ts: int, lo: int, hi: int) -> int:
    """
    Binary search to find the block number closest to the target timestamp.
    """
    while hi - lo > 1:
        mid = (lo + hi) // 2
        ts  = get_timestamp_fn(mid)
        if ts <= target_ts:
            lo = mid
        else:
            hi = mid
    return lo


def http_get(url: str, params: dict = None, timeout: int = 15,
             delay: float = 0, retries: int = 3) -> dict:
    """
    Wrapper GET request with automatic retry.
    delay: delay before request (seconds) — to avoid rate limits
    retries: number of retries if failed
    """
    if delay:
        time.sleep(delay)

    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            if resp.status_code == 429:
                wait = 2 ** attempt   # 1s, 2s, 4s
                print(f"    Rate limit (429), wait {wait}s then retry...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(1)
                continue
            raise e

    raise Exception(f"Failed after {retries} attempts: {url}")


def http_post(url: str, payload: dict, timeout: int = 15,
              delay: float = 0, retries: int = 3) -> dict:
    """
    Wrapper POST request with automatic retry.
    """
    if delay:
        time.sleep(delay)

    for attempt in range(retries):
        try:
            resp = requests.post(url, json=payload, timeout=timeout)
            if resp.status_code == 429:
                wait = 2 ** attempt
                print(f"    Rate limit (429), wait {wait}s then retry...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(1)
                continue
            raise e

    raise Exception(f"Failed after {retries} attempts: {url}")