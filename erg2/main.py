import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests


def main():
    # pernoume ta dedomena apo to openweather api gia thn Larisa
    api_key = "7974cc86d355e6bb74e5813935c6be71"
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": "Larisa,GR",
        "appid": api_key,
        "units": "metric"
    }

    resp = requests.get(url, params=params)
    data = resp.json()

  
    print("data 1 (Larisa) colected from openweather :)")

    # pairnw data gia ton volo
    params = {
        "q": "Volos,GR",
        "appid": api_key,
        "units": "metric"
    }

    resp = requests.get(url, params=params)
    data2 = resp.json()

  
    print("data 2 (Volos) colected from openweather :)")

    # Γράφημα 1:

    # Λάρισα vs Βολος
    larisa_name = data.get("city", {}).get("name", "Larisa")
    city2_name = data2.get("city", {}).get("name", "Second area")

    df_larisa = pd.DataFrame({
        "time": [x["dt_txt"] for x in data["list"]],
        "temp": [x["main"]["temp"] for x in data["list"]],
        "feels_like": [x["main"]["feels_like"] for x in data["list"]],
    })

    df_city2 = pd.DataFrame({
        "time": [x["dt_txt"] for x in data2["list"]],
        "temp": [x["main"]["temp"] for x in data2["list"]],
        "feels_like": [x["main"]["feels_like"] for x in data2["list"]],
    })

    df_larisa["time"] = pd.to_datetime(df_larisa["time"])
    df_city2["time"] = pd.to_datetime(df_city2["time"])

    plt.figure(figsize=(13, 6))
    plt.plot(df_larisa["time"], df_larisa["temp"], label=f"{larisa_name} Θερμοκρασία", linewidth=2)
    plt.plot(df_larisa["time"], df_larisa["feels_like"], label=f"{larisa_name} Αισθητή", linewidth=2)
    plt.plot(df_city2["time"], df_city2["temp"], "--", label=f"{city2_name} Θερμοκρασία", linewidth=2)
    plt.plot(df_city2["time"], df_city2["feels_like"], "--", label=f"{city2_name} Αισθητή", linewidth=2)
    plt.axhline(y=df_larisa["temp"].max(), color='red', linestyle=':', alpha=0.5, label=f"Max: {df_larisa['temp'].max():.1f}°C")
    plt.axhline(y=df_larisa["temp"].min(), color='blue', linestyle=':', alpha=0.5, label=f"Min: {df_larisa['temp'].min():.1f}°C")

    plt.title("Γράφημα 1: Θερμοκρασία και αισθητή θερμοκρασία (Λάρισα vs 2η περιοχή)")
    plt.xlabel("Ημερομηνία / Ώρα")
    plt.ylabel("°C")
    plt.grid(alpha=0.25)
    plt.legend(loc="upper left")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("graph1.png", dpi=160)
    plt.show()

    print("Γράφημα 1 δημιουργήθηκε και αποθηκεύτηκε ως graph1.png :)")

    # Γράφημα 2

    df_at_larisa = pd.DataFrame({
        "time": [x["dt_txt"] for x in data["list"]],
        "temp": [x["main"]["temp"] for x in data["list"]],
        "humidity": [x["main"]["humidity"] for x in data["list"]],
        "wind_ms": [x["wind"]["speed"] for x in data["list"]],
    })

    df_at_city2 = pd.DataFrame({
        "time": [x["dt_txt"] for x in data2["list"]],
        "temp": [x["main"]["temp"] for x in data2["list"]],
        "humidity": [x["main"]["humidity"] for x in data2["list"]],
        "wind_ms": [x["wind"]["speed"] for x in data2["list"]],
    })

    df_at_larisa["time"] = pd.to_datetime(df_at_larisa["time"])
    df_at_city2["time"] = pd.to_datetime(df_at_city2["time"])

    e_larisa = (df_at_larisa["humidity"] / 100.0) * 6.105 * np.exp(
        (17.27 * df_at_larisa["temp"]) / (237.7 + df_at_larisa["temp"])
    )
    e_city2 = (df_at_city2["humidity"] / 100.0) * 6.105 * np.exp(
        (17.27 * df_at_city2["temp"]) / (237.7 + df_at_city2["temp"])
    )

    df_at_larisa["at_calc"] = df_at_larisa["temp"] + 0.33 * e_larisa - 0.70 * df_at_larisa["wind_ms"] - 4.0
    df_at_city2["at_calc"] = df_at_city2["temp"] + 0.33 * e_city2 - 0.70 * df_at_city2["wind_ms"] - 4.0

    plt.figure(figsize=(13, 6))
    plt.plot(df_at_larisa["time"], df_at_larisa["at_calc"], label=f"{larisa_name} AT υπολογισμένη", linewidth=2)
    plt.plot(df_at_city2["time"], df_at_city2["at_calc"], "--", label=f"{city2_name} AT υπολογισμένη", linewidth=2)

    all_at = pd.concat([df_at_larisa["at_calc"], df_at_city2["at_calc"]])
    max_val = all_at.max()
    min_val = all_at.min()

    plt.axhline(y=max_val, color='red', linestyle=':', alpha=0.3, label=f"Max: {max_val:.1f}°C")
    plt.axhline(y=min_val, color='blue', linestyle=':', alpha=0.3, label=f"Min: {min_val:.1f}°C")

    plt.title("Γράφημα 2: Υπολογισμένη Αισθητή Θερμοκρασία (Steadman 1984)")
    plt.xlabel("Ημερομηνία / Ώρα")
    plt.ylabel("AT (°C)")
    plt.grid(alpha=0.25)
    plt.legend(loc="upper left")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("graph2.png", dpi=160)
    plt.show()

    print("Γράφημα 2 δημιουργήθηκε και αποθηκεύτηκε ως graph2.png :)")

    # Γράφημα 3

    # Ταχύτητα ανέμου και ριπές (gust) - Λάρισα vs Βόλος με min/max
    df_wind_larisa = pd.DataFrame({
        "time": [x["dt_txt"] for x in data["list"]],
        "wind_speed": [x["wind"]["speed"] for x in data["list"]],
        "gust": [x["wind"].get("gust", np.nan) for x in data["list"]],
    })

    df_wind_city2 = pd.DataFrame({
        "time": [x["dt_txt"] for x in data2["list"]],
        "wind_speed": [x["wind"]["speed"] for x in data2["list"]],
        "gust": [x["wind"].get("gust", np.nan) for x in data2["list"]],
    })

    df_wind_larisa["time"] = pd.to_datetime(df_wind_larisa["time"])
    df_wind_city2["time"] = pd.to_datetime(df_wind_city2["time"])

    lar_w_min = df_wind_larisa["wind_speed"].min()
    lar_w_max = df_wind_larisa["wind_speed"].max()
    c2_w_min = df_wind_city2["wind_speed"].min()
    c2_w_max = df_wind_city2["wind_speed"].max()

    lar_g = df_wind_larisa["gust"].dropna()
    c2_g = df_wind_city2["gust"].dropna()

    plt.figure(figsize=(13, 6))

    plt.plot(
        df_wind_larisa["time"],
        df_wind_larisa["wind_speed"],
        linewidth=2,
        label=f"{larisa_name} Wind speed (min={lar_w_min:.1f}, max={lar_w_max:.1f} m/s)"
    )

    plt.plot(
        df_wind_city2["time"],
        df_wind_city2["wind_speed"],
        "--",
        linewidth=2,
        label=f"{city2_name} Wind speed (min={c2_w_min:.1f}, max={c2_w_max:.1f} m/s)"
    )

    if not lar_g.empty:
        lar_g_min = lar_g.min()
        lar_g_max = lar_g.max()
        plt.plot(
            df_wind_larisa["time"],
            df_wind_larisa["gust"],
            linewidth=2,
            alpha=0.8,
            label=f"{larisa_name} Gust (min={lar_g_min:.1f}, max={lar_g_max:.1f} m/s)"
        )

    if not c2_g.empty:
        c2_g_min = c2_g.min()
        c2_g_max = c2_g.max()
        plt.plot(
            df_wind_city2["time"],
            df_wind_city2["gust"],
            "--",
            linewidth=2,
            alpha=0.8,
            label=f"{city2_name} Gust (min={c2_g_min:.1f}, max={c2_g_max:.1f} m/s)"
        )

    all_wind = pd.concat([
        df_wind_larisa["wind_speed"],
        df_wind_city2["wind_speed"],
        df_wind_larisa["gust"],
        df_wind_city2["gust"]
    ], ignore_index=True)

    max_wind = all_wind.max()
    min_wind = all_wind.min()

    plt.axhline(y=max_wind, color='red', linestyle=':', alpha=0.5, label=f"Max: {max_wind:.1f} m/s")
    plt.axhline(y=min_wind, color='blue', linestyle=':', alpha=0.5, label=f"Min: {min_wind:.1f} m/s")

    plt.title("Γράφημα 3: Ταχύτητα ανέμου και ριπές (gust) - Λάρισα vs Βόλος")
    plt.xlabel("Ημερομηνία / Ώρα")
    plt.ylabel("m/s")
    plt.grid(alpha=0.25)
    plt.legend()
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("graph3.png", dpi=160)
    plt.show()

    print("Γράφημα 3 δημιουργήθηκε και αποθηκεύτηκε ως graph3.png :)")

