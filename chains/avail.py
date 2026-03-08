from config import (
    AVAIL_RPC, SUBSCAN_API,
    AVAIL_REF_BLOCK, AVAIL_REF_TS, AVAIL_BLOCK_TIME
)
from utils.helpers import estimate_block, http_post

def find_block(target_ts: int) -> dict:
    """
    Find block Avail block closest to target_ts.
    
    How it works:
    1. Initial estimate using formula (block_ref + time difference / block time)
    2. Verify with the subscan API
    3. Refine if the estimate is still off
    """
    estimated = estimate_block(target_ts, AVAIL_REF_BLOCK, AVAIL_REF_TS, AVAIL_BLOCK_TIME)
    print(f"    [Avail] Block Estimated: {estimated}")
    
    try:
        data = http_post(f"{SUBSCAN_API}/scan/block", {"block_num": estimated})
        if data.get("code") == 0:
            actual_ts = data["data"]["block_timestamp"]
            diff      = target_ts - actual_ts
            final     = estimated + int(diff / AVAIL_BLOCK_TIME)
            print(f"    [Avail] Fine-tuned: {final} (difference {diff} seconds from target)")
    except Exception as e:
        print(f"    [Avail] Subscan skip: {e}")
        
    return {"block_number": estimated, "block_timestamp": None}

def get_balance(address: str, block_number: int) -> str:
    """
    Retrieve the Avail balance on a specific block
    
    Method A:
        Substrate-interface (accurate, direct query to the node)
    
    Method B:
        Subscan API (fallback, current balance, not historical)
    """
    # METHOD A
    try:
        from substrateinterface import SubstrateInterface
        substrate   = SubstrateInterface(url=AVAIL_RPC)
        block_hash  = substrate.get_block_hash(block_id=block_number)
        account     = substrate.query(
            module='System',
            storage_function='Account',
            params=[address],
            block_hash=block_hash
        )
        free        = account.value['data']['free']
        reserved    = account.value['data']['reserved']
        total       = (free + reserved) / 1e18
        return f"{total: .6f} AVAIL"
    except ImportError:
        print("     [Avail] substrate-interface is not installed, use Subscan")
    except Exception as e:
        print(f"    [Avail] RPC error: {e}")
        
    
    # METHOD B
    try:
        data        = http_post(f"{SUBSCAN_API}/open/account", {"address": address})
        balance     = float(data["data"].get("balance", 0)) / 1e18
        return f"{balance: .6f} AVAIL (Balance now, not historis)"
    except Exception as e:
        return f"error: {e}"