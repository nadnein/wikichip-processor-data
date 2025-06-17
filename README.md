# Wikichip Processor Scraper

This project fetches processor information from [WikiChip](https://en.wikichip.org) using its public MediaWiki API. It collects data such as:

- Processor name
- Launch date
- Thermal Design Power (TDP)
- Source
- Core count
- Thread count

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

## 📚 License and Data Source

This project uses data from [WikiChip](https://en.wikichip.org), which is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/).

> © WikiChip LLC and contributors.  
> The data retrieved and processed in this project is **for non-commercial use only** and adheres to the terms of the CC BY-NC-SA 4.0 license.  
> Please refer to [WikiChip’s licensing statement](https://en.wikichip.org/wiki/wikichip:general_disclaimer) for more information.
