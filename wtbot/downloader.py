import base64
import multiprocessing
import os
import re

from dependencies import get_driver, get_settings
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

settings = get_settings()


class image_src_regex:
    def __init__(self, locator, regex):
        self.locator = locator
        self.regex = regex

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        src = element.get_attribute("src")

        return element if bool(re.search(self.regex, src)) else False


def get_encoded_captcha(driver):
    captcha_loaded_regex = fr"{settings.captcha_not_loaded}([\w\+\/]+)"

    # wait till captcha is loaded
    try:
        element = WebDriverWait(driver, 10).until(
            image_src_regex((By.ID, settings.captcha_img_id), captcha_loaded_regex)
        )
    except TimeoutException:
        raise TimeoutException

    # get captcha encoded with base64
    src = element.get_attribute("src")
    encoded_captcha = src[len(settings.captcha_not_loaded) :]

    return encoded_captcha


def get_decoded_captcha(driver):
    encoded_captcha = get_encoded_captcha(driver)
    decoded_captcha = base64.b64decode(encoded_captcha)

    return decoded_captcha


def refresh_captcha(driver):
    # mark captcha img src attr as not loaded
    img = driver.find_element_by_id(settings.captcha_img_id)
    driver.execute_script(
        f"arguments[0].setAttribute('src','{settings.captcha_not_loaded}')",
        img,
    )

    # update captcha
    refresh_button = driver.find_element_by_xpath(
        '//*[@id="loginPage:SiteTemplate:siteLogin:'
        'loginComponent:loginForm:j_id169"]/div/div/img'
    )
    refresh_button.click()


def download_captchas(count):
    driver = get_driver()
    driver.get(settings.target_uri)
    proc = multiprocessing.current_process()

    i = count

    while i:
        try:
            decoded_captcha = get_decoded_captcha(driver)

            # save captcha to os
            dest = os.path.join(settings.media_root, f"{proc.ident}_{count - i}.png")
            with open(dest, "wb") as f:
                f.write(decoded_captcha)

            print(f"Download {count - i + 1} of {count} in proc {proc.name}")

            refresh_captcha(driver)

            i -= 1
        except StaleElementReferenceException:
            driver.refresh()
            continue


if __name__ == "__main__":
    workers_count = 10
    count_per_worker = [1000] * workers_count

    with multiprocessing.Pool(workers_count) as p:
        p.map(download_captchas, count_per_worker)
