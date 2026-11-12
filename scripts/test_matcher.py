import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from core.detector import parse_raw_report
from core.firmware_matcher import match_firmwares

sample_report = """v0.569a
Drive: 4(ATA)
OS: 10.0 build 26200 
Model: R5SL480G                                
Fw   : T0724A0 
Size : 457858 MB [480.1 GB]
From smart : [SMI2258XT] [T0724A0 00] [HYNV4]
Controller : SM2258   bufferless
FlashID: 0xad,0x5e,0x29,0x22,0x10,0x90,0x0,0x0 - Hynix 3dv4-72L TLC 8k 1024Gb/CE 512Gb/die
Channel: 2
CE     : 2
TotDie : 8
Plane  : 4
Die/Ce : 2
Ch map : 0x03
CE map : 0x05
Inter. : 4
First Fblock  :    2
Total Fblock  : 1272
Total Hblock  : 7155
Fblock Per Ce : 1272
Fblock Per Die: 1272
Original Spare Block Count :    85
Vendor Marked Bad Block    :     0
Bad Block From Pretest     :     6
"""

parsed = parse_raw_report(sample_report)
print("=== PARSED DETECTION ===")
for k, v in parsed.items():
    if k != "raw":
        print(f"  {k}: {v}")

matches = match_firmwares(parsed)
print(f"\n=== MATCHED FIRMWARES & MPTOOLS (Total: {len(matches)}) ===")
for m in matches[:6]:
    print(f"[{m['badge']}] Score: {m['match_score']} -> {m['filename']}")
    print(f"   Reasons: {', '.join(m['match_reasons'])}")
    print(f"   Target NAND: {m.get('target_nand')} | URL: {m.get('url')}")
