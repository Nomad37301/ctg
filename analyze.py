#!/usr/bin/env python3
"""
CTF Forensics - FIN-WS-04 - Try session key + various crypto approaches
"""
import sys, base64, struct, hashlib, itertools
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from scapy.all import rdpcap, DNS, DNSRR, ICMP, IP, TCP, Raw

PCAP = "traffic.pcap"
pkts = rdpcap(PCAP)

# ─── ICMP body (215 bytes) ────────────────────────────────────────────────────
NORMAL_PING = b"PINGPINGPINGPINGPINGPINGPINGPING"
icmp_raw = []
for p in pkts:
    if p.haslayer(ICMP) and p.haslayer(IP):
        icmp = p[ICMP]
        raw = bytes(icmp.payload)
        if raw != NORMAL_PING and raw:
            icmp_raw.append((icmp.seq, raw))

icmp_raw.sort(key=lambda x: x[0])
combined = b"".join(r for _, r in icmp_raw)
data_len = combined[7]  # = 215
body = combined[8:8 + data_len]
print(f"ICMP body ({len(body)} bytes): {body.hex()}\n")

# ─── RC4 decrypt ─────────────────────────────────────────────────────────────
def rc4(key, data):
    if isinstance(key, str): key = key.encode()
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = bytearray()
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(byte ^ S[(S[i] + S[j]) % 256])
    return bytes(out)

# From the HTTP packet: session=s3ac1f9b0e7d4426a8f1c05e9b3a7d2f4
SESSION = "s3ac1f9b0e7d4426a8f1c05e9b3a7d2f4"
USER = "financebot"

keys = [
    SESSION,
    USER,
    SESSION[:16],
    SESSION[:8],
    SESSION[1:],  # without leading 's'
    "3ac1f9b0e7d4426a8f1c05e9b3a7d2f4",
    bytes.fromhex("3ac1f9b0e7d4426a8f1c05e9b3a7d2f4"),  # raw hex bytes
    "financebot:s3ac1f9b0e7d4426a8f1c05e9b3a7d2f4",
    USER + ":" + SESSION,
    SESSION + USER,
    hashlib.md5(SESSION.encode()).hexdigest(),
    hashlib.sha1(SESSION.encode()).digest(),
    hashlib.sha256(SESSION.encode()).digest()[:16],
    hashlib.md5(USER.encode()).hexdigest(),
    # Combine with known domain info
    "185.220.101.44",
    "10.10.14.37",
    "portal.internal",
    "portal",
    "internal",
    b"NJ01",  # magic as key
]

print("RC4 with all candidate keys:")
for key in keys:
    if isinstance(key, str):
        key_b = key.encode()
    else:
        key_b = key
    dec = rc4(key_b, body)
    printable = sum(1 for b in dec if 32 <= b < 127)
    score = printable / len(dec)
    flag_hit = any(marker in dec for marker in [b"CTF{", b"flag{", b"FLAG{", b"ctf{", b"FIN{", b"FINCTF{", b"ctg{"])
    if score > 0.7 or flag_hit:
        print(f"\n  [HIT] key={key_b!r} score={score:.2f}")
        print(f"  {dec.decode('utf-8', errors='replace')}")

# Also try XOR with session token
print("\n\nXOR with session token bytes:")
key_b = SESSION.encode()
dec = bytes([body[i] ^ key_b[i % len(key_b)] for i in range(len(body))])
print(f"  score: {sum(1 for b in dec if 32<=b<127)/len(dec):.2f}")
print(f"  {dec.decode('utf-8', errors='replace')}")

# Try XOR with raw hex bytes of session
key_hex = bytes.fromhex("3ac1f9b0e7d4426a8f1c05e9b3a7d2f4")
print("\nXOR with session as raw hex bytes (16 bytes key):")
dec2 = bytes([body[i] ^ key_hex[i % len(key_hex)] for i in range(len(body))])
print(f"  score: {sum(1 for b in dec2 if 32<=b<127)/len(dec2):.2f}")
print(f"  {dec2.decode('utf-8', errors='replace')}")
print(f"  hex: {dec2.hex()}")

# ─── AES approach (if key is 16 bytes) ───────────────────────────────────────
try:
    from Crypto.Cipher import AES
    print("\n\nAES-CTR with session hex key:")
    key16 = bytes.fromhex("3ac1f9b0e7d4426a8f1c05e9b3a7d2f4")
    # Try different IVs
    for iv_candidate in [b"\x00" * 16, b"NJ01" + b"\x00" * 12, combined[:16]]:
        try:
            cipher = AES.new(key16, AES.MODE_CTR, nonce=b"", initial_value=iv_candidate)
            dec_aes = cipher.decrypt(body)
            score = sum(1 for b in dec_aes if 32<=b<127) / len(dec_aes)
            if score > 0.6:
                print(f"  [HIT] IV={iv_candidate.hex()} score={score:.2f}")
                print(f"  {dec_aes.decode('utf-8', errors='replace')}")
        except Exception as e:
            pass
except ImportError:
    print("\n(pycryptodome not installed, skipping AES)")
