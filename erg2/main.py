import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests


def main():
    # pernoume ta dedomena apo to openweather api
    api_key = "7974cc86d355e6bb74e5813935c6be71"
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": "Larisa,GR",
        "appid": api_key,
        "units": "metric"
    }

    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    # emfanizoume ta apotelesmata
    print(data)

    # # Γράφημα 1
    # plt.figure()
    # plt.plot(data["Time"], data["Temp_Out"], label="Θερμοκρασία")
    # plt.plot(data["Time"], results["wind_chill"], label="Wind Chill (υπολογισμός)")
    # plt.plot(data["Time"], results["Wind_Chill"], label="Wind Chill (weatherlink)")
    # plt.xlabel("Ώρα")
    # plt.ylabel("°C")
    # plt.title("Θερμοκρασία και Wind Chill")
    # plt.legend()
    # plt.savefig("graph1.png")
    
    # # Γράφημα 2
    # plt.figure()
    # plt.plot(data["Time"], data["Wind_Speed"], label="Μέση ταχύτητα")
    # plt.plot(data["Time"], data["Hi_Speed"], label="Μέγιστη ταχύτητα")
    # plt.xlabel("Ώρα")
    # plt.ylabel("km/h")
    # plt.title("Ταχύτητα Ανέμου")
    # plt.legend()
    # plt.savefig("graph2.png")
    
    # # Γράφημα 3
    # plt.figure()
    # plt.plot(data["Time"], data["Out_Hum"], label="Υγρασία (%)")
    # plt.xlabel("Ώρα")
    # plt.ylabel("%")
    # plt.title("Υγρασία και Βαρομετρική Πίεση")
    # plt.legend()
    # plt.savefig("graph3.png")


main()