# Blockchain Balance Snapshot

Automation script to fetch token balance from multiple blockchains at a specific timestamp.

**Snapshot Target:** `2024-12-31 23:59:59 UTC` (unix: `1735689599`)

---

## Chains & Tokens

| Chain | Token | Address                                            |
| ----- | ----- | -------------------------------------------------- |
| Avail | AVAIL | `5H1qc1com3wK9k1jxa6RjPFv1cB83G9HHEcFfSm8VtkpqPYH` |
| KCC   | KCS   | `0x14ea40648fc8c1781d19363f5b9cc9a877ac2469`       |
| KCC   | APE   | `0x14ea40648fc8c1781d19363f5b9cc9a877ac2469`       |
| TON   | TON   | `EQBysKw2y2jUpOAaUNEmxM9BqUg4iScsiOGgdTZvodwaP-jq` |
| TON   | USDT  | `EQBysKw2y2jUpOAaUNEmxM9BqUg4iScsiOGgdTZvodwaP-jq` |
| LTC   | LTC   | `ltc1qv7wsvsmx6tqxjz9l750n0pj524na4lmqrjhyz9`      |

---

## Folder Structure

```
blockchain_snapshot/
├── main.py               ← Entry point, run this
├── config.py             ← All wallet addresses, contracts, and API endpoints
├── requirements.txt
├── README.md
├── chains/
│   ├── avail.py          → find_block() + get_balance()
│   ├── kcc.py            → find_block() + get_kcs_balance() + get_ape_balance()
│   ├── ton.py            → find_seqno() + get_ton_balance() + get_usdt_balance()
│   └── ltc.py            → find_block() + get_balance()
└── utils/
    ├── helpers.py        → estimate_block(), binary_search_block(), http_get/post()
    └── printer.py        → print_header(), print_results(), save_results()
```

---

## Setup & How to Run

**1. Install dependencies**

```bash
pip install requests
pip install substrate-interface   # optional, to Avail via RPC directly
```

**2. Run the script**

```bash
python main.py
```

**3. Output**

- Terminal: table of results of all chains
- File: `results.json`

---

## How's this works?

### Finding the Target Block

Each chain has a different approach:

| Chain | Strategy                                      | Reason                                            |
| ----- | --------------------------------------------- | ------------------------------------------------- |
| Avail | Subscan API formula estimation + verification | Stable block time ~20 seconds                     |
| KCC   | Binary search via EVM JSON-RPC                | Block time ~3 seconds, more accurate using search |
| TON   | Estimates from reference seqno                | TonCenter rate limit, avoid too many requests     |
| LTC   | BlockCypher formula estimation + verification | Stable block time ~150 seconds                    |

### Fetch Balance

| Chain | Method                                                 |
| ----- | ------------------------------------------------------ |
| Avail | `substrate.query(System.Account, address, block_hash)` |
| KCS   | `eth_getBalance(address, block_hex)` via JSON-RPC      |
| APE   | `eth_call(balanceOf(address), block_hex)` via JSON-RPC |
| TON   | `getAddressInformation` via TonCenter API              |
| USDT  | `runGetMethod` → JettonMaster → JettonWallet (2 steps) |
| LTC   | Blockchair API with parameter `?before=<block>`        |

---

## Known Limitations

**KCS (KCC)**
The public RPC `rpc-mainnet.kcc.network` is not an archive node. Queries to older blocks result in a `missing trie node` error. The script automatically falls back to the `latest` balance with a note. For accurate historical values, a KCC archive node is required.

**TON (native & USDT)**
The TonCenter free tier does not support historical state queries per seqno. The returned balance is the current balance. For accurate historical values, a TON archive node or the Tonviewer Pro API is required.

**USDT di TON**
This wallet never holds genuine USDT (official Tether). It only holds fake/scam tokens (detected with a SCAM badge in Tonviewer). Balance = 0 USDT, confirmed via `runGetMethod` to the official JettonMaster, which returns 404/422.

---

## APIs Used

| API          | Endpoint                      | Used for                      |
| ------------ | ----------------------------- | ----------------------------- |
| Subscan      | `avail.api.subscan.io/api`    | Verify block availability     |
| KCC RPC      | `rpc-mainnet.kcc.network`     | Block discovery + balance KCC |
| TonCenter v2 | `toncenter.com/api/v2`        | Seqno + balance TON           |
| BlockCypher  | `api.blockcypher.com/v1/ltc`  | LTC block verification        |
| Blockchair   | `api.blockchair.com/litecoin` | Historical LTC balance        |

---

## Configuration

Everything that needs to be changed is in `config.py`:

```python
SNAPSHOT_TS        = 1735689599          # change if you want another timestamp
APE_CONTRACT_KCC   = "0xdae6c2..."       # verified from scan.kcc.io
USDT_JETTON_MASTER = "EQCxE6mU..."       # verified from tether.to official
```

## RESULTS
<img width="1341" height="818" alt="Screenshot 2026-03-08 221116" src="https://github.com/user-attachments/assets/c2e1a626-596c-4662-98d7-c145ce2ad455" />

