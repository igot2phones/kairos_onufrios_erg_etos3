import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    # fortonw ta dedomenta apo ton stathmo se ena DataFrame
    data = pd.read_csv("https://greendigital.uth.gr/data/meteo48h.csv.txt")
    # kanoume ena kainourgia DataFrame gia ta apotelesmata pou tha paroume
    results = pd.DataFrame(columns=["Time", "wind_chill"])

    results["Time"] = data["Time"]
    # ypologizoume to wind chill gia kathe grammi tou dataset
    results["wind_chill"] = np.where(
        (data["Wind_Speed"] > 4.8) & (data["Temp_Out"] <= 10),
        13.12 + 0.6215 * data["Temp_Out"] - 11.37 * (data["Wind_Speed"] ** 0.16) + 0.3965 * data["Temp_Out"] * (data["Wind_Speed"] ** 0.16),
        data["Temp_Out"] # an den isxuei i proipothesi, to wind chill einai idio me tin thermokrasia
    )
    # emfanizoume ta apotelesmata
    print(results)

    # Γράφημα 1
    plt.figure()
    plt.plot(data["Time"], data["Temp_Out"], label="Θερμοκρασία")
    plt.plot(data["Time"], results["wind_chill"], label="Wind Chill (υπολογισμός)")
    plt.plot(data["Time"], data["Wind_Chill"], label="Wind Chill (weatherlink)")
    plt.xlabel("Ώρα")
    plt.ylabel("°C")
    plt.title("Θερμοκρασία και Wind Chill")
    plt.legend()
    plt.savefig("graph1.png")
    
    # Γράφημα 2
    plt.figure()
    plt.plot(data["Time"], data["Wind_Speed"], label="Μέση ταχύτητα")
    plt.plot(data["Time"], data["Hi_Speed"], label="Μέγιστη ταχύτητα")
    plt.xlabel("Ώρα")
    plt.ylabel("km/h")
    plt.title("Ταχύτητα Ανέμου")
    plt.legend()
    plt.savefig("graph2.png")
    
    # Γράφημα 3
    plt.figure()
    plt.plot(data["Time"], data["Out_Hum"], label="Υγρασία (%)")
    plt.xlabel("Ώρα")
    plt.ylabel("%")
    plt.title("Υγρασία και Βαρομετρική Πίεση")
    plt.legend()
    plt.savefig("graph3.png")


main()