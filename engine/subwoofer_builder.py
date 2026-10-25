import os
import json
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# ==========================================
# ENVIRONMENT CONFIGURATION
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "https://hanifsalman11.github.io/subwoofer-amp-index").rstrip("/")
INDEXNOW_KEY = os.environ.get("INDEXNOW_KEY", "a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3").strip()
CUSTOM_SUB = os.environ.get("CUSTOM_SUB", "").strip()
PAGES_PER_RUN = int(os.environ.get("PAGES_PER_RUN", "3"))

DOCS_DIR = "docs"
DATA_DIR = "data"
PUBLISHED_FILE = os.path.join(DATA_DIR, "published_subwoofers.json")
MONETIZATION_FILE = os.path.join(DATA_DIR, "monetization.json")

# Format: (Subwoofer Model Name, Size Inches, RMS WattsSingle, Voice Coil Type, Ported CuFt, Tuning Hz, Sealed CuFt)
SEED_SUBWOOFERS = [
    ("Skar Audio EVL-12 D2 12-Inch Subwoofer", 12, 1250, "Dual 2-Ohm (DVC)", 2.00, 32, 1.25),
    ("Skar Audio SDR-12 D2 12-Inch Subwoofer", 12, 600, "Dual 2-Ohm (DVC)", 1.85, 34, 1.15),
    ("Skar Audio VXF-12 D2 12-Inch Competition Sub", 12, 1500, "Dual 2-Ohm (DVC)", 2.25, 31, 1.40),
    ("Skar Audio ZVX-15v2 D2 15-Inch SPL Subwoofer", 15, 1600, "Dual 2-Ohm (DVC)", 3.50, 30, 2.25),
    ("Sundown Audio SA-12 V.2 D2 12-Inch Subwoofer", 12, 1000, "Dual 2-Ohm (DVC)", 1.75, 35, 1.00),
    ("Sundown Audio X-12 V.3 D2 12-Inch Ultra-Low Sub", 12, 2000, "Dual 2-Ohm (DVC)", 2.50, 32, 1.50),
    ("Sundown Audio E-12 V.4 D2 12-Inch Subwoofer", 12, 500, "Dual 2-Ohm (DVC)", 1.75, 32, 1.00),
    ("JL Audio 12W7AE-3 12-Inch Anniversary Subwoofer", 12, 1000, "Single 3-Ohm (SVC)", 1.75, 32, 1.375),
    ("JL Audio 12W3v3-4 12-Inch Car Subwoofer", 12, 500, "Single 4-Ohm (SVC)", 1.75, 30, 1.125),
    ("JL Audio 10TW3-D4 10-Inch Shallow-Mount Subwoofer", 10, 400, "Dual 4-Ohm (DVC)", 0.60, 35, 0.50),
    ("Kicker CompR 12 (48CWR122) 12-Inch Subwoofer", 12, 500, "Dual 2-Ohm (DVC)", 1.75, 35, 1.00),
    ("Kicker Solo-Baric L7S 12 (44L7S122) Square Sub", 12, 750, "Dual 2-Ohm (DVC)", 2.25, 34, 1.25),
    ("Kicker CompVR 12 (43CVR124) 12-Inch Subwoofer", 12, 400, "Dual 4-Ohm (DVC)", 1.75, 35, 1.00),
    ("Rockford Fosgate Punch P3D4-12 12-Inch Subwoofer", 12, 600, "Dual 4-Ohm (DVC)", 1.79, 35, 1.02),
    ("Rockford Fosgate Power T1D212 12-Inch Subwoofer", 12, 800, "Dual 2-Ohm (DVC)", 1.75, 34, 1.25),
    ("Alpine R-Series R2-W12D4 12-Inch Halo Subwoofer", 12, 750, "Dual 4-Ohm (DVC)", 1.50, 33, 0.85),
    ("Alpine S-Series S2-W12D4 12-Inch Subwoofer", 12, 600, "Dual 4-Ohm (DVC)", 1.40, 34, 0.85),
    ("CT Sounds Tropo-12 D2 12-Inch Car Subwoofer", 12, 650, "Dual 2-Ohm (DVC)", 1.80, 34, 1.00),
    ("CT Sounds Ozone-12 D2 12-Inch Subwoofer", 12, 800, "Dual 2-Ohm (DVC)", 2.00, 33, 1.10),
    ("CT Sounds Meso-12 D2 12-Inch Competition Sub", 12, 1500, "Dual 2-Ohm (DVC)", 2.25, 32, 1.25),
    ("Deaf Bonce Apocalypse DB-SA252 D2 12-Inch Sub", 12, 1000, "Dual 2-Ohm (DVC)", 1.85, 34, 1.10),
    ("Deaf Bonce Machete MF-12R D2 12-Inch Subwoofer", 12, 1200, "Dual 2-Ohm (DVC)", 2.00, 33, 1.20),
    ("NVX VCW122 Version 3 12-Inch Subwoofer", 12, 1000, "Dual 2-Ohm (DVC)", 1.85, 33, 1.00),
    ("American Bass XR-12D2 12-Inch Competition Sub", 12, 1200, "Dual 2-Ohm (DVC)", 2.00, 34, 1.25),
    ("American Bass XFL-1222 12-Inch SPL Subwoofer", 12, 1500, "Dual 2-Ohm (DVC)", 2.25, 33, 1.40),
    ("Digital Designs DD Audio 612f 12-Inch Subwoofer", 12, 1000, "Dual 2-Ohm (DVC)", 2.00, 34, 1.15),
    ("DC Audio Level 3 12-Inch M3 Subwoofer", 12, 900, "Dual 2-Ohm (DVC)", 1.75, 34, 1.00),
    ("Orion HCCA 122 12-Inch Competition Subwoofer", 12, 2500, "Dual 2-Ohm (DVC)", 2.50, 32, 1.60),
    ("MTX Audio Terminator TNE212D Dual 12-Inch Setup", 12, 400, "Dual 12\" 2-Ohm Load", 2.40, 36, 2.00),
    ("Skar Audio VD-10 D2 10-Inch Shallow Truck Sub", 10, 500, "Dual 2-Ohm (DVC)", 1.25, 36, 0.65)
]


def load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Could not parse {filepath}: {e}")
    return default


def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    return re.sub(r"[\s-]+", "-", text).strip("-")


def safe_float(val, default=1.75):
    try:
        cleaned = re.sub(r"[^0-9.]", "", str(val))
        return float(cleaned) if cleaned else float(default)
    except Exception:
        return float(default)


