# ================================================================
# config.py 
# This file contains the constants, wallet addressesm and endpoints
# If you want to change the addresses or RPC, just change or edit 
# this file.
# ================================================================

# Snapshot timestamp
# Target snapshot: December 31, 2024 23:59:59 UTC
SNAPSHOT_TS = 1735689599

# Wallet addresses
AVAIL_ADDRESS = "5H1qc1com3wK9k1jxa6RjPFv1cB83G9HHEcFfSm8VtkpqPYH"
KCC_ADDRESS = "0x14ea40648fc8c1781d19363f5b9cc9a877ac2469"
TON_ADDRESS = "EQBysKw2y2jUpOAaUNEmxM9BqUg4iScsiOGgdTZvodwaP-jq"
LTC_ADDRESS = "ltc1qv7wsvsmx6tqxjz9l750n0pj524na4lmqrjhyz9"

# Token contracts
# APE in KCC - verification in https://scan.kcc.io/tokens
APE_CONTRACT_KCC = "0xDAe6c2A48BFAA66b43815c5548b10800919c993E"

# USDT Jetton Master in TON (Official)
USDT_JETTON_MASTER = "EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs"

# RPC / API endpoints
AVAIL_RPC = "https://mainnet.avail-rpc.com"
SUBSCAN_API = "https://avail.api.subscan.io/api"
KCC_RPC = "https://rpc-mainnet.kcc.network"
TON_API = "https://toncenter.com/api/v2"

# Reference Blocks (just for estimate)
# Avail: 
AVAIL_REF_BLOCK = 681_952
AVAIL_REF_TS = 1_733_724_180
AVAIL_BLOCK_TIME = 20

# LTC: 
LTC_REF_BLOCK = 2_784_332
LTC_REF_TS = 1_730_547_886
LTC_BLOCK_TIME = 150

# KCC:
KCC_CURRENT_BLOCK = 50_000_000
KCC_CURRENT_TS = 1_741_305_600
KCC_BLOCK_TIME = 3

# Output
OUTPUT_FILE = "results.json"