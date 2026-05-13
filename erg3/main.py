import json
import os
from datetime import datetime, timezone

import numpy as np
import matplotlib.pyplot as plt


# ====== Stathres ======
GAMMA_D = 9.8     # ksiri adiabatiki thermovathmida (K/km)
GAMMA_DEW = 1.8   # adiabatiki thermovathmida simeiou drosou (K/km)


def load_geojson(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_profile(gj):
    """Pernoume to katakorufo profile apo to GeoJSON.
    Epistrefei dict me arrays (taksinomimena kata ipsos)."""
    z, T, Td, p, u, v = [], [], [], [], [], []
    for feat in gj["features"]:
        pr = feat["properties"]
        if pr.get("gpheight") is None or pr.get("temp") is None:
            continue
        z.append(pr["gpheight"])
        T.append(pr["temp"])           # K
        Td.append(pr.get("dewpoint"))  # K (mporei na einai None)
        p.append(pr.get("pressure"))   # hPa
        u.append(pr.get("wind_u"))     # m/s
        v.append(pr.get("wind_v"))     # m/s

    z = np.array(z, dtype=float)
    T = np.array(T, dtype=float)
    Td = np.array([np.nan if x is None else x for x in Td], dtype=float)
    p = np.array([np.nan if x is None else x for x in p], dtype=float)
    u = np.array([np.nan if x is None else x for x in u], dtype=float)
    v = np.array([np.nan if x is None else x for x in v], dtype=float)

    # taksinomisi kata ipsos
    order = np.argsort(z)
    return {
        "z": z[order],
        "T": T[order],
        "Td": Td[order],
        "p": p[order],
        "u": u[order],
        "v": v[order],
    }


def relative_humidity(T_K, Td_K):
    """RH (%) apo thermokrasia kai simeio drosou (K) me ti schesi tou Magnus."""
    T_c = T_K - 273.15
    Td_c = Td_K - 273.15
    a, b = 17.625, 243.04
    es = 6.1094 * np.exp(a * T_c / (b + T_c))
    e = 6.1094 * np.exp(a * Td_c / (b + Td_c))
    rh = 100.0 * e / es
    return np.clip(rh, 0, 100)


def wind_speed(u, v):
    return np.sqrt(u * u + v * v)


def compute_lcl_ccl_tcon(prof):
    """Proseggistikoi ypologismoi LCL, CCL, TCON me statheres adiavatikes thermovathmides.

    LCL: ipsos opou T_dry kai Td_dry sigklinoun, ksekinontas apo tin epifaneia.
         h_LCL = (T0 - Td0) / (Gamma_d - Gamma_dew)  (kilometra)
    CCL: ipsos opou i epektasi tou epifaneiakou Td (me Gamma_dew) temnei
         to perivallontiko profile T(z).
    TCON: thermokrasia enausis = T sto CCL + Gamma_d * h_CCL (epifaneiaka)
    Olo se SI me ipsos se metra panw apo tin epifaneia.
    """
    z = prof["z"]
    T = prof["T"]  # K
    Td = prof["Td"]  # K

    z0 = z[0]
    T0 = T[0]
    Td0 = Td[0]

    # ---- LCL ----
    # diafora se K (= °C), thermovathmides se K/km -> ipsos se km
    h_lcl_km = (T0 - Td0) / (GAMMA_D - GAMMA_DEW)
    h_lcl = h_lcl_km * 1000.0  # metra panw apo tin epifaneia
    z_lcl = z0 + h_lcl

    # ---- CCL ----
    # epektasi tou epifaneiakou Td panw me Gamma_dew (K/km)
    dz_km = (z - z0) / 1000.0
    Td_parcel = Td0 - GAMMA_DEW * dz_km  # K
    diff = T - Td_parcel  # >0 otan to perivallon einai thermotero apo to parcel-Td
    # vriskoume tin proti tomi (allagi proshmou) ksekinontas apo tin epifaneia
    z_ccl = None
    for i in range(1, len(z)):
        if np.isnan(diff[i]) or np.isnan(diff[i - 1]):
            continue
        if diff[i - 1] * diff[i] <= 0 and (z[i] - z0) > 1.0:
            # grammiki paremvoli gia akrivesteri timi
            x1, x2 = diff[i - 1], diff[i]
            z1, z2 = z[i - 1], z[i]
            if x2 - x1 != 0:
                z_ccl = z1 - x1 * (z2 - z1) / (x2 - x1)
            else:
                z_ccl = z1
            break

    if z_ccl is None:
        h_ccl = float("nan")
        T_at_ccl = float("nan")
        tcon = float("nan")
    else:
        h_ccl = z_ccl - z0
        # thermokrasia perivallontos sto z_ccl (grammiki paremvoli)
        T_at_ccl = np.interp(z_ccl, z, T)
        # TCON: epekteinoume tin T_at_ccl pros ta katw me Gamma_d
        tcon = T_at_ccl + GAMMA_D * (h_ccl / 1000.0)

    return {
        "h_lcl_m": h_lcl,
        "z_lcl_m": z_lcl,
        "h_ccl_m": h_ccl,
        "z_ccl_m": (None if z_ccl is None else z_ccl),
        "T_at_ccl_K": T_at_ccl,
        "tcon_K": tcon,
    }


def plot_profiles(prof, station_name, dt_str, out_png, z_top=12000):
    z = prof["z"]
    T_c = prof["T"] - 273.15
    Td_c = prof["Td"] - 273.15
    ws = wind_speed(prof["u"], prof["v"])
    rh = relative_humidity(prof["T"], prof["Td"])

    mask = z <= (z[0] + z_top)

    fig, axes = plt.subplots(1, 3, figsize=(15, 8), sharey=True)

    ax = axes[0]
    ax.plot(T_c[mask], z[mask], "r-", label="Θερμοκρασία ξηρού βολβού")
    ax.plot(Td_c[mask], z[mask], "b-", label="Σημείο δρόσου")
    ax.set_xlabel("Θερμοκρασία (°C)")
    ax.set_ylabel("Γεωδυναμικό ύψος (m)")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")

    ax = axes[1]
    ax.plot(ws[mask], z[mask], "g-")
    ax.set_xlabel("Ταχύτητα ανέμου |V| (m/s)")
    ax.grid(alpha=0.3)

    ax = axes[2]
    ax.plot(rh[mask], z[mask], "m-")
    ax.set_xlabel("Σχετική υγρασία (%)")
    ax.set_xlim(0, 100)
    ax.grid(alpha=0.3)

    fig.suptitle(f"Ραδιοβόλιση — {station_name} — {dt_str}", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_png, dpi=160)
    plt.close(fig)
    print(f"Apothikeftike: {out_png}")


def write_results(out_txt, station_name, dt_str, prof, calc, windy_values=None):
    T0 = prof["T"][0]
    Td0 = prof["Td"][0]
    lines = []
    lines.append(f"Apotelesmata analysis radiovolisis")
    lines.append(f"Stathmos: {station_name}")
    lines.append(f"Imerominia/ora: {dt_str}")
    lines.append("")
    lines.append("Epifaneiakes times:")
    lines.append(f"  T  = {T0 - 273.15:.2f} °C")
    lines.append(f"  Td = {Td0 - 273.15:.2f} °C")
    lines.append(f"  T - Td = {(T0 - Td0):.2f} K")
    lines.append("")
    lines.append("Proseggistikoi ypologismoi (statheres adiavatikes thermovathmides):")
    lines.append(f"  Gamma_d   = {GAMMA_D} K/km (ksiros aeras)")
    lines.append(f"  Gamma_dew = {GAMMA_DEW} K/km (simeio drosou)")
    lines.append("")
    lines.append(f"  LCL  (epipedo sympyknosis logo eksanagasmenis anodou)")
    lines.append(f"    ipsos panw apo tin epifaneia: {calc['h_lcl_m']:.0f} m")
    lines.append(f"    geodynamiko ipsos:            {calc['z_lcl_m']:.0f} m")
    lines.append("")
    if not np.isnan(calc["h_ccl_m"]):
        lines.append(f"  CCL  (epipedo sympyknosis logo thermikis metaforas)")
        lines.append(f"    ipsos panw apo tin epifaneia: {calc['h_ccl_m']:.0f} m")
        lines.append(f"    geodynamiko ipsos:            {calc['z_ccl_m']:.0f} m")
        lines.append(f"    T sto CCL:                    {calc['T_at_ccl_K'] - 273.15:.2f} °C")
        lines.append("")
        lines.append(f"  TCON (thermokrasia enausis):    {calc['tcon_K'] - 273.15:.2f} °C")
    else:
        lines.append("  CCL: den vrethike tomi mesa sto profile.")
        lines.append("  TCON: mi diathesimi (apaitei CCL).")

    if windy_values:
        lines.append("")
        lines.append("Antistoixes times apo to windy.com:")
        for k, v in windy_values.items():
            lines.append(f"  {k}: {v}")

    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Apothikeftike: {out_txt}")


def process_file(path, out_png, out_txt, windy_values=None):
    gj = load_geojson(path)
    props = gj["properties"]
    station_name = props.get("station_name", "Unknown")
    ts = props.get("syn_timestamp")
    dt_str = (
        datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        if ts else "n/a"
    )

    prof = extract_profile(gj)
    calc = compute_lcl_ccl_tcon(prof)

    plot_profiles(prof, station_name, dt_str, out_png)
    write_results(out_txt, station_name, dt_str, prof, calc, windy_values=windy_values)

    print(f"\n--- {station_name} ({dt_str}) ---")
    print(f"  LCL  ~ {calc['h_lcl_m']:.0f} m")
    if not np.isnan(calc["h_ccl_m"]):
        print(f"  CCL  ~ {calc['h_ccl_m']:.0f} m")
        print(f"  TCON ~ {calc['tcon_K'] - 273.15:.2f} °C")


def main():
    here = os.path.dirname(os.path.abspath(__file__))

    thes_json = os.path.join(here, "16622-1776816000000-fm94thes.json")
    ath_json = os.path.join(here, "16622-1776816000000-fm94ath.json")

    # Times pou anaferei to windy gia ti Thessaloniki (apo tin ekfonisi)
    windy_thes = {
        "LCL":  "428 m",
        "CCL":  "1290 m",
        "TCON": "20 °C",
    }
    # Gia tin deuteri poli den dinontai sygkekrimenes times stin ekfonisi
    windy_ath = {
        "LCL":  "—  (sympliroste apo to windy.com)",
        "CCL":  "—  (sympliroste apo to windy.com)",
        "TCON": "—  (sympliroste apo to windy.com)",
    }

    process_file(
        thes_json,
        out_png=os.path.join(here, "thessaloniki.png"),
        out_txt=os.path.join(here, "thessaloniki.txt"),
        windy_values=windy_thes,
    )
    process_file(
        ath_json,
        out_png=os.path.join(here, "athina.png"),
        out_txt=os.path.join(here, "athina.txt"),
        windy_values=windy_ath,
    )


if __name__ == "__main__":
    main()
