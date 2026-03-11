# ================================================
# SCHIMMELRECHNER – Textbausteine v1.1
# Platzhalter werden vor Ausgabe ersetzt:
#   [tWand]   → Wandtemperatur
#   [ΔT]      → Temperaturdifferenz
#   [rH]      → Luftfeuchtigkeit
#   [surfRH]  → Oberflächenfeuchte
#   [TP]      → Taupunkt
#   [Abstand] → Abstand zum Taupunkt
# ================================================

TEXTBAUSTEINE = {

    "Fall 0": {
        "ursache": "Die Messwerte liegen im unauffälligen Bereich. Die Wandtemperatur ist ausreichend hoch und die Oberflächenfeuchte liegt sicher unterhalb der Schimmelgrenze. Kein Handlungsbedarf.",
        "befund1": "Die Wandtemperatur von [tWand] °C liegt im grünen Bereich. Die Temperaturdifferenz zur Raumluft beträgt [ΔT] °C. Die Außenwand funktioniert nach aktuellem Messbefund einwandfrei.",
        "befund2": "Die Raumluftfeuchtigkeit von [rH] % rF ist unauffällig. Heizverhalten und Lüftungsgewohnheiten erscheinen der Situation angemessen. Kein Nutzungsproblem erkennbar.",
        "befund3": "Kein Handlungsbedarf. Die Messwerte zeigen keine Auffälligkeiten. Bei Bedarf kann die Messung zu einem späteren Zeitpunkt oder unter anderen Bedingungen wiederholt werden."
    },

    "Fall A": {
        "ursache": "Die hohe Temperaturdifferenz zwischen Raumluft und Wandoberfläche bei normaler Luftfeuchtigkeit lässt mit hoher Wahrscheinlichkeit auf einen baulichen Mangel schließen – etwa eine Wärmebrücke oder einen Dämmungsmangel in der Außenwandkonstruktion.",
        "befund1": "Die gemessene Wandtemperatur liegt im kritischen bzw. auffälligen Bereich. Die Temperaturdifferenz zur Raumluft beträgt [ΔT] °C. Dieser Wert deutet auf eine unzureichende Dämmwirkung der Außenwand hin – entweder durch eine konstruktive Wärmebrücke oder durch einen Dämmungsmangel.",
        "befund2": "Die Raumluftfeuchtigkeit liegt mit [rH] % rF im normalen Bereich. Ein Nutzungsproblem – etwa unzureichende Lüftung oder erhöhte Feuchteproduktion – ist als Ursache des Schimmelrisikos unwahrscheinlich. Auch bei vorbildlichem Lüftungsverhalten würde das Risiko an dieser Stelle voraussichtlich bestehen bleiben.",
        "befund3": "Es wird empfohlen, die Wandkonstruktion fachlich begutachten zu lassen. Da Außenwände in der Regel zum Gemeinschaftseigentum zählen, könnte die Zuständigkeit für die Instandsetzung gemäß § 19 Abs. 2 Nr. 2 WEG bei der Eigentümergemeinschaft liegen – dies sollte rechtlich geprüft werden."
    },

    "Fall A2": {
        "ursache": "Die Temperaturdifferenz zwischen Raumluft und Wandoberfläche ist auffällig, liegt aber noch unterhalb des Schwellenwerts für einen eindeutigen Baumangel. Bei normaler Luftfeuchtigkeit könnte eine Dämmungsschwäche oder eine konstruktive Wärmebrücke als Ursache in Betracht kommen.",
        "befund1": "Die gemessene Wandtemperatur liegt im auffälligen Bereich. Die Temperaturdifferenz zur Raumluft beträgt [ΔT] °C. Dieser Wert liegt im Grenzbereich zwischen normalem Wärmedurchgang und einer möglichen Dämmungsschwäche – eine fachliche Einschätzung wäre zur Klärung sinnvoll.",
        "befund2": "Die Raumluftfeuchtigkeit von [rH] % rF ist unauffällig. Ein Nutzungsproblem als alleinige Ursache gilt bei diesen Werten als unwahrscheinlich. Das Risiko würde sich durch besseres Lüftungsverhalten zwar leicht reduzieren, eine bauliche Ursache wäre damit aber nicht ausgeschlossen.",
        "befund3": "Eine fachliche Überprüfung der Wandkonstruktion wird empfohlen – insbesondere der Dämmung und möglicher Wärmebrücken. Eine abschließende Bewertung der Verantwortlichkeiten sollte erst nach der Begutachtung erfolgen."
    },

    "Fall B": {
        "ursache": "Die erhöhte Raumluftfeuchtigkeit bei geringer Temperaturdifferenz deutet darauf hin, dass das Schimmelrisiko in erster Linie durch das Nutzungsverhalten bedingt ist – unzureichende Lüftung oder erhöhte Feuchteproduktion im Raum sind als Ursache wahrscheinlich.",
        "befund1": "Die Wandtemperatur von [tWand] °C liegt im unauffälligen Bereich. Die Temperaturdifferenz zur Raumluft beträgt lediglich [ΔT] °C. Die Wand selbst ist nach aktuellem Messbefund baulich unauffällig.",
        "befund2": "Die Raumluftfeuchtigkeit von [rH] % rF ist deutlich erhöht. Regelmäßiges Stoßlüften und die Überprüfung von Feuchtigkeitsquellen werden empfohlen – zum Beispiel Wäschetrocknen im Raum, Kochen ohne Dunstabzug oder zu wenig Luftaustausch. Die Messwerte deuten darauf hin, dass eine Anpassung des Lüftungsverhaltens das Risiko voraussichtlich deutlich reduzieren würde.",
        "befund3": "Die Ursache liegt nach aktuellem Befund im Nutzungsverhalten. Eine bauliche Maßnahme ist derzeit nicht angezeigt. Sollte das Schimmelrisiko trotz verbesserter Lüftung fortbestehen, wäre eine erneute Messung sinnvoll."
    },

    "Fall C": {
        "ursache": "Sowohl die Wandtemperatur als auch die Luftfeuchtigkeit tragen zum erhöhten Schimmelrisiko bei. Eine Kombination aus baulicher Ursache und Nutzungsverhalten ist wahrscheinlich – die genaue Gewichtung lässt sich anhand der vorliegenden Messwerte allein nicht abschließend bestimmen.",
        "befund1": "Die Wandtemperatur von [tWand] °C liegt im auffälligen Bereich. Die Temperaturdifferenz zur Raumluft beträgt [ΔT] °C. Dieser Wert lässt auf eine Dämmungsschwäche oder eine konstruktive Wärmebrücke schließen, die zum Risiko beiträgt.",
        "befund2": "Die Raumluftfeuchtigkeit von [rH] % rF ist erhöht und verstärkt das Risiko zusätzlich. Durch eine Verbesserung des Lüftungsverhaltens ließe sich das Risiko reduzieren – der bauliche Anteil des Problems bliebe davon allerdings unberührt.",
        "befund3": "Es wird empfohlen, sowohl das Lüftungsverhalten anzupassen als auch die Wandkonstruktion fachlich prüfen zu lassen. Da beide Seiten zum Problem beitragen, sollte die Frage der Verantwortlichkeit – insbesondere zwischen Eigentümergemeinschaft und Nutzer – einvernehmlich und auf Basis einer Fachbegutachtung geklärt werden."
    },

    "Fall D1": {
        "ursache": "Die Wandtemperatur ist baulich unauffällig. Das erhöhte Schimmelrisiko ergibt sich aus der hohen Raumluftfeuchtigkeit, die trotz gut gedämmter Wand zu einer kritischen Oberflächenfeuchte führt. Die Ursache liegt wahrscheinlich im Nutzungsverhalten.",
        "befund1": "Die Wandtemperatur von [tWand] °C liegt im grünen Bereich. Die Außenwand funktioniert nach aktuellem Messbefund ordnungsgemäß. Die Wand ist als Ursache des Schimmelrisikos unwahrscheinlich.",
        "befund2": "Die Raumluftfeuchtigkeit von [rH] % rF ist deutlich erhöht und ist nach aktuellem Befund die wahrscheinliche Hauptursache für das Risiko. Regelmäßiges Lüften, die Reduktion von Feuchtigkeitsquellen und gegebenenfalls der Einsatz eines Hygrometers zur Kontrolle der Raumluftfeuchte werden empfohlen.",
        "befund3": "Eine bauliche Maßnahme ist nach aktuellem Befund nicht erforderlich. Die Ursache liegt im Nutzungsverhalten. Sollte das Risiko trotz verbesserter Lüftung fortbestehen, wäre eine erneute Messung unter veränderten Bedingungen sinnvoll."
    },

    "Fall D2": {
        "ursache": "Obwohl die Wandtemperatur unauffällig ist, reicht sie bei der aktuellen Außenluftfeuchte nicht aus, um Kondensation zu verhindern. Die Ursache ist kein Baumangel und kein Nutzungsproblem im klassischen Sinne – sondern Sommerkondensation: Warme, feuchte Außenluft kühlt an der vergleichsweise kühlen Innenwand ab.",
        "befund1": "Die Wandtemperatur von [tWand] °C ist baulich einwandfrei. Der Taupunkt der Außenluft liegt über der Wandtemperatur. Das bedeutet: Feuchtigkeit aus der Außenluft kann an der Wand kondensieren, ohne dass die Wand selbst ein Problem darstellt.",
        "befund2": "Im Sommer gilt eine andere Regel als im Winter: Lüften hilft nur dann, wenn der Taupunkt der Außenluft niedriger ist als die Wandtemperatur. Bei schwüler Außenluft sollten Fenster und Türen geschlossen bleiben – auch wenn es draußen warm und scheinbar trocken wirkt.",
        "befund3": "Fenster geschlossen halten, solange die Außenluft schwül ist. Die Raumluft wenn möglich durch Kühlung oder Entfeuchtung stabilisieren. Eine bauliche Maßnahme ist nicht angezeigt. Bei wiederholtem Auftreten im Sommer wäre ein Hygrometer zur Raumüberwachung empfehlenswert."
    },

    "Fall D3": {
        "ursache": "Die Wandtemperatur ist unauffällig, und die Raumluftfeuchtigkeit ist nicht erhöht. Für eine sichere Bewertung des Schimmelrisikos fehlen dennoch wichtige Daten. Es ist möglich, dass Sommerkondensation durch feuchte Außenluft vorliegt.",
        "befund1": "Die Wandtemperatur von [tWand] °C liegt im grünen Bereich. Die Wand selbst ist als Ursache unwahrscheinlich. Die Oberflächenfeuchte liegt dennoch im erhöhten Bereich, was eine Erklärung erfordert.",
        "befund2": "Für eine eindeutige Diagnose wäre die Eingabe der Außentemperatur und Außenluftfeuchtigkeit erforderlich. Ohne diese Werte lässt sich nicht abschließend beurteilen, ob Sommerkondensation die Ursache ist.",
        "befund3": "Bitte Außentemperatur und Außenluftfeuchtigkeit ergänzen oder die Messung zu einem anderen Zeitpunkt wiederholen. Alternativ: Wenn die erhöhte Oberflächenfeuchte regelmäßig in den Sommermonaten auftritt, ist Sommerkondensation als Ursache wahrscheinlich."
    },

    "S7a": {
        "ursache": "Die rechnerische Oberflächenfeuchte liegt weit über der Schimmelgrenze von 80 %. Bei dauerhafter Belastung ist Schimmelwachstum nicht nur möglich, sondern zu erwarten. Zeitnahes Handeln ist angezeigt.",
        "befund1": "Der kälteste Messpunkt liegt bei [tWand] °C mit einer Temperaturdifferenz von [ΔT] °C zur Raumluft. Die Oberflächenfeuchte erreicht rechnerisch [surfRH] % – das liegt deutlich über dem Schwellenwert für Schimmelbildung. Die Wand befindet sich in einem Zustand, der aktives Schimmelwachstum begünstigt.",
        "befund2": "Schimmelsporen können die Raumluftqualität beeinträchtigen und bei empfindlichen Personen gesundheitliche Beschwerden auslösen. Die Situation sollte nicht auf Dauer hingenommen werden.",
        "befund3": "Eine fachliche Begutachtung durch einen Sachverständigen wird dringend empfohlen. Bereits sichtbare Schimmelstellen sollten fachgerecht beseitigt werden. Sofern ein baulicher Mangel vorliegt, könnte die Zuständigkeit gemäß § 19 Abs. 2 Nr. 2 WEG bei der Eigentümergemeinschaft liegen – dies sollte rechtlich geprüft werden."
    },

    "S7b": {
        "ursache": "Der Abstand zwischen Wandtemperatur und Taupunkt beträgt nur [Abstand] °C. Bereits eine geringfügige Erhöhung der Raumluftfeuchtigkeit – durch Duschen, Kochen oder eine weitere Person im Raum – würde zu direkter Kondensatbildung führen: sichtbaren Wassertropfen an der Wand.",
        "befund1": "Der kälteste Messpunkt liegt bei [tWand] °C. Der Taupunkt der Raumluft liegt bei [TP] °C. Der Abstand beträgt lediglich [Abstand] °C – die Wand ist an diesem Punkt praktisch am Kondensationslimit. Unter normalen Nutzungsbedingungen ist mit Tauwasserbildung zu rechnen.",
        "befund2": "Auch bei unauffälliger Grundfeuchte reicht jede kurzfristige Aktivität aus, die Feuchtigkeit erzeugt, um die Taupunktgrenze zu überschreiten. Das Risiko besteht unabhängig davon, ob die Raumluftfeuchtigkeit im Messzeitpunkt erhöht war.",
        "befund3": "Sofortige Überprüfung der Wandkonstruktion wird empfohlen. Die Ursache liegt mit hoher Wahrscheinlichkeit in einem baulichen Mangel. Eine fachliche Begutachtung sollte zeitnah veranlasst werden. Der Zuständigkeitsrahmen gemäß § 19 Abs. 2 Nr. 2 WEG sollte geprüft werden."
    },

    "S7c": {
        "ursache": "Die Messwerte zeigen die kritischste mögliche Kombination: Die Oberflächenfeuchte liegt weit über der Schimmelgrenze, und gleichzeitig beträgt der Abstand zum Taupunkt nur [Abstand] °C. Schimmelwachstum findet bei dauerhafter Belastung mit hoher Wahrscheinlichkeit bereits statt – und direktes Kondensat kann jederzeit auftreten.",
        "befund1": "Der kälteste Messpunkt liegt bei [tWand] °C, der Taupunkt bei [TP] °C, Abstand nur [Abstand] °C. Die Oberflächenfeuchte erreicht [surfRH] %. Beide Alarmschwellen sind gleichzeitig überschritten. Die Wand befindet sich in einem Zustand, der akute Feuchte- und Schimmelschäden erwarten lässt.",
        "befund2": "Das gleichzeitige Vorliegen von extremer Oberflächenfeuchte und minimalem Taupunktabstand ist ein ernstes Warnsignal. Dauerhafter Aufenthalt in diesem Bereich ist – insbesondere für Kinder, ältere Personen und Menschen mit Atemwegserkrankungen – nicht empfehlenswert.",
        "befund3": "Unverzügliche fachliche Begutachtung wird dringend empfohlen. Sichtbare Schimmelstellen sind fachgerecht zu beseitigen. Die Wandkonstruktion sollte auf Dämmungsmängel und Wärmebrücken geprüft werden. Die Frage der WEG-Zuständigkeit gemäß § 19 Abs. 2 Nr. 2 WEG sollte rechtlich geprüft werden. Dies ist kein Fall für abwartendes Beobachten."
    },

    "Fuzzy Rot/Gelb Tendenz Rot": {
        "ursache": "Der Messwert liegt im Übergangsbereich zwischen rotem und gelbem Bereich. Die Tendenz geht in Richtung kritisch.",
        "befund1": "Der Messwert von [tWand] °C liegt im Übergangsbereich zwischen rotem und gelbem Bereich. Die Tendenz geht in Richtung kritisch. Laser-Thermometer haben eine typische Messungenauigkeit von ±0,5–1,0 °C – der tatsächliche Wert könnte also im klar roten Bereich liegen.",
        "befund2": "Eine Wiederholungsmessung an diesem Punkt wird empfohlen, bevor Maßnahmen eingeleitet werden.",
        "befund3": "Wiederholungsmessung empfohlen. Bei Bestätigung des Wertes fachliche Prüfung veranlassen."
    },

    "Fuzzy Rot/Gelb Tendenz Gelb": {
        "ursache": "Der Messwert liegt im Übergangsbereich zwischen rotem und gelbem Bereich. Die Tendenz geht eher in Richtung auffällig als kritisch.",
        "befund1": "Der Messwert von [tWand] °C liegt im Übergangsbereich zwischen rotem und gelbem Bereich. Die Tendenz geht eher in Richtung auffällig als kritisch. Dennoch: Laser-Thermometer haben eine typische Messungenauigkeit von ±0,5–1,0 °C – der tatsächliche Wert könnte in den klar roten Bereich fallen.",
        "befund2": "Eine Wiederholungsmessung und ergänzende Kriterien werden empfohlen.",
        "befund3": "Wiederholungsmessung empfohlen. Situation beobachten."
    },

    "Fuzzy Gelb/Grün Tendenz Gelb": {
        "ursache": "Der Messwert liegt im Übergangsbereich zwischen gelbem und grünem Bereich. Die Tendenz geht in Richtung auffällig.",
        "befund1": "Der Messwert von [tWand] °C liegt im Übergangsbereich zwischen gelbem und grünem Bereich. Die Tendenz geht in Richtung auffällig. Bei Messungenauigkeiten des Geräts von ±0,5–1,0 °C könnte der tatsächliche Wert im klar gelben Bereich liegen.",
        "befund2": "Eine Wiederholungsmessung und die Berücksichtigung der Oberflächenfeuchte werden empfohlen.",
        "befund3": "Situation beobachten, Wiederholungsmessung sinnvoll."
    },

    "Fuzzy Gelb/Grün Tendenz Grün": {
        "ursache": "Der Messwert liegt im Übergangsbereich zwischen gelbem und grünem Bereich. Die Tendenz geht eher in Richtung unauffällig.",
        "befund1": "Der Messwert von [tWand] °C liegt im Übergangsbereich zwischen gelbem und grünem Bereich. Die Tendenz geht eher in Richtung unauffällig. Bei Messungenauigkeiten des Geräts von ±0,5–1,0 °C ist ein Ausschlag in den gelben Bereich möglich, aber bei dieser Konstellation weniger wahrscheinlich.",
        "befund2": "Eine Wiederholungsmessung bei Unsicherheit wird empfohlen.",
        "befund3": "Kein akuter Handlungsbedarf. Wiederholungsmessung optional."
    }
}

