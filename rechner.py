import math

def schimmel_analyse_kern(t_raum, rF_raum, t_wand):

    rF_raum_safe = max(rF_raum, 0.1)

    A = 17.625
    B = 243.04

    es_raum = 6.112 * math.exp((A * t_raum) / (B + t_raum))
    e_raum = (rF_raum_safe / 100.0) * es_raum

    v = math.log(e_raum / 6.112)
    t_taupunkt = (B * v) / (A - v)

    es_wand = 6.112 * math.exp((A * t_wand) / (B + t_wand))
    surf_rh_real = (e_raum / es_wand) * 100

    surf_rh_display = max(0.0, min(surf_rh_real, 100.0))

    taupunkt_abstand = t_wand - t_taupunkt
    delta_t = t_raum - t_wand

    scenario_id = ""

    if surf_rh_real >= 90 or taupunkt_abstand < 1.0:
        scenario_id = "S7 (Akute Gefahr)"

    elif delta_t >= 5 and rF_raum_safe <= 65:
        scenario_id = "Fall A (Baumangel)"

    elif delta_t < 3 and rF_raum_safe > 65:
        scenario_id = "Fall B (Nutzungsproblem)"

    elif surf_rh_real > 80:
        if t_wand >= 18.0:
            scenario_id = "Fall D3 (Sommer-Lüftungsfehler)"
        else:
            scenario_id = "Fall D1 (Mischursache)"

    else:
        scenario_id = "Fall C (Alles OK)"

    return {
        "taupunkt": round(t_taupunkt, 2),
        "taupunkt_abstand": round(taupunkt_abstand, 2),
        "surfRH": round(surf_rh_display, 1),
        "delta_t": round(delta_t, 2),
        "scenario_id": scenario_id
    }
