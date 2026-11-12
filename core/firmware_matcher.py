import os
import re

from core.paths import get_firmware_dir

# Generation character of an SBF* image, from s11-flasher2-readme (SBFMxx.x table).
# header is the stub family: 0t Toshiba/Kioxia/Hynix/Sandisk, 0m Intel/Micron.
# None means the readme does not name a stub, so the user must choose one.
PHISON_S11_GENERATIONS = {
    "0": {"nand": "Toshiba 15nm MLC", "header": "0t"},
    "1": {"nand": "Toshiba 15nm TLC", "header": "0t"},
    "2": {"nand": "Intel/Micron L06B 32L MLC", "header": "0m"},
    "5": {"nand": "Hynix 16nm TLC", "header": "0t"},
    "6": {"nand": "Toshiba BiCS2/BiCS3/BiCS4 3D TLC", "header": "0t"},
    "7": {"nand": "Micron/Intel B0KB 32L TLC", "header": "0m"},
    "8": {"nand": "Toshiba 15nm MLC (UFS)", "header": "0t"},
    "9": {"nand": "Toshiba 15nm MLC", "header": "0t"},
    "A": {"nand": "Intel 3D TLC (L06B → B0KB)", "header": "0m"},
    "B": {"nand": "Micron/Intel B16A/B17A 64L TLC", "header": "0m"},
    "E": {"nand": "Hynix 3D 72L TLC", "header": "0t"},
    "F": {"nand": "Samsung 14nm MLC", "header": None},
    "G": {"nand": "Phison S11, серия G (тип NAND в таблице не указан)", "header": None},
    "J": {"nand": "Micron B27A/B27B 96L TLC", "header": "0m"},
    "K": {"nand": "Intel N18A/N28A 3D QLC", "header": "0m"},
    "P": {"nand": "YMTC 64L TLC", "header": None},
    "X": {"nand": "Hynix 3D V5/V6 TLC", "header": "0t"},
    "Y": {"nand": "Micron B37R 128L TLC", "header": "0m"},
}

PHISON_S11_SUBTYPES = {
    "BA": "Micron/Intel B16A/B17A 64L TLC",
    "BB": "Micron/Intel B16A/B17A 64L TLC, полный SLC-кэш",
    "KA": "Intel N18A 64L QLC",
    "KB": "Intel N28A 96L QLC",
}

SUPPORTED_FW_SIZES = (1479168, 1544704, 1547776)

def parse_s11_filename(filename):
    """Read series and NAND generation from names like SBFM61.2 or SBFMBB."""
    base = os.path.basename(filename or "").upper()
    match = re.match(r"SBF([A-Z0-9])([0-9A-Z])([0-9A-Z])?", base)
    if not match:
        return None
    gen = match.group(2).upper()
    third = (match.group(3) or "").upper()
    sub = gen + third if third else gen
    info = PHISON_S11_GENERATIONS.get(gen)
    nand = PHISON_S11_SUBTYPES.get(sub)
    if not nand:
        nand = info["nand"] if info else "Phison S11, поколение не описано в таблице"
    series = "SBF" + match.group(1).upper()
    return {
        "series": series,
        "gen": gen,
        "sub": sub,
        "prefix5": series + gen,
        "nand": nand,
        "header": info["header"] if info else None,
    }

