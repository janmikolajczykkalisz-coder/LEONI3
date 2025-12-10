# --- Zestawy średnic ---

DIAMETERS_SET_3 = [
    1.5830, 1.4100, 1.2560, 1.1190, 0.9970,
    0.8880, 0.7910, 0.7049, 0.6280, 0.5590
]

DIAMETERS_SET_2 = [
    0.5089, 0.4620, 0.4200, 0.3820, 0.3470,
    0.3158, 0.2870, 0.2610, 0.2373, 0.2150
]

DIAMETERS_SET_1 = [
    0.2011, 0.1878, 0.1749, 0.1631, 0.1521,
    0.1418, 0.1323, 0.1233, 0.1150, 0.1072
]
DIAMETERS_BY_SET = {
    "1": DIAMETERS_SET_1,
    "2": DIAMETERS_SET_2,
    "3": DIAMETERS_SET_3
}
ZESTAWY = {"1": "Untersatz", "2": "Mittelsatz", "3": "Grundsatz"}
TRANSLATIONS = {
    "pl": {
        "title": "Generator SATZ-KARTE",
        "satz_label": "Numer karty setu :",
        "operator_label": "Operator:",
        "select_set_label": "Wybierz zestaw średnic:",
        "machine_label": "Numer maszyny:",
        "stone_type_label": "Typ kamienia:",
        "col_code": "Kod kamienia",
        "col_diameter": "Średnica (mm)",
        "col_action": "Akcja",
        "add_stone": "Dodaj kamień",
        "generate_pdf": "Generuj etykietę PDF",
        "generate_label": "Generuj Naklejkę",
        "history_link": "📜 Zobacz historię zapisanych kart",
        "lang_toggle_title": "Przełącz język PL/DE"
    },
    "de": {
        "title": "Generator SATZ-KARTE",
        "satz_label": "Satzkartennummer:",
        "operator_label": "Bearbeiter:",
        "select_set_label": "Wählen Sie den Durchmessersatz:",
        "machine_label": "Maschinennummer:",
        "stone_type_label": "Steintyp:",
        "col_code": "Steincode",
        "col_diameter": "Durchmesser (mm)",
        "col_action": "Aktion",
        "add_stone": "Stein hinzufügen",
        "generate_pdf": "PDF erstellen",
        "generate_label": "Etikett erstellen",
        "history_link": "📜 Gespeicherte Karten ansehen",
        "lang_toggle_title": "Sprache umschalten PL/DE"
    }
}
