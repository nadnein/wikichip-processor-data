from src.processor_parser import get_all_page_titles, get_processor_data
from src.utils import save_titles_to_file, load_titles_from_file, save_results_to_csv
from src.config import BATCH_SIZE

def main():
    titles = load_titles_from_file()
    if not titles:
        titles = get_all_page_titles()
        save_titles_to_file(titles)

    print("Fetching processor details...")
    processors = get_processor_data(titles, batch_size=BATCH_SIZE)

    save_results_to_csv(
        processors,
        columns=["Processor", "Launch Date", "Source", "TDP (W)", "Cores", "Threads"]
    )

if __name__ == "__main__":
    main()