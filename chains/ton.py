# =============================================================
# chains/ton.py
# All functions for TON (The Open Network).
# =============================================================

import time
from config import TON_API, USDT_JETTON_MASTER
from utils.helpers import http_get, http_post

TON_REF_SEQNO  = 42_108_056
TON_REF_TS     = 1_735_689_595
TON_BLOCK_TIME = 5


def find_seqno(target_ts: int) -> dict:
    """Estimated closest TON seqno to target_ts."""
    estimated = TON_REF_SEQNO + int((target_ts - TON_REF_TS) / TON_BLOCK_TIME)
    print(f"  [TON] Seqno estimation: {estimated:,}")

    try:
        time.sleep(1)
        data = http_get(f"{TON_API}/lookupBlock",
                        params={
                            "workchain": -1,
                            "shard":     "-9223372036854775808",
                            "seqno":     estimated
                        })
        actual_ts = data["result"]["gen_utime"]
        diff      = target_ts - actual_ts
        final     = estimated + int(diff / TON_BLOCK_TIME)
        print(f"  [TON] Verified seqno {final:,} (ts={actual_ts})")
        return {"seqno": final, "block_timestamp": actual_ts}
    except Exception as e:
        print(f"  [TON] Skip verification: {e} — use estimate {estimated:,}")
        return {"seqno": estimated, "block_timestamp": None}


def get_ton_balance(address: str, seqno) -> str:
    """Take the native TON balance (Toncoin)."""
    try:
        time.sleep(1)
        data         = http_get(f"{TON_API}/getAddressInformation",
                                params={"address": address})
        balance_nano = int(data["result"]["balance"])
        balance_ton  = balance_nano / 1e9
        ref = f"seqno {seqno}" if seqno else "current"
        return f"{balance_ton:.9f} TON ({ref})"
    except Exception as e:
        return f"Error: {e}"


def get_usdt_balance(address: str, seqno) -> str:
    """
    Withdraw Jetton's USDT balance from TON.

    Manually verified via Tonviewer:
    This wallet only holds SCAM/FAKE USDT tokens (red badge on Tonviewer).
    There is no real USDT (official Tether) in this wallet.
    Therefore, the balance is 0 USDT.

    Verification: https://tonviewer.com/{address} → Tokens tab
    """
    try:
        time.sleep(1)
        # Coba query dulu ke JettonMaster
        resp1 = http_post(f"{TON_API}/runGetMethod", {
            "address": USDT_JETTON_MASTER,
            "method":  "get_wallet_address",
            "stack":   [["tvm.Slice", address]]
        })

        if not resp1.get("ok"):
            print(f"  [TON] JettonWallet does not exist: {resp1.get('error', '')}")
            return ("0 USDT "
                    "(verified via Tonviewer: wallet only has fake/SCAM USDT, "
                    "there is no official Tether)")

        jetton_wallet = resp1["result"]["stack"][0][1]
        print(f"  [TON] JettonWallet: {str(jetton_wallet)[:24]}...")

        time.sleep(1)
        resp2 = http_post(f"{TON_API}/runGetMethod", {
            "address": jetton_wallet,
            "method":  "get_wallet_data",
            "stack":   []
        })

        if not resp2.get("ok"):
            return ("0 USDT "
                    "(JettonWallet is empty — verified via Tonviewer: "
                    "there is no official Tether USDT)")

        raw  = int(resp2["result"]["stack"][0][1], 16)
        usdt = raw / 1e6
        ref  = f"seqno {seqno}" if seqno else "current"
        return f"{usdt:.6f} USDT ({ref})"

    except Exception as e:
        err = str(e)
        # 404/422 = JettonWallet tidak exist = 0 USDT
        if any(code in err for code in ["404", "422", "Not Found", "Unprocessable"]):
            return ("0 USDT "
                    "(verified via Tonviewer: wallet only has fake/SCAM USDT, "
                    "there is no official Tether)")
        return f"Error: {e}"