import json
from datetime import datetime, timezone
from config import OUTPUT_FILE

def print_header(snapshot_ts: int):
    """Print header"""
    ts_str  = datetime.fromtimestamp(snapshot_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "=" * 65)
    print("     BLOCKCHAIN BALANCE SNAPSHOT")   
    print(f"    Target  : {ts_str} UTC  (unix={snapshot_ts})")
    print("=" * 65)
    
    
def print_results(results: list):
    """Print table"""
    print("\n" + "=" * 65)
    print("     RESULT")
    print("=" * 65)
    print(f"    {'Chain': <8} {'Token': <8} {'Block/Seqno': <22} {'Balance'}")
    print("     " + "=" * 60)
    for r in results:
        print(f"    {r['chain']: <8} {r['token']: <8} {str(r['block']): <22} {r['balance']}")
    print()
    
    
def save_results(results: list, snapshot_ts: int):
    """Save result to JSON"""
    ts_str      = datetime.fromtimestamp(snapshot_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    output = {
        "snapshot_timestamp": snapshot_ts,
        "snapshot_utc": ts_str,
        "results": results
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)
    print(f"    Result has been saved in {OUTPUT_FILE}")