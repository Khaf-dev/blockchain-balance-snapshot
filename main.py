# ================================================================
# main.py -> Entry Point <- Run this file to start the application
#
# This file just "orchestrator" - no logic inside code block
# This task is to call the functions in the right order and 
# handle the flow of the application.
#
# If u want add new chain, just add the function at chains file
# and call the function here, no need to change the logic of 
# this file.
# ================================================================

import sys
import os

# Add the root folder into path
sys.path.insert(0, os.path.dirname(__file__))

from config import (
    SNAPSHOT_TS,
    AVAIL_ADDRESS, KCC_ADDRESS, TON_ADDRESS, LTC_ADDRESS
)
from chains import avail, kcc, ton, ltc
from utils.printer import print_header, print_results, save_results

def main():
    print_header(SNAPSHOT_TS)
    results = []
    
    # Call the functions for each chain
    # AVAIL
    print("\n[1/4] AVAIl")
    avail_block = avail.find_block(SNAPSHOT_TS)
    avail_bal = avail.get_balance(AVAIL_ADDRESS, avail_block["block_number"])
    results.append({
        "chain": "AVAIL",
        "address": AVAIL_ADDRESS,
        "token": "AVAIL", 
        "block": avail_block["block_number"],
        "balance": avail_bal,
    })
    
    # KCC -> KCS
    print("\n[2/4] KCC")
    kcc_block = kcc.find_block(SNAPSHOT_TS)
    results.append({
        "chain": "KCC",
        "address": KCC_ADDRESS,
        "token": "KCS",
        "block": kcc_block["block_number"],
        "balance": kcc.get_kcs_balance(KCC_ADDRESS, kcc_block["block_number"]),
    })
    
    # KCC -> APE
    results.append({
        "chain": "KCC",
        "address": KCC_ADDRESS,
        "token": "APE",
        "block": kcc_block["block_number"],
        "balance": kcc.get_ape_balance(KCC_ADDRESS, kcc_block["block_number"])
    })
    
    # TON
    print("\n[3/4] TON")
    ton_info = ton.find_seqno(SNAPSHOT_TS)
    results.append({
        "chain": "TON",
        "address": TON_ADDRESS,
        "token": "TON",
        "block": f"seqno={ton_info['seqno']}",
        "balance": ton.get_ton_balance(TON_ADDRESS, ton_info["seqno"])
    })
    results.append({
        "chain": "TON",
        "address": TON_ADDRESS,
        "token": "USDT",
        "block": f"seqno={ton_info['seqno']}",
        "balance": ton.get_usdt_balance(TON_ADDRESS, ton_info["seqno"])
    })
    
    # LTC
    print("\n[4/4] LTC")
    ltc_block = ltc.find_block(SNAPSHOT_TS)
    results.append({
        "chain": "LTC",
        "address": LTC_ADDRESS,
        "token": "LTC",
        "block": ltc_block["block_number"],
        "balance": ltc.get_balance(LTC_ADDRESS, ltc_block["block_number"])
    })
    
    # Output results
    print_results(results)
    save_results(results, SNAPSHOT_TS)
    
if __name__ == "__main__":
    main()
    