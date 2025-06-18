
import re
import pandas as pd

def normalize_text(name: str) -> str:
    if not isinstance(name, str):
        return ""
    name = name.lower()
    name = name.replace("®", "").replace("™", "")
    name = name.replace("processor", "")
    name = re.sub(r"[^\w\s-]", "", name)  # preserve hyphens in model names
    name = re.sub(r"\s+", " ", name).strip()
    return name

def reorder_vendor(name: str) -> str:
    # Matches formats like "Core i5-7200U - Intel"
    match = re.match(r"(.+?)\s*-\s*(intel|amd|arm|apple|qualcomm|via|motorola|samsung|ibm|nvidia|rockchip|hisilicon|centaur|zhaoxin)$", name, re.IGNORECASE)
    if match:
        chip, vendor = match.groups()
        return f"{vendor.strip()} {chip.strip()}"
    return name

def normalize_processor_name(name: str) -> str:
    name = normalize_text(name)
    name = reorder_vendor(name)
    return name.strip()

def normalize_processor_column(column) -> pd.Series:
    return column.apply(normalize_processor_name)