from functools import lru_cache

from config import Settings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@lru_cache
def get_settings():
    return Settings()


@lru_cache
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    settings = get_settings()
    driver = webdriver.Chrome(settings.chrome_driver, options=chrome_options)

    return driver