# Fuzzy-Schlüssel für scenario_id aus Python-Backend
SCENARIO_KEY_MAP = {
    "Fall 0 (Unauffällig)":              "Fall 0",
    "Fall A (Baumangel)":                "Fall A",
    "Fall A2 (Baumangel wahrscheinlich)":"Fall A2",
    "Fall B (Nutzungsproblem)":          "Fall B",
    "Fall C (Mischursache)":             "Fall C",
    "Fall C (Alles OK)":                 "Fall 0",   # Mapping alter scenario_id aus analysis_core.py
    "Fall D1 (Nutzung bei guter Wand)":  "Fall D1",
    "Fall D2 (Sommerkondensation)":      "Fall D2",
    "Fall D3 (Daten fehlen)":            "Fall D3",
    "Fall D3 (Sommer-Lüftung)":         "Fall D2",  # Mapping alter scenario_id
    "S7 (Akute Gefahr)":                 "S7a",      # Default wenn nur ein Trigger
    "S7a (Schimmelwachstum)":            "S7a",
    "S7b (Kondensatgefahr)":             "S7b",
    "S7c (Worst Case)":                  "S7c",
    "Fuzzy Rot/Gelb Tendenz Rot":        "Fuzzy Rot/Gelb Tendenz Rot",
    "Fuzzy Rot/Gelb Tendenz Gelb":       "Fuzzy Rot/Gelb Tendenz Gelb",
    "Fuzzy Gelb/Grün Tendenz Gelb":      "Fuzzy Gelb/Grün Tendenz Gelb",
    "Fuzzy Gelb/Grün Tendenz Grün":      "Fuzzy Gelb/Grün Tendenz Grün",
}


