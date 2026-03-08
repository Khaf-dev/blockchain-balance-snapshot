# Blockchain Balance Snapshot

Automation script untuk fetch token balance dari beberapa blockchain pada timestamp tertentu.

**Snapshot Target:** `2024-12-31 23:59:59 UTC` (unix: `1735689599`)

---

## Chains & Tokens

| Chain | Token |                       Address                      |
|-------|-------|----------------------------------------------------|
| Avail | AVAIL | `5H1qc1com3wK9k1jxa6RjPFv1cB83G9HHEcFfSm8VtkpqPYH` |
| KCC   | KCS   | `0x14ea40648fc8c1781d19363f5b9cc9a877ac2469`       |
| KCC   | APE   | `0x14ea40648fc8c1781d19363f5b9cc9a877ac2469`       |
| TON   | TON   | `EQBysKw2y2jUpOAaUNEmxM9BqUg4iScsiOGgdTZvodwaP-jq` |
| TON   | USDT  | `EQBysKw2y2jUpOAaUNEmxM9BqUg4iScsiOGgdTZvodwaP-jq` |
| LTC   | LTC   | `ltc1qv7wsvsmx6tqxjz9l750n0pj524na4lmqrjhyz9`      |

---

## Struktur Folder

```
blockchain_snapshot/
├── main.py               ← Entry point, jalankan ini
├── config.py             ← Semua alamat wallet, contract, dan API endpoint
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

## Setup & Cara Jalankan

**1. Install dependencies**
```bash
pip install requests
pip install substrate-interface   # opsional, untuk Avail via RPC langsung
```

**2. Jalankan script**
```bash
python main.py
```

**3. Output**
- Terminal: tabel hasil semua chain
- File: `results.json`

---

## Cara Kerja

### Menemukan Block Target
Setiap chain punya pendekatan berbeda:

| Chain |                Strategi                 |                                Alasan                                     |
|-------|-----------------------------------------|---------------------------------------------------------------------------|
| Avail | Estimasi rumus + verifikasi Subscan API | Block time stabil ~20 detik                                               |
| KCC   | Binary search via EVM JSON-RPC          | Block time ~3 detik, lebih akurat pakai search                            |
| TON   | Estimasi dari reference seqno           | TonCenter rate limit, hindari terlalu banyak request                      |
| LTC   | Estimasi rumus + verifikasi BlockCypher | Block time stabil ~150 detik                                              |

### Fetch Balance
| Chain |                           Method                         |
|-------|----------------------------------------------------------|
| Avail | `substrate.query(System.Account, address, block_hash)`   |
| KCS   | `eth_getBalance(address, block_hex)` via JSON-RPC        |
| APE   | `eth_call(balanceOf(address), block_hex)` via JSON-RPC   |
| TON   | `getAddressInformation` via TonCenter API                |
| USDT  | `runGetMethod` → JettonMaster → JettonWallet (2 langkah) |
| LTC   | Blockchair API dengan parameter `?before=<block>`        |

---

## Known Limitations

**KCS (KCC)**
Public RPC `rpc-mainnet.kcc.network` bukan archive node. Query ke block lama menghasilkan error `missing trie node`. Script otomatis fallback ke balance `latest` dengan keterangan. Untuk nilai historis yang akurat diperlukan KCC archive node.

**TON (native & USDT)**
TonCenter free tier tidak support historical state query per seqno. Balance yang direturn adalah balance saat ini. Untuk nilai historis akurat diperlukan TON archive node atau Tonviewer Pro API.

**USDT di TON**
Wallet ini tidak pernah hold USDT asli (Tether official). Yang ada hanya fake/SCAM token (terdeteksi badge SCAM di Tonviewer). Balance = 0 USDT, dikonfirmasi via `runGetMethod` ke JettonMaster resmi yang return 404/422.

---

## APIs yang Dipakai

| API          | Endpoint                         |                  Dipakai untuk                     |
|--------------|----------------------------------|----------------------------------------------------|
| Subscan      | `avail.api.subscan.io/api`       | Verifikasi block Avail                             |
| KCC RPC      | `rpc-mainnet.kcc.network`        | Block discovery + balance KCC                      |
| TonCenter v2 | `toncenter.com/api/v2`           | Seqno + balance TON                                |
| BlockCypher  | `api.blockcypher.com/v1/ltc`     | Verifikasi block LTC                               |
| Blockchair   | `api.blockchair.com/litecoin`    | Balance LTC historis                               |

---

## Konfigurasi

Semua yang perlu diubah ada di `config.py`:

```python
SNAPSHOT_TS        = 1735689599          # ganti kalau mau timestamp lain
APE_CONTRACT_KCC   = "0xdae6c2..."       # verified dari scan.kcc.io
USDT_JETTON_MASTER = "EQCxE6mU..."       # verified dari tether.to official
```