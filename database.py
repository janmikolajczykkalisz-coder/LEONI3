import sqlite3
import pandas as pd
from io import BytesIO
from data import ZESTAWY  # potrzebne do mapowania nazw zestawów

DB_NAME = "satzkarten.db"

# --- Inicjalizacja bazy ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            satznummer TEXT,
            machine TEXT,
            zestaw TEXT,
            data TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            satznummer TEXT,
            code TEXT,
            diameter REAL,
            status TEXT DEFAULT 'Nowy',
            FOREIGN KEY (satznummer) REFERENCES history(satznummer)
        )
    """)

    cursor.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    conn.close()


# --- Zapisywanie historii ---
def save_history(satznummer, machine, zestaw, data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO history (satznummer, machine, zestaw, data) VALUES (?, ?, ?, ?)",
        (satznummer, machine, zestaw, data)
    )
    conn.commit()
    conn.close()


# --- Zapisywanie szczegółów ---
def save_details(satznummer, codes, diameters):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for code, dia in zip(codes, diameters):
        cursor.execute(
            "INSERT INTO details (satznummer, code, diameter, status) VALUES (?, ?, ?, ?)",
            (satznummer, code, dia, "Nowy")
        )
    conn.commit()
    conn.close()


# --- Pobieranie historii z filtrami (zwraca słowniki) ---
def get_history_filtered(satznummer="", machine="", zestaw="", date_from="", date_to=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = "SELECT id, satznummer, machine, zestaw, data FROM history WHERE 1=1"
    params = []
    if satznummer:
        query += " AND satznummer LIKE ?"
        params.append(f"%{satznummer}%")
    if machine:
        query += " AND machine LIKE ?"
        params.append(f"%{machine}%")
    if zestaw:
        query += " AND zestaw = ?"
        params.append(zestaw)
    if date_from:
        query += " AND date(data) >= date(?)"
        params.append(date_from)
    if date_to:
        query += " AND date(data) <= date(?)"
        params.append(date_to)

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "satznummer": r[1],
            "machine": r[2],
            "zestaw": r[3],
            "data": r[4],
            "zestaw_name": ZESTAWY.get(str(r[3]), r[3])
        })
    return result


# --- Pobieranie szczegółów z filtrami (zwraca słowniki) ---
def get_details_filtered(
    satznummer="",
    machine="",
    zestaw="",
    date_from="",
    date_to="",
    code="",
    diameter="",
    page=1,
    per_page=50
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = """
        SELECT d.id, d.satznummer, d.code, d.diameter, d.status,
               h.machine, h.zestaw, h.data
        FROM details d
        JOIN history h ON d.satznummer = h.satznummer
        WHERE 1=1
    """
    params = []
    if satznummer:
        query += " AND d.satznummer LIKE ?"
        params.append(f"%{satznummer}%")
    if machine:
        query += " AND h.machine LIKE ?"
        params.append(f"%{machine}%")
    if zestaw:
        query += " AND h.zestaw = ?"
        params.append(zestaw)
    if date_from:
        query += " AND date(h.data) >= date(?)"
        params.append(date_from)
    if date_to:
        query += " AND date(h.data) <= date(?)"
        params.append(date_to)
    if code:
        query += " AND d.code LIKE ?"
        params.append(f"%{code}%")
    if diameter:
        query += " AND d.diameter = ?"
        params.append(diameter)

    # paginacja
    query += " ORDER BY d.id DESC LIMIT ? OFFSET ?"
    params.append(per_page)
    params.append((page - 1) * per_page)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "satznummer": r[1],
            "code": r[2],
            "diameter": r[3],
            "status": r[4],
            "machine": r[5],
            "zestaw": r[6],
            "data": r[7],
            "zestaw_name": ZESTAWY.get(str(r[6]), r[6])
        })
    return result


# --- Pobieranie pełnych danych karty ---
def get_card_data(satznummer):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT machine, zestaw, data FROM history WHERE satznummer = ?", (satznummer,))
    history_row = cursor.fetchone()
    if not history_row:
        conn.close()
        return None

    machine, zestaw, _ = history_row
    cursor.execute("SELECT code, diameter FROM details WHERE satznummer = ?", (satznummer,))
    details = cursor.fetchall()
    conn.close()
    return machine, zestaw, details


# --- Usuwanie ---
def delete_card(satznummer):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM details WHERE satznummer = ?", (satznummer,))
    cursor.execute("DELETE FROM history WHERE satznummer = ?", (satznummer,))
    conn.commit()
    conn.close()

def delete_stone(stone_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM details WHERE id = ?", (stone_id,))
    conn.commit()
    conn.close()


# --- Eksporty ---
def export_to_excel(satznummer=None, zestaw=None):
    conn = sqlite3.connect(DB_NAME)
    query = """
        SELECT h.satznummer, h.machine, h.zestaw,
               d.code, d.diameter, d.status
        FROM history h
        JOIN details d ON h.satznummer = d.satznummer
        WHERE 1=1
    """
    params = []
    if zestaw:
        query += " AND h.zestaw = ?"
        params.append(zestaw)
    if satznummer:
        query += " AND h.satznummer = ?"
        params.append(satznummer)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Karta")
        worksheet = writer.sheets["Karta"]
        for col in worksheet.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            worksheet.column_dimensions[col_letter].width = max_length + 2
        worksheet.auto_filter.ref = worksheet.dimensions
    output.seek(0)
    return output


def export_to_excel_transposed(satznummer=None, zestaw=None):
    conn = sqlite3.connect(DB_NAME)

    query = """
        SELECT h.satznummer, h.machine, h.zestaw,
               d.code, d.diameter, d.status
        FROM history h
        JOIN details d ON h.satznummer = d.satznummer
        WHERE 1=1
    """
    params = []
    if zestaw:
        query += " AND h.zestaw = ?"
        params.append(zestaw)
    if satznummer:
        query += " AND h.satznummer = ?"
        params.append(satznummer)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    # --- transpozycja ---
    df_transposed = df.T
    df_transposed.reset_index(inplace=True)
    df_transposed.columns.values[0] = "Pole"

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_transposed.to_excel(writer, index=False, sheet_name="Karta")

        worksheet = writer.sheets["Karta"]
        for col in worksheet.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            worksheet.column_dimensions[col_letter].width = max_length + 2
        worksheet.auto_filter.ref = worksheet.dimensions

    output.seek(0)
    return output