def build_amazon_url(search_keywords, mon_cfg):
    domain = mon_cfg.get("marketplace_domain", "www.amazon.com")
    tag = mon_cfg.get("amazon_associate_tag", "YOUR_AMAZON_TAG-20")
    encoded_q = urllib.parse.quote_plus(search_keywords)
    return f"https://{domain}/s?k={encoded_q}&tag={tag}"


def discover_google_subwoofer_queries():
    """Mengambil kueri model subwoofer & kalkulator boks/amplifier dari Google Autocomplete US."""
    discovered = []
    seeds = [
        "skar audio ",
        "sundown audio ",
        "jl audio ",
        "kicker compr ",
        "subwoofer box calculator for "
    ]
    for seed in seeds:
        try:
            q = f"{seed}box specs" if "calculator" not in seed else seed
            url = f"http://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=us&q={urllib.parse.quote(q)}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for suggestion in data[1]:
                    cleaned = suggestion.lower()
                    for pref in seeds:
                        if "calculator" in pref:
                            cleaned = cleaned.replace(pref, "")
                    cleaned = re.sub(
                        r"\b(box|specs|calculator|volume|ported|sealed|size|amp|manual|reddit)\b",
                        "",
                        cleaned
                    ).strip()
                    if 5 <= len(cleaned) <= 42:
                        sz_match = re.search(r"\b(8|10|12|15|18)\b", cleaned)
                        sz_val = int(sz_match.group(1)) if sz_match else 12
                        vb_val = 0.85 if sz_val == 8 else (1.35 if sz_val == 10 else (1.85 if sz_val == 12 else 3.25))
                        discovered.append((cleaned.title(), sz_val, 800, "Dual 2-Ohm (DVC)", vb_val, 33, round(vb_val * 0.6, 2)))
        except Exception as e:
            print(f"[WARN] Google Suggest notice: {e}")
    return discovered


def build_deterministic_sub_data(sub_tuple):
    """Mesin Fisika Akustik Thiele-Small, Resonansi Helmholtz & Kelistrikan 13.8V DC (100% bebas gagal)."""
    sub_name, size_in, rms_w, coil_type, ported_cuft, tuning_hz, sealed_cuft = sub_tuple

    # Luas Port Area optimal (14 sq in per 1.0 cu ft net volume untuk mencegah port chuffing noise)
    port_area_sqin = int(round(ported_cuft * 14.0))
    # Rumus Panjang Port Helmholtz (inci):
    # Lv = ((1.463 * 10^7 * R^2) / (Fb^2 * Vb_in3)) - (1.463 * R)
    # di mana Vb_in3 = ported_cuft * 1728, R = sqrt(port_area_sqin / pi)
    vb_in3 = ported_cuft * 1728.0
    r_equiv = (port_area_sqin / 3.14159) ** 0.5
    port_length_in = round(((14630000.0 * (r_equiv ** 2)) / ((tuning_hz ** 2) * vb_in3)) - (1.463 * r_equiv), 1)
    port_length_in = max(14.0, min(38.0, port_length_in))

    # Perhitungan Arus DC Alternator & Ukuran Kabel OFC (pada 13.8V & efisiensi Class-D 80%)
    dc_current_amps = int(round(rms_w / (13.8 * 0.80)))
    anl_fuse_amps = int(round(dc_current_amps * 1.25, -1))
    if rms_w >= 1200:
        ofc_wire = "1/0 AWG 100% Oxygen-Free Copper (OFC)"
        alt_note = "Requires Big-3 1/0 AWG Alternator-to-Battery Upgrade + Auxiliary AGM Battery"
    elif rms_w >= 550:
        ofc_wire = "4 AWG 100% Oxygen-Free Copper (OFC)"
        alt_note = " Runs cleanly on factory electrical with a 4 AWG OFC kit (avoid Copper-Clad Aluminum CCA)"
    else:
        ofc_wire = "8 AWG or 4 AWG 100% Oxygen-Free Copper (OFC)"
        alt_note = "Compatible with stock alternator and battery"

    return {
        "sub_name": sub_name,
        "seo_title": f"{sub_name} Box Specs, Port Tuning (Hz) & Amp Wire Calculator (2026)",
        "meta_description": f"Calculate exact ported box volume ({ported_cuft} cu ft @ {tuning_hz} Hz), port area ({port_area_sqin} sq in), monoblock amp RMS ({rms_w}W), and OFC wire gauge ({ofc_wire}) for the {sub_name}.",
        "specs": {
            "size_inches": size_in,
            "rms_watts": rms_w,
            "voice_coil_config": coil_type,
            "ported_volume_cuft": ported_cuft,
            "tuning_freq_hz": tuning_hz,
            "sealed_volume_cuft": sealed_cuft,
            "port_area_sqin": port_area_sqin,
            "port_length_in": port_length_in,
            "dc_amperage_draw": dc_current_amps,
            "recommended_anl_fuse": anl_fuse_amps,
            "recommended_ofc_wire": ofc_wire
        },
        "acoustic_verdict": f"Rated at {rms_w:,} Watts RMS ({size_in}-inch {coil_type}), the {sub_name} achieves peak low-end output inside a {ported_cuft} cu. ft. net vented enclosure tuned to {tuning_hz} Hz (requiring {port_area_sqin} sq. in. of slot port area × {port_length_in}\" length), or {sealed_cuft} cu. ft. sealed for tight transient response. Powering this subwoofer at full RMS draws ~{dc_current_amps} Amps DC at 13.8V, requiring {ofc_wire} cable protected by a {anl_fuse_amps}A ANL fuse.",
        "hardware_bundle": [
            {
                "badge": f"{rms_w}W+ Class-D Monoblock",
                "title": f"{int(round(rms_w * 1.2, -2)):,}W RMS 1-Ohm Stable Class-D Monoblock Car Audio Amplifier",
                "price_range": "$149 - $499",
                "amazon_query": f"{int(round(rms_w * 1.2, -2))}W RMS 1 Ohm Stable Monoblock Subwoofer Amplifier",
                "audio_note": f"Provides 20% clean dynamic headroom above {rms_w}W RMS so you never clip the MOSFET output stage into the voice coils."
            },
            {
                "badge": f"{ported_cuft} ft³ Ported Box",
                "title": f"Heavy-Duty 3/4\" MDF / Birch Vented {size_in}-Inch Subwoofer Enclosure ({ported_cuft} Cu Ft @ {tuning_hz} Hz)",
                "price_range": "$109 - $279",
                "amazon_query": f"Single {size_in} Inch Ported Vented Subwoofer Box 3/4 MDF Kerf",
                "audio_note": f"Tuned near {tuning_hz} Hz with internal bracing and {port_area_sqin} sq. in. high-flow slot port to eliminate port chuffing."
            },
            {
                "badge": "100% OFC Amp Wire Kit",
                "title": f"True-Spec {ofc_wire} Complete Amplifier Wiring Kit + {anl_fuse_amps}A ANL Fuse Holder",
                "price_range": "$69 - $169",
                "amazon_query": f"{ofc_wire.split()[0]} AWG OFC 100% Oxygen Free Copper Amplifier Wiring Kit ANL",
                "audio_note": f"Handles {dc_current_amps}A continuous DC draw without voltage drop. Never use cheap CCA (Copper-Clad Aluminum) wire on {rms_w}W+ amps."
            },
            {
                "badge": "Subwoofer & AGM Power",
                "title": f"{sub_name} + Car Audio AGM Battery / Digital Bass Restoration Processor",
                "price_range": "$129 - $399",
                "amazon_query": f"{sub_name} Subwoofer",
                "audio_note": alt_note
            }
        ],
        "tuning_checklist": [
            f"Set your Monoblock Amplifier's Subsonic (Infrasonic) Filter to {max(20, tuning_hz - 5)} Hz (about 1/2 octave below your {tuning_hz} Hz box tuning) to prevent the cone from unloading and bottoming out on ultra-low notes.",
            f"Set your Low-Pass Filter (LPF) crossover between 70 Hz and 80 Hz (24 dB/octave Linkwitz-Riley slope) and keep Bass Boost at 0 dB to prevent clipped square-wave voice coil burn.",
            f"Add the physical woofer displacement (~0.12–0.18 cu. ft.) plus internal slot port displacement to your {ported_cuft} cu. ft. net airspace when cutting 3/4-inch MDF or Baltic Birch panels.",
            f"Wire your {coil_type} terminals using 12 AWG বা 10 AWG pure OFC speaker wire, and set amplifier gain using a 40 Hz (-5 dB) test tone and digital multimeter ($V = \\sqrt{{\\text{{Watts}} \\times \\text{{Ohms}}}}$)."
        ],
        "faqs": [
            {
                "q": f"What is the best ported box volume and tuning for the {sub_name}?",
                "a": f"For deep daily musical bass, build a {ported_cuft} cubic feet net internal volume enclosure tuned to {tuning_hz} Hz with {port_area_sqin} sq. in. of port area ({port_length_in} inches port length). If you prefer a compact sealed trunk box, use {sealed_cuft} cubic feet net."
            },
            {
                "q": f"What size amplifier and wire gauge do I need for the {sub_name}?",
                "a": f"Pair the {sub_name} with a 1-Ohm or 2-Ohm stable Class-D monoblock amplifier delivering {rms_w}W to {int(round(rms_w * 1.25))}W RMS. Because it draws ~{dc_current_amps} Amps DC at full tilt, run {ofc_wire} power and ground cable with a {anl_fuse_amps}A ANL fuse."
            },
            {
                "q": f"How do I set the amplifier gain voltage for {rms_w}W RMS with a multimeter?",
                "a": f"Using Ohm's Law ($V = \\sqrt{{\\text{{Watts}} \\times \\text{{Ohms}}}}$), at a 1-Ohm final load your target AC speaker terminal voltage is {round((rms_w * 1.0) ** 0.5, 1)}V AC; at a 2-Ohm final load, set gain to {round((rms_w * 2.0) ** 0.5, 1)}V AC using a 40 Hz test tone."
            }
        ]
    }