def get_textbausteine(scenario_id: str, t_wand: float, delta_t: float,
                      rh: float, surf_rh: float, taupunkt: float,
                      taupunkt_abstand: float) -> dict:
    """
    Gibt die Textbausteine für ein Szenario zurück,
    mit ersetzten Platzhaltern.
    """
    key = SCENARIO_KEY_MAP.get(scenario_id)
    if not key:
        # Fallback: Fuzzy-Keys direkt versuchen
        key = scenario_id if scenario_id in TEXTBAUSTEINE else "Fall 0"

    texte = TEXTBAUSTEINE.get(key, TEXTBAUSTEINE["Fall 0"])

    def replace(text):
        return (text
            .replace("[tWand]",   f"{t_wand:.1f}")
            .replace("[ΔT]",      f"{delta_t:.1f}")
            .replace("[rH]",      f"{rh:.0f}")
            .replace("[surfRH]",  f"{surf_rh:.0f}")
            .replace("[TP]",      f"{taupunkt:.1f}")
            .replace("[Abstand]", f"{taupunkt_abstand:.1f}")
        )

    return {
        "ursache":  replace(texte["ursache"]),
        "befund1":  replace(texte["befund1"]),
        "befund2":  replace(texte["befund2"]),
        "befund3":  replace(texte["befund3"]),
    }
