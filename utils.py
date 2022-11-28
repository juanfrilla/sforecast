import os, pandas as pd
from typing import Dict
from datetime import datetime, timedelta

from threadingresult import ThreadWithReturnValue
from forecast_scraper import ForecastScraper

from datetime import time, datetime

from tides_scraper import TidesScraper


def df_to_csv(path, df: pd.DataFrame) -> None:
    if os.path.exists(path):
        os.remove(path)

    df.to_csv(path, index=False)

    if os.path.exists(path):
        os.system(f"explorer.exe {path}")


def dict_to_df(dict: Dict) -> pd.DataFrame:
    df = pd.DataFrame(dict)
    return df


def add_days_to_forecast(forecast):
    time_list = forecast['time']
    days_list = []
    date = datetime.now()
    for index, time in enumerate(time_list):
        if time == "AM" and index != 0:
            date += timedelta(days=1)
            days_list.append(date.strftime("%m-%d, %A"))
        else:
            days_list.append(date.strftime("%m-%d, %A"))
    forecast['days'] = days_list
    return forecast


def add_beach_to_forecast(forecast, beach):
    count_row = len(forecast)
    same_beach_list = [beach for i in range(0, count_row)]

    forecast['beach'] = same_beach_list

    return forecast


def combine_df(df1, df2):
    df = pd.concat([df1, df2], axis=0, ignore_index=True)
    return df


def combine_df_tides(df, tides_data):
    tides_data = {k: tides_data[k] for k in list(tides_data)[:12]}

    for (index, row) in df.iterrows():
        if 'AM' in row['time'] and  row['days'] in tides_data and 'Subiendo' in tides_data[row['days']][0]:
            value = tides_data[row['days']][0]

        elif 'AM' in row['time'] and  row['days'] in tides_data and 'Bajando' in tides_data[row['days']][0]:
            value = tides_data[row['days']][1]
        
        # elif 'Bajando' in tides_data[row['days']][0] and 'Bajando' in tides_data[row['days']][1]: TODO corregir que está bajando en dos
        #     value = tides_data[row['days']][1]
        #     print("sssssir", tides_data[row['days']])

        elif 'PM' in row['time'] and  row['days'] in tides_data and 'Subiendo' in tides_data[row['days']][1]:
            value = tides_data[row['days']][1]
        elif 'PM' in row['time'] and  row['days'] in tides_data and  'Bajando' in tides_data[row['days']][1] and len(tides_data[row['days']]) > 2:
            value = tides_data[row['days']][2]
        elif 'Night' in row['time'] and  row['days'] in tides_data and len(tides_data[row['days']]) > 2:
            value = tides_data[row['days']][2]
        elif 'Night' in row['time'] and  row['days'] in tides_data and  len(tides_data[row['days']]) < 2:
            value = "-"
        else:
            value = "-"
        df.loc[index, "tides"] = value
    return df


def hour_AM_PM(hours_dict):
    AM = [time(0, 0, 0), time(12, 0, 0)]
    PM = [time(12, 0, 0), time(20, 0, 0)]
    Night = [time(20, 0, 0), time(23, 59, 0)]

    new_dict = {}

    for key, value in hours_dict.items():
        new_list = []
        for element in value:
            if element is not None:
                h_m = element.split(" ")[1].replace("h", "")
                time_to_check = datetime.strptime(f"{h_m}:00",
                                                  "%H:%M:%S").time()

                if time_to_check > AM[0] and time_to_check < AM[1]:
                    text = check_ple_baj(f"{element} AM")
                elif time_to_check > PM[0] and time_to_check < PM[1]:
                    text = check_ple_baj(f"{element} PM")
                elif time_to_check > Night[0] and time_to_check < Night[1]:
                    text = check_ple_baj(f"{element} Night")
                new_list.append(text)
        new_dict[key] = new_list

    return new_dict


def check_ple_baj(text):
    if "ple" in text:
        return text.replace("ple", "Subiendo hasta las")
    elif "baj" in text:
        return text.replace("baj", "Bajando hasta las")
#TODO Posiblemente ponerle desde las hasta las 

def get_greater_hour(my_dict):
    new_dict = {}
    for key, value in my_dict.items():
        AM_list = []
        PM_list = []
        Night_list = []

        for element in value:
            if element is not None and "AM" in element:
                AM_list.append(element)
            elif element is not None and "PM" in element:
                PM_list.append(element)
            elif element is not None and "Night" in element:
                Night_list.append(element)

        #TODO quedarme de aqui la subida y no la bajada
        if len(AM_list) > 1 and Night_list != []:
            new_dict[key] = [AM_list[1], PM_list[0], Night_list[0]]
        elif (len(AM_list) < 1 and Night_list != []) or (len(PM_list) < 1
                                                         and Night_list != []):
            new_dict[key] = [AM_list[0], PM_list[0], Night_list[0]]
        elif len(AM_list) > 1 and Night_list == []:
            new_dict[key] = [AM_list[1], PM_list[0]]
        elif (len(AM_list) < 1 and Night_list == []) or (len(PM_list) < 1
                                                         and Night_list == []):
            new_dict[key] = [AM_list[0], PM_list[0]]

        elif len(PM_list) > 1 and Night_list != []:
            new_dict[key] = [AM_list[0], PM_list[1], Night_list[0]]
        elif len(PM_list) > 1 and Night_list == []:
            new_dict[key] = [AM_list[0], PM_list[1]]

    return new_dict


def process_scrape_forecast(url, beach, pos):
    fc_scraper = ForecastScraper()

    fc_scraper.driver.get(url)

    if pos == 0:
        fc_scraper.accept_conditions()

    fc_scraper.prepare_site()
    forecast = fc_scraper.scrape()
    df = dict_to_df(forecast)
    fc_scraper.driver.quit()
    return [beach, df]

def process_scrape_tides():
    tide_scraper = TidesScraper()
    tides = tide_scraper.scrape()
    tide_scraper.driver.quit()
    return [None, tides]


def scrape_multiple_sites(urls):
    threads = list()

    x = ThreadWithReturnValue(target=process_scrape_tides, args=())
    threads.append(x)
    x.start()

    forecast = pd.DataFrame()

    for index, element in enumerate(urls):
        url = element['url']
        beach = element['beach']
        x = ThreadWithReturnValue(target=process_scrape_forecast,
                                  args=(url, beach, index))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        [beach, results] = thread.join()
        if beach is not None:
            df = add_days_to_forecast(results)
            df = add_beach_to_forecast(df, beach)
        else:
            tides = results
            tides = hour_AM_PM(tides)
            tides = get_greater_hour(tides)
            continue

        if df is not None and tides is not None:
            df = combine_df_tides(df, tides)
            forecast = combine_df(forecast, df)

    return forecast