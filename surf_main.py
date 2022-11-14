import utils
import warnings

warnings.filterwarnings('ignore')
import pandas as pd

urls = [{
        "beach":
        "Arrieta-Punta-Jameos",
        "url":
        "https://www.surf-forecast.com/breaks/Arrieta/forecasts/latest/six_day"
    }, {
        "beach":
        "Caleta de Caballo",
        "url":
        "https://www.surf-forecast.com/breaks/Caletade-Cabello/forecasts/latest/six_day"
    }, {
        "beach":
        "El Golfo",
        "url":
        "https://www.surf-forecast.com/breaks/El-Golfo/forecasts/latest/six_day"
    }, {
        "beach":
        "Jameos del Agua",
        "url":
        "https://www.surf-forecast.com/breaks/Jameosdel-Agua/forecasts/latest/six_day"
    }, {
        "beach":
        "Izquierda de la Santa",
        "url":
        "https://www.surf-forecast.com/breaks/La-Santa-The-Slab/forecasts/latest/six_day"
    },
    {
        "beach":
        "Famara-Papelillo",
        "url":
        "https://www.surf-forecast.com/breaks/Playade-Famara_1/forecasts/latest/six_day"
    },  {
        "beach":
        "Janubio",
        "url":
        "https://www.surf-forecast.com/breaks/Playadel-Janubio/forecasts/latest/six_day"
    }, {
        "beach":
        "San Juan",
        "url":
        "https://www.surf-forecast.com/breaks/San-Juan/forecasts/latest/six_day"
    }
]

if __name__ == "__main__":
    df = utils.scrape_multiple_sites(urls)

    
    df = df.drop(df[(df["wind-state"] != "off") & (df["wind-state"] != "cross-off")].index)

    df = df.drop(df[(df["time"] == "Night")].index)


    df = df[[
        "days", "time", "wave-height", "periods", "energy", "wind",
        "wind-state", "beach", "tides"
    ]]

    df.sort_values(by=["days", "beach"], inplace=True, ascending=[True, True])

    utils.df_to_csv("forecast.csv", df)