def scan_local_firmwares():
    """Indexes all firmware files found in firmware/"""
    firmwares = []
    firmware_dir = get_firmware_dir()
    
    # Scan Phison
    phison_s11_dir = os.path.join(firmware_dir, "phison", "s11")
    if os.path.exists(phison_s11_dir):
        for root, dirs, files in os.walk(phison_s11_dir):
            for f in files:
                if f.upper().endswith(".BIN"):
                    path = os.path.join(root, f)
                    size = os.path.getsize(path)
                    
                    ident = parse_s11_filename(f)
                    size_ok = size in SUPPORTED_FW_SIZES
                    if ident:
                        target_nand = ident["nand"]
                        header_type = ident["header"]
                        generation = f"Поколение {ident['gen']} ({ident['prefix5']})"
                        s11_prefix = ident["prefix5"]
                        s11_gen = ident["gen"]
                    else:
                        target_nand = "Phison S11, имя не по таблице SBF"
                        header_type = None
                        generation = "Имя не распознано"
                        s11_prefix = ""
                        s11_gen = ""

                    firmwares.append({
                        "vendor": "Phison",
                        "controller": "PS3111-S11",
                        "filename": f,
                        "path": path,
                        "size": size,
                        "size_str": f"{round(size / 1024, 1)} KB",
                        "target_nand": target_nand,
                        "generation": generation,
                        "header_type": header_type,
                        "size_supported": size_ok,
                        "s11_prefix": s11_prefix,
                        "s11_gen": s11_gen,
                        "is_local": True
                    })

    # Scan SMI
    smi_dir = os.path.join(firmware_dir, "smi")
    if os.path.exists(smi_dir):
        for root, dirs, files in os.walk(smi_dir):
            for f in files:
                if f.upper().endswith((".BIN", ".RAR", ".ZIP", ".7Z")):
                    path = os.path.join(root, f)
                    size = os.path.getsize(path)
                    ctrl = "SM2258XT" if "2258" in f else ("SM2259XT" if "2259" in f else "SMI")
                    firmwares.append({
                        "vendor": "Silicon Motion",
                        "controller": ctrl,
                        "filename": f,
                        "path": path,
                        "size": size,
                        "size_str": f"{round(size / (1024*1024), 2)} MB",
                        "target_nand": "SMI MPTool Package",
                        "generation": "MPTool",
                        "is_local": True
                    })

    # Scan Maxio
    maxio_dir = os.path.join(firmware_dir, "maxio")
    if os.path.exists(maxio_dir):
        for root, dirs, files in os.walk(maxio_dir):
            for f in files:
                if f.upper().endswith((".BIN", ".RAR", ".ZIP", ".7Z")):
                    path = os.path.join(root, f)
                    size = os.path.getsize(path)
                    firmwares.append({
                        "vendor": "Maxio",
                        "controller": "MAS0902",
                        "filename": f,
                        "path": path,
                        "size": size,
                        "size_str": f"{round(size / (1024*1024), 2)} MB",
                        "target_nand": "Maxio MPTool Package",
                        "generation": "MPTool",
                        "is_local": True
                    })

    return firmwares

