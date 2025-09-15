# Wikichip Processor Scraper

This project fetches processor information from [WikiChip](https://en.wikichip.org) using its public MediaWiki API. It collects data such as:

- Processor name
- Launch date
- Source
- Intended Usage
- Thermal Design Power (TDP)
- Core count
- Thread count
- Process
- Die Area

The results are saved into a structured CSV file for further analysis.

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/wikichip-processor-scraper.git
cd wikichip-processor-scraper
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 How to Run the Scripts

### 1. `scrape_processors.py`

The `scrape_processors.py` script fetches processor data from WikiChip and saves it into a CSV file. It performs the following tasks:
- Fetches processor titles from WikiChip (if not already saved in a JSON file).
- Retrieves detailed processor data using the WikiChip API.
- Appends additional processor data from an external processors CSV file.
- Normalizes processor names and removes duplicates.
- Adds default rows for usage type categories.
- Saves the final processor data into a CSV file.

#### **Example Usage:**
```bash
python -m scripts.scrape_processors --input-titles data/page_titles.json --cpu-tdp-csv data/CPU_TDP_wikichip.csv --external-csv data/external_processors.csv
```

#### **Arguments:**
- `--input-titles`: Path to the JSON file containing processor titles (default: `data/page_titles.json`).
- `--input-csv`: Path to the input CSV file for processor data (default: `data/CPU_TDP_wikichip.csv`).
- `--ampere-csv`: Path to the Ampere processors CSV file (default: `data/ampere_processors.csv`).
- `--output-csv`: Path to the output CSV file where the final data will be saved (default: `data/CPU_TDP_wikichip.csv`).

---

### 2. `analyze_proc_tables.py`

The `analyze_proc_tables.py` script compares two processor tables (CSV files) and performs the following analyses:
- Finds matching processor names between the two tables.
- Identifies differences in TDP and core counts for matching processors.
- Saves unmatched processors from each table into separate CSV files.

#### **Usage:**
```bash
python -m scripts.analyze_proc_tables data/CPU_TDP_wikichip.csv data/CPU_TDP.csv --output-dir data/analysis_results
```

#### **Arguments:**
- `input_file1`: Path to the first input CSV file (e.g., `data/CPU_TDP_wikichip.csv`).
- `input_file2`: Path to the second input CSV file (e.g., `data/CPU_TDP.csv`).
- `--output-dir`: Directory where the analysis results will be saved (default: `data/analysis_results`).

#### **Outputs:**
- `matching_processor_names.csv`: Processors with matching names in both tables.
- `diff_cores_or_tdp.csv`: Processors with significant differences in TDP or core counts.
- `unmatched_<input_file1>.csv`: Processors found in the first table but not in the second.
- `unmatched_<input_file2>.csv`: Processors found in the second table but not in the first.

---

## 📚 License and Data Source

This project uses data from [WikiChip](https://en.wikichip.org), which is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/).

> © WikiChip LLC and contributors.  
> The data retrieved and processed in this project is **for non-commercial use only** and adheres to the terms of the CC BY-NC-SA 4.0 license.  
> Please refer to [WikiChip’s licensing statement](https://en.wikichip.org/wiki/wikichip:general_disclaimer) for more information.