def generate_sub_data(sub_tuple):
    """Memanggil Gemini 2.5 Flash API; jika gagal otomatis memakai Deterministic Thiele-Small Engine."""
    if not GEMINI_API_KEY:
        return build_deterministic_sub_data(sub_tuple)

    sub_name, size_in, rms_w, coil_type, ported_cuft, tuning_hz, sealed_cuft = sub_tuple
    port_area_sqin = int(round(ported_cuft * 14.0))
    vb_in3 = ported_cuft * 1728.0
    r_equiv = (port_area_sqin / 3.14159) ** 0.5
    port_length_in = max(14.0, min(38.0, round(((14630000.0 * (r_equiv ** 2)) / ((tuning_hz ** 2) * vb_in3)) - (1.463 * r_equiv), 1)))
    dc_amps = int(round(rms_w / (13.8 * 0.80)))
    anl_fuse = int(round(dc_amps * 1.25, -1))
    ofc_wire = "1/0 AWG 100% OFC Copper" if rms_w >= 1200 else "4 AWG 100% OFC Copper"

    prompt = f"""
You are a MECP Master Certified Car Audio Acoustic Engineer & SPL Enclosure Designer. Create an accurate 2026 ported/sealed box volume, Helmholtz port tuning, monoblock amplifier RMS, and OFC wire gauge guide for: "{sub_name}".
Baseline reference specs: Size={size_in} Inch, Power={rms_w}W RMS, Coils={coil_type}, Ported Net Volume={ported_cuft} cu ft @ {tuning_hz} Hz, Port Area={port_area_sqin} sq in, Port Length={port_length_in} in, Sealed Volume={sealed_cuft} cu ft, DC Draw={dc_amps}A, Wire={ofc_wire}.
Return ONLY a valid JSON object matching this exact schema:
{{
  "sub_name": "{sub_name}",
  "seo_title": "{sub_name} Box Specs, Port Tuning (Hz) & Amp Wire Calculator (2026)",
  "meta_description": "Calculate exact ported box cubic feet, Helmholtz port length, monoblock amplifier RMS, and OFC wire gauge for the {sub_name}.",
  "specs": {{
    "size_inches": {size_in},
    "rms_watts": {rms_w},
    "voice_coil_config": "{coil_type}",
    "ported_volume_cuft": {ported_cuft},
    "tuning_freq_hz": {tuning_hz},
    "sealed_volume_cuft": {sealed_cuft},
    "port_area_sqin": {port_area_sqin},
    "port_length_in": {port_length_in},
    "dc_amperage_draw": {dc_amps},
    "recommended_anl_fuse": {anl_fuse},
    "recommended_ofc_wire": "{ofc_wire}"
  }},
  "acoustic_verdict": "3-sentence technical summary stating RMS wattage, optimal ported net cubic feet, tuning Hz, port area/length, DC amp draw, and required OFC wire gauge.",
  "hardware_bundle": [
    {{
      "badge": "Class-D Monoblock Amp",
      "title": "Exact RMS 1-Ohm Stable Class-D Monoblock Amplifier recommendation",
      "price_range": "$159 - $499",
      "amazon_query": "{rms_w}W RMS 1 Ohm Monoblock Car Audio Amplifier",
      "audio_note": "1-sentence clean RMS headroom note"
    }},
    {{
      "badge": "Vented MDF/Birch Box",
      "title": "Exact {size_in}-Inch Ported Subwoofer Enclosure ({ported_cuft} Cu Ft)",
      "price_range": "$119 - $279",
      "amazon_query": "{size_in} Inch Ported Subwoofer Box 3/4 MDF",
      "audio_note": "1-sentence tuning frequency and port area note"
    }},
    {{
      "badge": "100% OFC Amp Wire Kit",
      "title": "True-Spec {ofc_wire} Amplifier Wiring Kit + {anl_fuse}A ANL Fuse",
      "price_range": "$69 - $169",
      "amazon_query": "{ofc_wire.split()[0]} AWG OFC Amplifier Wiring Kit",
      "audio_note": "1-sentence OFC vs CCA voltage drop note"
    }},
    {{
      "badge": "Subwoofer & AGM Power",
      "title": "{sub_name}",
      "price_range": "$129 - $399",
      "amazon_query": "{sub_name}",
      "audio_note": "1-sentence voice coil cooling and excursion note"
    }}
  ],
  "tuning_checklist": [
    "Step 1 regarding subsonic filter setting (5 Hz below port tuning)",
    "Step 2 regarding low-pass filter (LPF) and zero bass boost",
    "Step 3 regarding woofer and port displacement subtraction",
    "Step 4 regarding multimeter AC voltage gain matching (sqrt(Watts * Ohms))"
  ],
  "faqs": [
    {{"q": "What is the best ported and sealed box size for the {sub_name}?", "a": "Exact net cubic feet, tuning Hz, port area, and port length."}},
    {{"q": "What size amp and wire gauge do I need for the {sub_name}?", "a": "Exact RMS wattage, DC amps, ANL fuse, and OFC wire gauge."}},
    {{"q": "What voltage should I set my amp gain to for {rms_w}W RMS?", "a": "Exact AC volts at 1-Ohm, 2-Ohm, and 4-Ohm loads."}}
  ]
}}
"""

    for model_id in ["gemini-2.5-flash", "gemini-2.0-flash"]:
        try:
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                raw_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                raw_text = re.sub(r"\s*```$", "", raw_text)
                parsed = json.loads(raw_text)
                if "specs" in parsed and "hardware_bundle" in parsed:
                    return parsed
        except Exception as e:
            print(f"[WARN] Gemini ({model_id}) notice for '{sub_name}': {e}")

    return build_deterministic_sub_data(sub_tuple)


