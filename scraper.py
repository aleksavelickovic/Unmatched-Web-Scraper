from time import sleep

import pytest
import time

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
import chromedriver_autoinstaller
import undetected_chromedriver as uc

SLEEP_TIME = 25  # Prilagoditi broj shodno brzini vase internet konekcije


# @pytest.fixture()
# def browser():
#     if chromedriver_autoinstaller.get_chrome_version() is None:
#         chromedriver_autoinstaller.install()
#     # neophodno odraditi ovo zbog problema sa CORS
#     options = webdriver.ChromeOptions()
#     options.add_argument("--disable-web-security")
#     options.add_argument("--disable-site-isolation-trials")
#     # kreiraj instancu drajvera za test
#     driver = uc.Chrome(options=options)
#
#     driver.implicitly_wait(10)
#
#     yield driver
#
#     driver.quit()


def test_scrape_page():
    options = webdriver.ChromeOptions()
    # neophodno odraditi ovo zbog problema sa CORS
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-site-isolation-trials")
    browser = uc.Chrome(options=options)
    browser.implicitly_wait(10)

    browser.get("https://www.umleague.net/fighterstats")

    select_hero_element = browser.find_element(By.ID, 'selectHero')
    # select_hero_element.click()
    browser.execute_script("arguments[0].scrollIntoView();",
                           select_hero_element)  # Nije obavezno ali cisto da se vidi sta se desava

    limiter = 0
    select_hero = Select(select_hero_element)
    for option in select_hero.options:
        while limiter < 12:
            option.click()
            sleep(SLEEP_TIME)
            limiter += 1

    # for request in driver.requests

    browser.quit()

# sleep(5)
