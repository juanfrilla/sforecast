from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

import utils
import pandas as pd


class ForecastScraper(object):

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")

        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        self.driver = webdriver.Chrome(
            executable_path=r"/usr/bin/chromedriver", chrome_options=options)

    def page_is_loaded(self):
        x = self.driver.execute_script("return document.readyState")
        if x == "complete":
            return True
        return False

    def accept_conditions(self):
        try:
            WebDriverWait(self.driver, 15).until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.XPATH, "/html/body/div[5]/iframe")))
            self.driver.find_element(
                By.XPATH, "/html/body/div/div[2]/div[5]/button[2]").click()
        except:
            pass

    def prepare_site(self):
        square = self.driver.find_element(
            By.CLASS_NAME,
            "js-incentive.not-in-print.forecast-table__incentive")
        self.driver.execute_script("arguments[0].remove();", square)

    def scrape(self):
        forecast = {}
        if self.page_is_loaded():
            s = BeautifulSoup(self.driver.page_source, "html.parser")
            drn_list = [
                "time", "wave-height", "periods", "energy", "wind",
                "wind-state"
            ]
            for row_name in drn_list:
                forecast[row_name] = []
                row = s.find('tr', {'data-row-name': row_name})
                cells = row.find_all("td")
                for cell in cells:
                    if cell.text.strip() != '':
                        forecast[row_name].append(cell.text)
        return forecast
