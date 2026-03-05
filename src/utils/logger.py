import logging
import sys
from datetime import datetime

def get_logger(name):
    """
    লগার তৈরি করার ফাংশন
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # কনসোল হ্যান্ডলার
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # ফাইল হ্যান্ডলার (ঐচ্ছিক)
        file_handler = logging.FileHandler(f'logs/{datetime.now().strftime("%Y%m%d")}.log')
        file_handler.setLevel(logging.DEBUG)
        
        # ফরম্যাটার
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger
