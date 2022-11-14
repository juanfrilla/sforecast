from time import sleep
from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
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
        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=options)
    
    def page_is_loaded(self):
        x = self.driver.execute_script("return document.readyState")
        if x == "complete":
            return True
        return False

    def prepare_site(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 15).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"/html/body/div[5]/iframe")))
        self.driver.find_element(By.XPATH, "/html/body/div/div[2]/div[5]/button[2]").click()
        square = self.driver.find_element(By.CLASS_NAME, "js-incentive.not-in-print.forecast-table__incentive")
        self.driver.execute_script("arguments[0].remove();", square)
    
    
    def scrape(self):
        forecast = {}
        if self.page_is_loaded():
            s = BeautifulSoup(self.driver.page_source, "html.parser")
            drn_list = ["time","wave-height", "periods", "energy", "wind", "wind-state"]
            for row_name in drn_list:
                forecast[row_name] = []
                row = s.find('tr', {'data-row-name': row_name})
                cells = row.find_all("td")
                for cell in cells:
                    if cell.text.strip() != '':
                        forecast[row_name].append(cell.text)
        return forecast
                                

if __name__ == "__main__":
    scraper = ForecastScraper()

    urls = {
        "Arrieta-Punta-Jameos": "https://www.surf-forecast.com/breaks/Arrieta/forecasts/latest/six_day",
        "Caleta de Caballo": "https://www.surf-forecast.com/breaks/Caletade-Cabello/forecasts/latest/six_day",
        "El Golfo": "https://www.surf-forecast.com/breaks/El-Golfo/forecasts/latest/six_day",
        "Jameos del Agua": "https://www.surf-forecast.com/breaks/Jameosdel-Agua/forecasts/latest/six_day",
        "Izquierda de la Santa": "https://www.surf-forecast.com/breaks/La-Santa-The-Slab/forecasts/latest/six_day",
        "Famara-Papelillo": "https://www.surf-forecast.com/breaks/Playade-Famara_1/forecasts/latest/six_day",
        "Janubio": "https://www.surf-forecast.com/breaks/Playadel-Janubio/forecasts/latest/six_day",
        "San Juan": "https://www.surf-forecast.com/breaks/San-Juan/forecasts/latest/six_day"
    }


    scraper.prepare_site(urls['Izquierda de la Santa'])
    forecast = scraper.scrape()
    df = utils.dict_to_df(forecast)
    df = utils.add_days_to_df(df)

    df = df.drop(df[(df["wind-state"] != "off") & (df["wind-state"] != "cross-off")].index)


    df = df[["days", "time","wave-height", "periods", "energy", "wind", "wind-state"]]
    utils.df_to_csv("forecast.csv", df)
    scraper.driver.quit()