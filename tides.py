from bs4 import BeautifulSoup
import os, datetime, pandas as pd
from typing import Dict
from selenium import webdriver
from selenium.webdriver.chrome.service import Service



class TidesScraper(object):

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--start-maximized")
        ser = Service(r"/usr/bin/chromedriver")
        self.driver = webdriver.Chrome(service=ser, options=options)
        self.link = "https://www.temperaturadelmar.es/europa/lanzarote/arrecife/tides.html"


    def page_is_loaded(self):
        x = self.driver.execute_script("return document.readyState")
        if x == "complete":
            return True
        return False

    def scrape(self) -> Dict:
        self.driver.get(self.link)
        hours_dict = {}
        if self.page_is_loaded():
            s = BeautifulSoup(self.driver.page_source, "html.parser")
            tables = s.find_all("table", class_="table table-bordered")
            horas = []
            for table in tables:
                tablebody = table.find("tbody")
                rows = tablebody.find_all("tr")
                hora = []
                for row in rows:
                    cells = row.find_all("td")
                    for cell in cells:
                        if cell.text == "pleamar" or cell.text == "bajamar": #TODO poner aqui directamente subiendo hasta las o bajando hasta las
                            hora.append(cell.text.replace("amar", ""))
                        elif ":" in cell.text:
                            ple_baj = hora.pop()
                            text_to_insert = f"{ple_baj} {cell.text}h"
                            hora.insert(len(hora), text_to_insert)
                horas.append(hora)
                for hora in horas:
                    if len(hora) == 3:
                        hora.append(None)
            for hora in horas:
                hours_dict[self.get_day_name(horas.index(hora))] = hora
        return hours_dict

    def mareas_to_df(self, dict: Dict) -> pd.DataFrame:
        df = pd.DataFrame(dict)
        return df

    def df_to_txt(self, df: pd.DataFrame) -> None:
        if os.path.exists("mareas.txt"):
            os.remove("mareas.txt")
        with open("mareas.txt", "a") as f:
            dfAsString = df.to_string(header=True, index=False)
            f.write(dfAsString)

    def get_day_name(self, add: float) -> str:
        today = datetime.date.today()
        day = today + datetime.timedelta(days=add)
        day_name_number = day.strftime("%d-%m, %A")

        return day_name_number