def match_firmwares(detected_info):
    """
    Given detection info (controller, flash_id, flash_desc),
    ranks local firmware files and online MPTool packages by compatibility.
    """
    combined = scan_local_firmwares()

    if not detected_info or not detected_info.get("controller"):
        return combined

    ctrl = (detected_info.get("controller") or "").upper()
    flash_desc = (detected_info.get("flash_desc") or "").upper()
    fw_current = (detected_info.get("fw_version") or "").upper()
    raw_text = (detected_info.get("raw") or "").upper()

    detected_s11 = parse_s11_filename(fw_current) if fw_current.startswith("SBF") else None
    nand_part = (detected_info.get("nand_part") or "").upper()
    matches = []
    others = []

    for item in combined:
        score = 0
        reasons = []
        item_ctrl = item.get("controller", "").upper()
        item_file = item.get("filename", "").upper()
        target_nand = item.get("target_nand", "").upper()
        scored_s11_gen = False

        if ctrl and (ctrl in item_ctrl or item_ctrl in ctrl):
            score += 40
            reasons.append(f"Контроллер совпадает ({item['controller']})")
        elif "2258" in ctrl and "2258" in item_file:
            score += 40
            reasons.append("Контроллер SM2258")
        elif "2259" in ctrl and "2259" in item_file:
            score += 40
            reasons.append("Контроллер SM2259")
        elif any(k in ctrl for k in ["MAS0902", "MAS0901", "MK8215", "CS1802", "DM9343"]):
            if "MAS0902" in item_file or "MAS0902" in item_ctrl:
                score += 45
                reasons.append("Контроллер Maxio MAS0902")
        elif "MAS1102" in ctrl and "1102" in item_file:
            score += 45
            reasons.append("Контроллер Maxio MAS1102")
        elif "MAP1602" in ctrl and "1602" in item_file:
            score += 45
            reasons.append("Контроллер Maxio MAP1602")
        elif "MAP1202" in ctrl and "1202" in item_file:
            score += 45
            reasons.append("Контроллер Maxio MAP1202")

        if detected_s11 and item.get("s11_prefix"):
            scored_s11_gen = True
            if item["s11_prefix"] == detected_s11["prefix5"]:
                score += 80
                reasons.append(f"Та же серия {detected_s11['prefix5']}")
            elif item.get("s11_gen") == detected_s11["gen"]:
                score += 30
                reasons.append(
                    f"Поколение NAND {detected_s11['gen']} совпадает, серия другая ({item['s11_prefix']})"
                )

        if nand_part and nand_part in item_file:
            score += 60
            reasons.append(f"Точное совпадение маркировки NAND ({nand_part})")

        # Keyword NAND score is for catalog packages. Local S11 images are ranked by series.
        if not scored_s11_gen:
            blob = f"{flash_desc} {raw_text} {nand_part}"
            if any(h in blob for h in ["HYNIX", "HY3D", "HYNV4", "3DV4", "HYV4"]):
                if any(k in item_file for k in ["HY3D-V4", "HYNV4", "3DV4", "HYV4"]):
                    score += 40
                    reasons.append("Память Hynix 3D-V4 (72L)")
                elif "HYNIX" in item_file or "HY3D" in item_file or "HYNIX" in target_nand:
                    score += 20
                    reasons.append("Память Hynix")

            if "TOSHIBA" in blob or "KIOXIA" in blob:
                if "BICS4" in flash_desc and ("BICS4" in item_file or "BICS4" in target_nand):
                    score += 40
                    reasons.append("Поколение Kioxia/Toshiba BiCS4")
                elif "BICS3" in flash_desc and ("BICS3" in item_file or "BICS3" in target_nand):
                    score += 40
                    reasons.append("Поколение Toshiba BiCS3")
                elif "BICS" in flash_desc and ("BICS" in item_file or "BICS" in target_nand):
                    score += 25
                    reasons.append("Память Toshiba BiCS")
                elif "TOSHIBA" in target_nand or "TOSHIBA" in item_file:
                    score += 20
                    reasons.append("Память Toshiba")

            if "MICRON" in blob or "INTEL" in blob:
                if ("B16A" in flash_desc or "B16" in flash_desc) and ("B16" in item_file or "B16" in target_nand):
                    score += 40
                    reasons.append("Поколение Micron B16A")
                elif ("B17A" in flash_desc or "B17" in flash_desc) and ("B17" in item_file or "B17" in target_nand):
                    score += 40
                    reasons.append("Поколение Micron B17A")
                elif ("B27A" in flash_desc or "B27" in flash_desc) and ("B27" in item_file or "B27" in target_nand):
                    score += 40
                    reasons.append("Поколение Micron B27A")
                elif "B0KB" in flash_desc and ("B0KB" in item_file or "B0KB" in target_nand):
                    score += 40
                    reasons.append("Поколение Micron B0KB")
                elif "N18" in blob and "N18" in item_file:
                    score += 40
                    reasons.append("Поколение Intel N18A (64L)")
                elif "N28" in blob and "N28" in item_file:
                    score += 40
                    reasons.append("Поколение Intel N28A (96L)")
                elif "MICRON" in target_nand or "MICRON" in item_file or "INTEL" in item_file:
                    score += 20
                    reasons.append("Память Micron/Intel")

            if "YMTC" in flash_desc and ("YMTC" in item_file or "YMTC" in target_nand):
                score += 40
                reasons.append("Память YMTC")

        if fw_current and fw_current in item_file:
            score += 60
            reasons.append(f"Совпадение версии прошивки ({fw_current})")

        item["match_score"] = score
        item["match_reasons"] = reasons
        same_series = any(reason.startswith("Та же серия") for reason in reasons)

        if same_series:
            item["badge"] = "Та же серия прошивки"
            item["badge_color"] = "emerald"
            matches.append(item)
        elif score >= 70:
            item["badge"] = "Совпадает контроллер и память"
            item["badge_color"] = "blue"
            matches.append(item)
        elif score >= 40:
            item["badge"] = "Тот же контроллер, другая память"
            item["badge_color"] = "gray"
            matches.append(item)
        else:
            item["badge"] = "Другая серия"
            item["badge_color"] = "gray"
            others.append(item)

    matches.sort(key=lambda x: x["match_score"], reverse=True)
    others.sort(key=lambda x: x["match_score"], reverse=True)
    return matches + others

if __name__ == "__main__":
    fw = scan_local_firmwares()
    print(f"Total indexed firmwares: {len(fw)}")
    test_detection = {
        "controller": "PS3111-S11",
        "flash_desc": "Toshiba BiCS3 64L TLC",
        "fw_version": "SBFG61.2"
    }
    ranked = match_firmwares(test_detection)
    print("\nTop 5 matches for Toshiba BiCS3 SBFG61.2:")
    for r in ranked[:5]:
        print(f"  [{r['badge']}] {r['filename']} (Score: {r['match_score']}) -> {', '.join(r['match_reasons'])}")
