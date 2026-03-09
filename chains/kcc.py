# =============================================================
# chains/kcc.py
# All functions for KuCoin Community Chain (KCC).
# =============================================================

from config import (
    KCC_RPC, APE_CONTRACT_KCC,
    KCC_CURRENT_BLOCK, KCC_CURRENT_TS, KCC_BLOCK_TIME
)
from utils.helpers import binary_search_block, http_post


def _get_block_timestamp(block_number: int) -> int:
    """Get Unix timestamp from a KCC block via EVM JSON-RPC."""
    data = http_post(KCC_RPC, {
        "jsonrpc": "2.0",
        "method":  "eth_getBlockByNumber",
        "params":  [hex(block_number), False],
        "id": 1
    })
    if not data.get("result"):
        raise Exception(f"Block {block_number} not found")
    return int(data["result"]["timestamp"], 16)


def find_block(target_ts: int) -> dict:
    """Binary search the closest KCC block to target_ts."""
    estimated = KCC_CURRENT_BLOCK - int((KCC_CURRENT_TS - target_ts) / KCC_BLOCK_TIME)
    lo = max(1, estimated - 200_000)
    hi = estimated + 200_000

    print(f"  [KCC] Binary search di range [{lo:,} - {hi:,}]")

    try:
        block = binary_search_block(_get_block_timestamp, target_ts, lo, hi)
        ts    = _get_block_timestamp(block)
        print(f"    [KCC] Found: block {block:,} (ts={ts})")
        return {"block_number": block, "block_timestamp": ts}
    except Exception as e:
        print(f"    [KCC] Error: {e} — use estimate {estimated:,}")
        return {"block_number": estimated, "block_timestamp": None}


def get_kcs_balance(address: str, block_number: int) -> str:
    """
    Retrieve the KCS (native token) balance.

    The public KCC RPC is not an archive node — it only stores the state of the last few thousand blocks. If the block is too old, 
    it will give a 'missing trie node' error.

    Solution: try querying, if it fails, fallback to 'latest'
    Note that this is not an accurate historical value.
    """
    # Try on a historical block first
    try:
        data = http_post(KCC_RPC, {
            "jsonrpc": "2.0",
            "method":  "eth_getBalance",
            "params":  [address, hex(block_number)],
            "id": 1
        })
        # If there is a trie node error, go directly to fallback
        if "error" in data:
            err_msg = str(data["error"])
            if "trie" in err_msg or "missing" in err_msg:
                raise Exception("trie node pruned")
            return f"RPC Error: {data['error']}"

        wei = int(data["result"], 16)
        kcs = wei / 1e18
        return f"{kcs:.6f} KCS"

    except Exception as e:
        if "trie" in str(e) or "pruned" in str(e):
            # Fallback: query balance on the latest block
            print(f"    [KCC] Block {block_number:,} has been pruned, fallback to 'latest'")
            try:
                data = http_post(KCC_RPC, {
                    "jsonrpc": "2.0",
                    "method":  "eth_getBalance",
                    "params":  [address, "latest"],
                    "id": 1
                })
                wei = int(data["result"], 16)
                kcs = wei / 1e18
                # Note that these are not historical values.
                return (f"{kcs:.6f} KCS "
                        f"(current balance — public RPC not supported"
                        f"historical query, use archive node for EOY 2024 values)")
            except Exception as e2:
                return f"Error fallback: {e2}"
        return f"Error: {e}"


def get_erc20_balance(address: str, contract: str, block_number: int,
                      symbol: str, decimals: int = 18) -> str:
    """
    Retrieve the balance of ERC-20 tokens at a specific block via eth_call.
    balanceOf(address) selector = 0x70a08231
    """
    padded   = address[2:].lower().zfill(64)
    calldata = "0x70a08231" + padded

    try:
        data = http_post(KCC_RPC, {
            "jsonrpc": "2.0",
            "method":  "eth_call",
            "params":  [{"to": contract, "data": calldata}, hex(block_number)],
            "id": 1
        })
        if "error" in data:
            err_msg = str(data["error"])
            if "trie" in err_msg or "missing" in err_msg:
                # Fallback to latest for ERC-20 too
                print(f"    [KCC] {symbol} fallback to 'latest'")
                data = http_post(KCC_RPC, {
                    "jsonrpc": "2.0",
                    "method":  "eth_call",
                    "params":  [{"to": contract, "data": calldata}, "latest"],
                    "id": 1
                })
            else:
                return f"0 {symbol} (contract error)"

        result = data.get("result", "0x")
        if not result or result == "0x":
            return f"0 {symbol} (token does not exist at this address)"
        raw   = int(result, 16)
        human = raw / (10 ** decimals)
        return f"{human:.6f} {symbol}"
    except Exception as e:
        return f"Error: {e}"


def get_ape_balance(address: str, block_number: int) -> str:
    """Shortcut for APE balance (ERC-20 on KCC)."""
    return get_erc20_balance(address, APE_CONTRACT_KCC, block_number, "APE")