def build_sub_html_page(data, slug, mon_cfg):
    sub_name = data.get("sub_name", "Car Audio Subwoofer")
    sp = data.get("specs", {})
    size_in = int(safe_float(sp.get("size_inches", 12), 12))
    rms_w = int(safe_float(sp.get("rms_watts", 1000), 1000))
    coil_cfg = sp.get("voice_coil_config", "Dual 2-Ohm (DVC)")
    ported_cuft = round(safe_float(sp.get("ported_volume_cuft", 1.85), 1.85), 2)
    tuning_hz = int(safe_float(sp.get("tuning_freq_hz", 33), 33))
    sealed_cuft = round(safe_float(sp.get("sealed_volume_cuft", 1.10), 1.10), 2)
    port_area = int(safe_float(sp.get("port_area_sqin", 26), 26))
    port_len = round(safe_float(sp.get("port_length_in", 24.5), 24.5), 1)
    dc_amps = int(safe_float(sp.get("dc_amperage_draw", 90), 90))
    anl_fuse = int(safe_float(sp.get("recommended_anl_fuse", 120), 120))
    ofc_wire = sp.get("recommended_ofc_wire", "4 AWG 100% OFC Copper")

    header_cta = mon_cfg.get("header_cta", {})
    header_cta_url = build_amazon_url(header_cta.get("search_query", "1+Ohm+Monoblock+Subwoofer+Amplifier"), mon_cfg)

    schema_graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "SoftwareApplication",
                "name": f"{sub_name} Box Volume, Port Tuning & Amp Wire Calculator",
                "applicationCategory": "UtilitiesApplication",
                "operatingSystem": "Web Browser",
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f.get("q", ""),
                        "acceptedAnswer": {"@type": "Answer", "text": f.get("a", "")}
                    } for f in data.get("faqs", [])
                ]
            }
        ]
    }

    bundle_html = ""
    for item in data.get("hardware_bundle", []):
        amz_url = build_amazon_url(item.get("amazon_query", item.get("title", "Monoblock Subwoofer Amplifier")), mon_cfg)
        bundle_html += f"""
        <div class="bg-zinc-900 border border-zinc-800 rounded-xl p-5 flex flex-col justify-between hover:border-fuchsia-500/60 transition">
          <div>
            <div class="flex items-center justify-between gap-2 mb-2">
              <span class="text-xs font-bold uppercase tracking-wider bg-fuchsia-500/10 text-fuchsia-400 border border-fuchsia-500/20 px-2.5 py-0.5 rounded">{item.get('badge', 'Car Audio')}</span>
              <span class="text-sm font-bold text-emerald-400">{item.get('price_range', '$99+')}</span>
            </div>
            <h3 class="text-base font-bold text-white mt-2">{item.get('title', '')}</h3>
            <p class="text-xs text-zinc-400 mt-2 leading-relaxed">🔊 {item.get('audio_note', '')}</p>
          </div>
          <a href="{amz_url}" target="_blank" rel="nofollow sponsored" class="mt-5 block text-center bg-fuchsia-500 hover:bg-fuchsia-400 text-zinc-950 font-extrabold py-2.5 px-4 rounded-lg text-sm transition shadow-lg">
            Check Price on Amazon →
          </a>
        </div>"""

    # Build Single vs Dual vs Quad Subwoofer Setup Reference Table
    matrix_rows_html = ""
    for cnt, label_s in [(1, f"Single {size_in}\" Setup"), (2, f"Dual {size_in}\" Setup (2 Subs)"), (3, f"Triple {size_in}\" Setup (3 Subs)"), (4, f"Quad {size_in}\" Wall/Trunk (4 Subs)")]:
        tot_rms = rms_w * cnt
        tot_vb = round(ported_cuft * cnt, 2)
        tot_pa = port_area * cnt
        tot_dc = int(round(tot_rms / (13.8 * 0.80)))
        wire_tier = "4 AWG OFC (100A Fuse)" if tot_rms <= 1000 else ("1/0 AWG OFC (200A Fuse)" if tot_rms <= 2200 else "Dual 1/0 AWG OFC + High-Output Alternator")
        matrix_rows_html += f"""
        <tr class="border-b border-zinc-800 hover:bg-zinc-800/40">
          <td class="py-3 px-4 font-bold text-white">{label_s}</td>
          <td class="py-3 px-4 font-bold text-fuchsia-400">{tot_rms:,}W RMS</td>
          <td class="py-3 px-4 text-emerald-400 font-semibold">{tot_vb} ft³ Net ({tot_pa} sq.in Port)</td>
          <td class="py-3 px-4 text-zinc-300">~{tot_dc}A DC Draw</td>
          <td class="py-3 px-4 text-xs text-zinc-300">{wire_tier}</td>
        </tr>"""

    checklist_html = ""
    for idx, step_text in enumerate(data.get("tuning_checklist", []), start=1):
        checklist_html += f"""
        <label class="flex items-start gap-3.5 bg-zinc-900 border border-zinc-800 rounded-xl p-4 cursor-pointer hover:border-zinc-700 transition">
          <input type="checkbox" class="mt-1 w-5 h-5 accent-fuchsia-500 rounded cursor-pointer sub-check">
          <span class="text-sm text-zinc-200 leading-relaxed"><strong>MECP Step {idx}:</strong> {step_text}</span>
        </label>"""

    faqs_html = "".join([
        f"<div class='bg-zinc-900 border border-zinc-800 rounded-xl p-5'><h3 class='font-bold text-white text-base mb-2'>{f.get('q', '')}</h3><p class='text-sm text-zinc-300 leading-relaxed'>{f.get('a', '')}</p></div>"
        for f in data.get("faqs", [])
    ])

    canonical_url = f"{SITE_BASE_URL}/{slug}.html"
    amz_domain = mon_cfg.get("marketplace_domain", "www.amazon.com")
    amz_tag = mon_cfg.get("amazon_associate_tag", "YOUR_AMAZON_TAG-20")

    html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{data.get('seo_title', sub_name)}</title>
  <meta name="description" content="{data.get('meta_description', '')}">
  <link rel="canonical" href="{canonical_url}">
  <meta property="og:title" content="{data.get('seo_title', sub_name)}">
  <meta property="og:description" content="{data.get('meta_description', '')}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical_url}">
  <script src="https://cdn.tailwindcss.com"></script>
  <script type="application/ld+json">{json.dumps(schema_graph)}</script>
