# src/main.py ফাইলের শুরুতে যোগ করুন
import os
import platform

def is_cloud_environment():
    """চেক করে কোড ক্লাউডে চলছে কিনা"""
    cloud_indicators = [
        'STREAMLIT_CLOUD' in os.environ,
        'STREAMLIT_SHARING' in os.environ,
        'STREAMLIT_RUNTIME' in os.environ,
        'REPLIT_DB_URL' in os.environ,
        'KOYEB_APP' in os.environ,
        'RAILWAY_ENVIRONMENT' in os.environ
    ]
    return any(cloud_indicators)

# প্যাকেট স্নিফার চালানোর আগে চেক করুন
if not is_cloud_environment():
    from src.data_collection.packet_sniffer import start_sniffing
    start_sniffing()
else:
    logging.info("প্যাকেট স্নিফিং ক্লাউডে ডিজেবল করা হয়েছে")
# to test logging
from utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Logger is working!")


# run: python src/main.py


# 1. USING API_KEY
#from data_collection.api_collector import collect_data
#data = collect_data()
#print("Collected Data:", data)
# python src/main.py


# 2. using web scrapping
#from data_collection.scraper_collector import scrape_data

#url = "https://odibets.com/aviator"  # Replace with actual URL
#crash_value = scrape_data(url)
#print("Scraped Crash Value:", crash_value)



# USING OCR
#from data_collection.ocr_collector import extract_text_from_image

#crash_value = extract_text_from_image("path/to/image.png")  # Replace with actual image path
#print("Extracted Crash Value from Image:", crash_value)

# run: python src/main.py


# 3. USING PACKET SNIFFER
from data_collection.packet_sniffer import start_sniffer

start_sniffer()  # Be cautious; this will capture live packets!










from src.data_collection.api_collector import collect_data
from src.data_collection.scraper_collector import scrape_data
from src.data_collection.ocr_collector import extract_text_from_image
from src.data_collection.packet_sniffer import start_sniffer
from src.analysis.prediction_engine import PredictionEngine

# Example usage:
def main():
    # Collect data (choose one method or use all)
    data = collect_data()
    print("Collected Data:", data)

    url = "https://example.com/aviator"  # Replace with actual URL
    crash_value = scrape_data(url)
    print("Scraped Crash Value:", crash_value)

    crash_value_from_image = extract_text_from_image("path/to/image.png")  # Replace with actual image path
    print("Extracted Crash Value from Image:", crash_value_from_image)

    # Start packet sniffer (use with caution)
    # start_sniffer()

    # Analyze patterns and predict
    engine = PredictionEngine()
    prediction = engine.predict()
    print("Prediction:", "Win" if prediction else "Loss")

if __name__ == "__main__":
    main()
