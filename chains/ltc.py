from config import LTC_REF_BLOCK, LTC_REF_TS, LTC_BLOCK_TIME
from utils.helpers import estimate_block, http_get

def find_block(target_ts: int) -> dict:
    """
    Estimated closest LTC block.
    """
    estimated = estimate_block(target_ts, LTC_REF_BLOCK, LTC_REF_TS, LTC_BLOCK_TIME)
    print(f"    [LTC] Block Estimate: {estimated: ,}")
    
    try:
        data = http_get(
            f"https://api.blockcypher.com/v1/ltc/main/blocks/{estimated}",
            params={"txstart": 1, "limit": 1}
        )
        if "error" not in data:
            actual_time = data.get("time", "")
            print(f"    [LTC] Confirmed block {estimated: ,} -> {actual_time}")
            return {"block_number": estimated, "block_timestamp": actual_time}
    except Exception as e:
        print(f"    [LTC] BlockCypher error: {e}")
        
    return {"block_number": estimated, "block_timestamp": None}


def get_balance(address: str, block_number: int) -> str:
    """
    Get the LTC balance at a specific block using the Blockchair API.
    
    How UTXOs work:
        - Balance == the sum of all received and unspent coins.
        - The `before=block` parameter filters out UTXOs confirmed before that block.
        --> This gives us an accurate snapshot of the balance at that point in time.
    """
    try:
        data        = http_get(
            f"https://api.blockchair.com/litecoin/dashboards/address/{address}",
            params={"before": block_number}
        )
        balance_sat = data["data"][address]["address"]["balance"]
        balance_ltc = balance_sat / 1e8 # <== satoshi to LTC
        return f"{balance_ltc: .8f} LTC"
    except Exception as e:
        return f"Error: {e}"