</head>
<body class="bg-zinc-950 text-zinc-100 antialiased min-h-screen flex flex-col">
  <header class="border-b border-zinc-800 bg-zinc-900/80 backdrop-blur sticky top-0 z-30">
    <div class="max-w-5xl mx-auto px-4 py-3.5 flex items-center justify-between">
      <a href="index.html" class="text-lg font-black tracking-tight text-white flex items-center gap-2">
        <span class="bg-fuchsia-500 text-zinc-950 px-2 py-0.5 rounded font-black">BASS</span>BoxIndex
      </a>
      <a href="{header_cta_url}" target="_blank" rel="nofollow sponsored" class="text-xs sm:text-sm bg-fuchsia-500 hover:bg-fuchsia-400 text-zinc-950 font-extrabold px-3.5 py-2 rounded-lg transition">
        {header_cta.get('cta_text', 'Shop Monoblock Amps & Boxes →')}
      </a>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-4 py-10 flex-1 w-full">
    <div class="mb-8">
      <div class="flex flex-wrap items-center gap-2.5 mb-3">
        <span class="text-xs font-extrabold uppercase tracking-widest bg-fuchsia-500 text-zinc-950 px-3 py-1 rounded-full">{rms_w:,}W RMS ({size_in}" {coil_cfg})</span>
        <span class="text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded-full">Ported: {ported_cuft} ft³ @ {tuning_hz} Hz | Sealed: {sealed_cuft} ft³</span>
        <span class="text-xs font-semibold bg-zinc-800 text-zinc-300 px-3 py-1 rounded-full">Wire: {ofc_wire} ({anl_fuse}A Fuse)</span>
      </div>
      <h1 class="text-3xl sm:text-4xl font-black text-white leading-tight">{data.get('seo_title', sub_name)}</h1>
      <div class="mt-4 bg-zinc-900 border-l-4 border-fuchsia-500 p-4 rounded-r-xl text-sm text-zinc-200 leading-relaxed">
        <strong>MECP Acoustic & Electrical Verdict:</strong> {data.get('acoustic_verdict', '')}
      </div>
    </div>

    <!-- INTERACTIVE BOX VOLUME, PORT LENGTH, GAIN VOLTAGE & OFC WIRE CALCULATOR -->
    <section class="bg-zinc-900 border border-zinc-800 rounded-2xl p-6 sm:p-8 mb-12 shadow-2xl">
      <h2 class="text-xl font-extrabold text-white mb-2">Interactive {sub_name} Enclosure, Port & Amp Calculator</h2>
      <p class="text-xs text-zinc-400 mb-6">Select subwoofer count, net box volume (ft³), target port tuning frequency (Hz), and final wiring impedance (Ohms) to compute exact slot port length, multimeter gain voltage, and OFC wire size.</p>

      <div class="grid md:grid-cols-2 gap-8 items-center">
        <div class="space-y-5">
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label for="subCountSelect" class="block text-xs font-medium text-zinc-400 mb-1">Number of Subwoofers</label>
              <select id="subCountSelect" class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-fuchsia-500">
                <option value="1" selected>1x {size_in}" Subwoofer ({rms_w}W RMS)</option>
                <option value="2">2x {size_in}" Subwoofers ({rms_w*2}W RMS)</option>
                <option value="4">4x {size_in}" Subwoofers ({rms_w*4}W RMS)</option>
              </select>
            </div>
            <div>
              <label for="ohmSelect" class="block text-xs font-medium text-zinc-400 mb-1">Final Amplifier Load (Ω)</label>
              <select id="ohmSelect" class="w-full bg-zinc-950 border border-zinc-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-fuchsia-500">
                <option value="1.0" selected>1.0 Ohm Parallel Load</option>
                <option value="2.0">2.0 Ohm Final Load</option>
                <option value="4.0">4.0 Ohm Series/Bridged Load</option>
              </select>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-sm font-medium mb-1.5">
              <label for="vbSlider" class="text-zinc-300">Net Internal Box Volume Per Sub (Cu. Ft.)</label>
              <span class="text-fuchsia-400 font-bold"><span id="vbVal">{ported_cuft}</span> ft³ / sub</span>
            </div>
            <input id="vbSlider" type="range" min="0.75" max="4.00" step="0.05" value="{ported_cuft}" class="w-full accent-fuchsia-500 cursor-pointer">
          </div>

          <div>
            <div class="flex justify-between text-sm font-medium mb-1.5">
              <label for="hzSlider" class="text-zinc-300">Target Port Tuning Frequency ($F_b$ in Hz)</label>
              <span class="text-fuchsia-400 font-bold"><span id="hzVal">{tuning_hz}</span> Hz</span>
            </div>
            <input id="hzSlider" type="range" min="26" max="42" step="1" value="{tuning_hz}" class="w-full accent-fuchsia-500 cursor-pointer">
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="bg-zinc-950 border border-fuchsia-500/30 rounded-xl p-4">
            <span class="text-xs uppercase text-fuchsia-400 font-bold">Total Net Box & Port</span>
            <div id="boxSpecOut" class="text-xl sm:text-2xl font-black text-white mt-1">{ported_cuft} ft³ Net</div>
            <p id="portDimOut" class="text-xs text-fuchsia-400 font-semibold mt-1">Port: {port_area} sq.in × {port_len}" L</p>
          </div>

          <div class="bg-zinc-950 border border-emerald-500/30 rounded-xl p-4">
            <span class="text-xs uppercase text-emerald-400 font-bold">Amp Gain & OFC Wire</span>
            <div id="gainVoltOut" class="text-xl sm:text-2xl font-black text-emerald-400 mt-1">31.6V AC</div>
            <p id="wireSpecOut" class="text-xs text-zinc-300 font-semibold mt-1">Need 4 AWG OFC ({anl_fuse}A)</p>
          </div>
        </div>
      </div>

      <div class="mt-6 bg-fuchsia-950/40 border border-fuchsia-500/30 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div id="subAdviceBanner" class="text-sm text-fuchsia-100 font-medium"></div>
        <a id="dynamicSubBtn" href="{header_cta_url}" target="_blank" rel="nofollow sponsored" class="shrink-0 bg-fuchsia-500 hover:bg-fuchsia-400 text-zinc-950 font-extrabold px-4 py-2.5 rounded-lg text-xs uppercase tracking-wider transition">
          Shop Matched Monoblock Amp & Kit on Amazon →
        </a>
      </div>
    </section>

    <!-- 4-CARD HARDWARE BUNDLE -->
    <section class="mb-12">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-extrabold text-white">Complete {sub_name} Amplifier, Enclosure & OFC Wiring Bundle</h2>
        <span class="text-xs text-zinc-400">CEA-2006 & True-Spec 100% OFC Copper</span>
      </div>
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">{bundle_html}</div>
    </section>

    <!-- MULTI-SUBWOOFER SCALING MATRIX TABLE -->
    <section class="mb-12">
      <h2 class="text-2xl font-extrabold text-white mb-4">{sub_name} Single vs. Dual vs. Quad Enclosure & Electrical Chart</h2>
      <div class="overflow-x-auto bg-zinc-900 border border-zinc-800 rounded-xl">
        <table class="w-full text-left border-collapse text-sm">
          <thead>
            <tr class="border-b border-zinc-800 bg-zinc-950/60 text-zinc-400 uppercase text-xs">
              <th class="py-3.5 px-4">Configuration</th>
              <th class="py-3.5 px-4 text-fuchsia-400">Total RMS Power</th>
              <th class="py-3.5 px-4 text-emerald-400">Net Vented Volume & Port</th>
              <th class="py-3.5 px-4">13.8V Alternator Draw</th>
              <th class="py-3.5 px-4">Required OFC Power Wire</th>
            </tr>
          </thead>
          <tbody>{matrix_rows_html}</tbody>
        </table>
      </div>
    </section>

    <!-- MECP TUNING CHECKLIST -->
    <section class="mb-12">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-extrabold text-white">MECP Amplifier Gain, Subsonic & Crossover Tuning Checklist</h2>
        <span id="subBadge" class="text-xs font-bold bg-zinc-800 text-fuchsia-400 px-3 py-1 rounded-full">0 / 4 Completed</span>
      </div>
      <div class="space-y-3">{checklist_html}</div>
    </section>

    <!-- FAQ -->
    <section class="mb-12">
      <h2 class="text-2xl font-extrabold text-white mb-5">Frequently Asked Questions ({sub_name})</h2>
      <div class="space-y-4">{faqs_html}</div>
    </section>
  </main>

  <footer class="border-t border-zinc-800 py-8 text-center text-xs text-zinc-500 px-4">
    <p>© {datetime.now(timezone.utc).year} BassBoxIndex. Independent Thiele-Small Enclosure & Car Audio Electrical Database. As an Amazon Associate, we earn from qualifying purchases.</p>
  </footer>

  <script>
    const singleRms = {rms_w};
    const subSizeIn = {size_in};
    const amzDomain = "{amz_domain}";
    const amzTag = "{amz_tag}";

    const subCountSelect = document.getElementById('subCountSelect');
    const ohmSelect = document.getElementById('ohmSelect');
    const vbSlider = document.getElementById('vbSlider');
    const hzSlider = document.getElementById('hzSlider');
    const vbVal = document.getElementById('vbVal');
    const hzVal = document.getElementById('hzVal');
    const boxSpecOut = document.getElementById('boxSpecOut');
    const portDimOut = document.getElementById('portDimOut');
    const gainVoltOut = document.getElementById('gainVoltOut');
    const wireSpecOut = document.getElementById('wireSpecOut');
    const subAdviceBanner = document.getElementById('subAdviceBanner');
    const dynamicSubBtn = document.getElementById('dynamicSubBtn');

    function recalculateSub() {{
      const count = parseInt(subCountSelect.value, 10);
      const ohms = parseFloat(ohmSelect.value);
      const vbPerSub = parseFloat(vbSlider.value);
      const fbHz = parseInt(hzSlider.value, 10);

      vbVal.textContent = vbPerSub.toFixed(2);
      hzVal.textContent = fbHz;

      const totalVb = vbPerSub * count;
      const totalRms = singleRms * count;
      const portAreaSqIn = Math.round(totalVb * 14.0);

      const vbCubicInches = totalVb * 1728.0;
      const rEquiv = Math.sqrt(portAreaSqIn / Math.PI);
      let portLenIn = ((14630000.0 * rEquiv * rEquiv) / (fbHz * fbHz * vbCubicInches)) - (1.463 * rEquiv);
      portLenIn = Math.max(12.0, Math.min(42.0, portLenIn));

      const targetGainVolts = Math.sqrt(totalRms * ohms);
      const dcAmps = Math.round(totalRms / (13.8 * 0.80));
      const fuseAmps = Math.ceil((dcAmps * 1.25) / 10) * 10;

      let wireLabel = "4 AWG OFC";
      if (totalRms >= 1200) wireLabel = "1/0 AWG OFC";
      else if (totalRms <= 500) wireLabel = "8 AWG / 4 AWG OFC";

      boxSpecOut.textContent = `${{totalVb.toFixed(2)}} ft³ Net`;
      portDimOut.textContent = `Port: ${{portAreaSqIn}} sq.in × ${{portLenIn.toFixed(1)}}" L`;
      gainVoltOut.textContent = `${{targetGainVolts.toFixed(1)}}V AC (@${{ohms}}Ω)`;
      wireSpecOut.textContent = `Wire: ${{wireLabel}} (${{fuseAmps}}A ANL)`;

      const recAmpWatts = Math.ceil((totalRms * 1.15) / 100) * 100;
      const subsonicHz = Math.max(20, fbHz - 5);

      subAdviceBanner.innerHTML = `🔊 <strong>MECP Build Spec:</strong> Power with a <strong>${{recAmpWatts.toLocaleString()}}W RMS Monoblock Amp</strong> wired with <strong>${{wireLabel}} cable</strong>. Set Gain to <strong>${{targetGainVolts.toFixed(1)}}V AC</strong> and Subsonic Filter to <strong>${{subsonicHz}} Hz</strong>.`;
      dynamicSubBtn.href = `https://${{amzDomain}}/s?k=${{recAmpWatts}}W+RMS+1+Ohm+Monoblock+Subwoofer+Amplifier+${{encodeURIComponent(wireLabel)}}+Wiring+Kit&tag=${{amzTag}}`;
    }}

    subCountSelect.addEventListener('change', recalculateSub);
    ohmSelect.addEventListener('change', recalculateSub);
    vbSlider.addEventListener('input', recalculateSub);
    hzSlider.addEventListener('input', recalculateSub);
    recalculateSub();

    const checks = document.querySelectorAll('.sub-check');
    const badge = document.getElementById('subBadge');
    checks.forEach(ch => {{
      ch.addEventListener('change', () => {{
        const done = Array.from(checks).filter(c => c.checked).length;
        badge.textContent = `${{done}} / ${{checks.length}} Completed`;
      }});
    }});
  </script>
</body>
</html>"""

    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(os.path.join(DOCS_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)


def rebuild_portal_sitemap_and_rss(published, mon_cfg):
    header_cta = mon_cfg.get("header_cta", {})
    header_cta_url = build_amazon_url(header_cta.get("search_query", "1+Ohm+Monoblock+Subwoofer+Amplifier"), mon_cfg)

    cards_html = ""
    for item in reversed(published):
        cards_html += f"""
        <a href="{item['slug']}.html" class="block bg-zinc-900 border border-zinc-800 hover:border-fuchsia-500/60 rounded-xl p-5 transition group">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-black uppercase bg-fuchsia-500 text-zinc-950 px-2.5 py-0.5 rounded">{item.get('rms_w', 1000):,}W RMS ({item.get('size_in', 12)}")</span>
            <span class="text-xs text-zinc-400">{item.get('ported_cuft', 1.85)} ft³ @ {item.get('tuning_hz', 33)} Hz</span>
          </div>
          <h2 class="text-base font-bold text-white group-hover:text-fuchsia-400 transition">{item['sub_name']} Box & Amp Calculator</h2>
          <p class="text-xs text-zinc-400 mt-2 line-clamp-2">{item['description']}</p>
          <span class="inline-block mt-4 text-xs font-extrabold text-fuchsia-400">Calculate Box Volume, Port & Amp Wire →</span>
        </a>"""

    index_html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BassBoxIndex — Subwoofer Box Volume, Port Tuning & Amp Wire Calculator (2026)</title>
  <meta name="description" content="Calculate exact ported and sealed subwoofer box cubic feet, Helmholtz slot port length, multimeter gain voltage, and 1/0 AWG OFC wire size for Skar, Sundown, JL Audio, Kicker, and Rockford Fosgate subwoofers.">
  <link rel="canonical" href="{SITE_BASE_URL}/">
  <link rel="alternate" type="application/rss+xml" title="BassBoxIndex RSS Feed" href="{SITE_BASE_URL}/rss.xml">
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-zinc-950 text-zinc-100 min-h-screen flex flex-col">
  <header class="border-b border-zinc-800 bg-zinc-900/80 sticky top-0 z-30 backdrop-blur">
    <div class="max-w-5xl mx-auto px-4 py-3.5 flex items-center justify-between">
      <div class="text-lg font-black text-white flex items-center gap-2">
        <span class="bg-fuchsia-500 text-zinc-950 px-2 py-0.5 rounded font-black">BASS</span>BoxIndex
      </div>
      <a href="{header_cta_url}" target="_blank" rel="nofollow sponsored" class="text-xs sm:text-sm bg-fuchsia-500 hover:bg-fuchsia-400 text-zinc-950 font-extrabold px-3.5 py-2 rounded-lg transition">
        {header_cta.get('cta_text', 'Shop Monoblock Amps & Boxes →')}
      </a>
    </div>
  </header>

  <main class="max-w-5xl mx-auto px-4 py-12 flex-1 w-full">
    <div class="text-center max-w-2xl mx-auto mb-10">
      <h1 class="text-3xl sm:text-5xl font-black text-white tracking-tight">Subwoofer Box Volume, Port Tuning & Amp Wire Database</h1>
      <p class="text-zinc-400 mt-3 text-base sm:text-lg">Select your subwoofer model below to calculate net ported/sealed cubic feet ($V_b$), slot port dimensions ($F_b$), multimeter AC gain voltage, and 100% OFC wire gauge.</p>
      <div class="mt-6">
        <input id="filterInput" type="text" placeholder="Search subwoofer model (e.g. Skar EVL-12, Sundown SA-12, JL Audio 12W7, Kicker CompR, Rockford P3...)" class="w-full bg-zinc-900 border border-zinc-700 rounded-xl px-4 py-3.5 text-sm text-white focus:outline-none focus:border-fuchsia-500">
      </div>
    </div>

    <div id="subGrid" class="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">{cards_html}</div>
  </main>

  <footer class="border-t border-zinc-800 py-8 text-center text-xs text-zinc-500">
    <p>© {datetime.now(timezone.utc).year} BassBoxIndex. As an Amazon Associate, we earn from qualifying purchases.</p>
  </footer>

  <script>
    const filterInput = document.getElementById('filterInput');
    const cards = Array.from(document.getElementById('subGrid').children);
    filterInput.addEventListener('input', (e) => {{
      const q = e.target.value.toLowerCase();
      cards.forEach(c => {{
        c.style.display = c.textContent.toLowerCase().includes(q) ? 'block' : 'none';
      }});
    }});
  </script>
</body>
</html>"""

    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls_xml = f"""  <url>
    <loc>{SITE_BASE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>\n"""

    for item in published:
        urls_xml += f"""  <url>
    <loc>{SITE_BASE_URL}/{item['slug']}.html</loc>
    <lastmod>{item.get('date', today)}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>\n"""

    with open(os.path.join(DOCS_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls_xml}</urlset>""")

    rss_items = ""
    for item in list(reversed(published))[:30]:
        rss_items += f"""    <item>
      <title>{item['title']}</title>
      <link>{SITE_BASE_URL}/{item['slug']}.html</link>
      <guid>{SITE_BASE_URL}/{item['slug']}.html</guid>
      <description>{item['description']}</description>
    </item>\n"""

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>BassBoxIndex Car Audio Subwoofer Enclosure & Amp Database</title>
    <link>{SITE_BASE_URL}/</link>
    <description>Interactive Subwoofer Box Volume, Port Tuning & Amplifier Wire Gauge Calculators</description>
    <atom:link href="{SITE_BASE_URL}/rss.xml" rel="self" type="application/rss+xml" />
    <atom:link href="https://pubsubhubbub.appspot.com/" rel="hub" />
{rss_items}  </channel>
</rss>"""

    with open(os.path.join(DOCS_DIR, "rss.xml"), "w", encoding="utf-8") as f:
        f.write(rss_xml)

    with open(os.path.join(DOCS_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_BASE_URL}/sitemap.xml\n")

    with open(os.path.join(DOCS_DIR, f"{INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY)


def notify_search_engines(new_urls):
    if not SITE_BASE_URL or not new_urls:
        return
    parsed_host = urllib.parse.urlparse(SITE_BASE_URL).netloc
    payload = {
        "host": parsed_host,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{SITE_BASE_URL}/{INDEXNOW_KEY}.txt",
        "urlList": new_urls
    }
    try:
        req = urllib.request.Request(
            "https://api.indexnow.org/indexnow",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[INDEXNOW] Pushed {len(new_urls)} URLs (HTTP {resp.status})")
    except Exception as e:
        print(f"[WARN] IndexNow ping notice: {e}")

    try:
        hub_data = urllib.parse.urlencode({
            "hub.mode": "publish",
            "hub.url": f"{SITE_BASE_URL}/rss.xml"
        }).encode("utf-8")
        req_hub = urllib.request.Request(
            "https://pubsubhubbub.appspot.com/",
            data=hub_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST"
        )
        with urllib.request.urlopen(req_hub, timeout=15) as resp_hub:
            print(f"[WEBSUB] Google PubSubHubbub ping status: {resp_hub.status}")
    except Exception as e:
        print(f"[WARN] WebSub ping notice: {e}")


def main():
    published = load_json(PUBLISHED_FILE, [])
    mon_cfg = load_json(MONETIZATION_FILE, {})
    published_slugs = {item["slug"] for item in published}

    candidates = []
    if CUSTOM_SUB:
        candidates.append((CUSTOM_SUB.strip(), 12, 1000, "Dual 2-Ohm (DVC)", 1.85, 33, 1.15))
    candidates.extend(SEED_SUBWOOFERS)
    candidates.extend(discover_google_subwoofer_queries())

    new_urls = []
    count = 0

    for sub_tuple in candidates:
        if count >= PAGES_PER_RUN:
            break
        s_name = sub_tuple[0]
        slug = slugify(f"{s_name}-box-specs-amp-wire-calculator")
        if slug in published_slugs:
            continue

        print(f"[ENGINE] Generating subwoofer enclosure & amp calculator for: {s_name}...")
        try:
            data = generate_sub_data(sub_tuple)
            build_sub_html_page(data, slug, mon_cfg)
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            sp = data.get("specs", {})

            published.append({
                "sub_name": data.get("sub_name", s_name),
                "slug": slug,
                "title": data.get("seo_title", f"{s_name} Box & Amp Calculator"),
                "description": data.get("meta_description", ""),
                "size_in": int(safe_float(sp.get("size_inches", sub_tuple[1]), sub_tuple[1])),
                "rms_w": int(safe_float(sp.get("rms_watts", sub_tuple[2]), sub_tuple[2])),
                "ported_cuft": round(safe_float(sp.get("ported_volume_cuft", sub_tuple[4]), sub_tuple[4]), 2),
                "tuning_hz": int(safe_float(sp.get("tuning_freq_hz", sub_tuple[5]), sub_tuple[5])),
                "date": today
            })
            published_slugs.add(slug)
            if SITE_BASE_URL:
                new_urls.append(f"{SITE_BASE_URL}/{slug}.html")
            count += 1
            time.sleep(2)
        except Exception as e:
            print(f"[ERROR] Failed building {s_name}: {e}")

    save_json(PUBLISHED_FILE, published)
    rebuild_portal_sitemap_and_rss(published, mon_cfg)
    if new_urls and SITE_BASE_URL:
        new_urls.append(f"{SITE_BASE_URL}/")
        notify_search_engines(new_urls)
    print(f"[DONE] Published {count} new subwoofer box & amplifier calculator pages.")


if __name__ == "__main__":
    main()