def modarismenh_ergasia_1():
    # fortonw ta dedomenta apo ton stathmo se ena DataFrame
    data = pd.read_csv("https://greendigital.uth.gr/data/meteo48h.csv.txt")

    print("Data collected from meteorological station :)")

    # Γράφημα 1
    data["datetime"] = pd.to_datetime(data["Unix_time"], unit="s")

    plt.figure(figsize=(13, 6))
    plt.plot(data["datetime"], data["Temp_Out"], label="Θερμοκρασία (Temp_Out)", linewidth=2)
    plt.plot(data["datetime"], data["THW_Index"], label="Αισθητή Θερμοκρασία (THW_Index)", linewidth=2)

    plt.title("Θερμοκρασία και αισθητή θερμοκρασία (THW_Index) από μετεωρολογικό σταθμό")
    plt.xlabel("Ημερομηνία / Ώρα")
    plt.ylabel("°C")
    all_temp = pd.concat([data["Temp_Out"], data["THW_Index"]], ignore_index=True)
    max_temp = all_temp.max()
    min_temp = all_temp.min()

    plt.axhline(y=max_temp, color="red", linestyle=":", alpha=0.5, label=f"Max: {max_temp:.1f}°C")
    plt.axhline(y=min_temp, color="blue", linestyle=":", alpha=0.5, label=f"Min: {min_temp:.1f}°C")
    plt.legend(loc="upper left")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("graph_station_thw.png", dpi=160)
    plt.show()

    print("Γράφημα δημιουργήθηκε και αποθηκεύτηκε ως graph_station_thw.png :)")

    # Γράφημα 2
    
    plt.figure(figsize=(13, 6))
    plt.plot(data["datetime"], data["Wind_Speed"], label="Ταχύτητα ανέμου (Wind_Speed)", linewidth=2)
    plt.plot(data["datetime"], data["Hi_Speed"], label="Ριπές ανέμου (Hi_Speed)", linewidth=2)
    
    all_wind_data = pd.concat([data["Wind_Speed"], data["Hi_Speed"]])
    plt.axhline(y=all_wind_data.max(), color='red', linestyle=':', alpha=0.5, label=f"Max: {all_wind_data.max():.1f} m/s")
    plt.axhline(y=all_wind_data.min(), color='blue', linestyle=':', alpha=0.5, label=f"Min: {all_wind_data.min():.1f} m/s")
    
    plt.title("Ταχύτητα ανέμου και ριπές ανέμου (Hi_Speed) από μετεωρολογικό σταθμό")
    plt.xlabel("Ημερομηνία / Ώρα")
    plt.ylabel("m/s")
    plt.legend(loc="upper left")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig("graph_station_wind_hi_speed.png", dpi=160)
    plt.show()

    print("Γράφημα δημιουργήθηκε και αποθηκεύτηκε ως graph_station_wind_hi_speed.png :)")

main()
modarismenh_ergasia_1()