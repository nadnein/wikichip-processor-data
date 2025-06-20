from .config import API_URL, MAX_RETRIES, DELAY_RANGE
import random
import time
from datetime import datetime, timezone
import requests
import json

session = requests.Session()


def get_all_page_titles():
    """
    Retrieves all page titles listed in the 'all microprocessor models' category.
    """
    titles = []
    cont = None

    while True:
        params = {
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": "Category:all microprocessor models",
            "cmlimit": "50"
        }
        if cont:
            params["cmcontinue"] = cont

        response = session.get(API_URL, params=params)

        try:
            resp = response.json()
        except Exception as e:
            print("❌ Failed to parse JSON!")
            print("Status code:", response.status_code)
            print("Raw response (first 300 chars):")
            print(response.text[:300])
            raise e

        members = resp.get("query", {}).get("categorymembers", [])
        titles.extend([m["title"] for m in members])

        cont = resp.get("continue", {}).get("cmcontinue")
        if not cont:
            break

        time.sleep(1)

    return titles



def get_processor_data(titles, batch_size):
    """
    Fetches processor metadata from WikiChip for given titles.

    Returns:
        List of tuples: (title, source, launch_date, tdp, cores, threads)
    """
    results = []
    total_batches = (len(titles) + batch_size - 1) // batch_size

    for batch_idx in range(0, len(titles), batch_size):
        batch = titles[batch_idx:batch_idx + batch_size]
        query_str = " OR ".join(f"[[{t}]]" for t in batch)
        ask_query = f"{query_str}|?tdp|?first launched|?core count|?thread count|?model|?name|?market segment"

        params = {
            "action": "ask",
            "format": "json",
            "query": ask_query
        }

        for attempt in range(MAX_RETRIES):
            try:
                response = session.get(API_URL, params=params)
                resp = response.json()

                # 🚨 Check for API-level errors (e.g. query too complex)
                if "error" in resp:
                    print(f"🚨 API Error in batch {batch_idx // batch_size + 1}/{total_batches}")
                    print("➡️  Message:", json.dumps(resp["error"], indent=2))
                    break  # Skip this batch entirely
                break  # success
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed for batch {batch_idx // batch_size + 1}/{total_batches}")
                print("Status code:", response.status_code if 'response' in locals() else "unknown")
                print("First part of response:", response.text[:300] if 'response' in locals() else "no response")
                time.sleep(5)
        else:
            print(f"❌ Skipping batch {batch_idx // batch_size + 1} after {MAX_RETRIES} failed attempts.")
            continue

        # If no error, process the actual data
        ask_results = resp.get("query", {}).get("results", {})

        for title, data in ask_results.items():
            printouts = data.get("printouts", {})
            launch_date_list = printouts.get("first launched", [])
            tdp_list = printouts.get("tdp", [])
            cores_list = printouts.get("core count", [])
            threads_list = printouts.get("thread count", [])
            market_segment_list = printouts.get("market segment", [])

            launch_date = launch_date_list[0]["timestamp"] if launch_date_list and "timestamp" in launch_date_list[0] else None
            tdp = tdp_list[0]["value"] if tdp_list and "value" in tdp_list[0] else None
            cores = int(cores_list[0]) if cores_list else None
            threads = int(threads_list[0]) if threads_list else None
            # Join all market segments as a single string, or None if empty
            market_segment = "; ".join(str(seg) for seg in market_segment_list) if market_segment_list else None

            if tdp and cores:
                launch_fmt = datetime.fromtimestamp(int(launch_date), tz=timezone.utc).strftime('%Y-%m-%d') if launch_date else ""
                display = data.get("displaytitle", title)
                source = data.get("fullurl", None)
                results.append((display, launch_fmt, source, market_segment, tdp, cores, threads))


        wait = round(random.uniform(*DELAY_RANGE), 2)
        print(f"✅ Finished batch {batch_idx // batch_size + 1}/{total_batches} — sleeping {wait}s")
        time.sleep(wait)

    return results

