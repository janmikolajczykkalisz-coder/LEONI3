from flask import (
    Flask, render_template, request, send_file, redirect,
    make_response, url_for
)
from datetime import datetime
import zoneinfo

from database import (
    init_db,
    save_history,
    save_details,
    delete_card,
    delete_stone,
    get_history_filtered,
    get_details_filtered,
    get_card_data,
    export_to_excel_transposed
)

from generated_code_utils import generate_unique_satznummer
from pdf_utils import generate_pdf_bytes
from label_utils import generate_label_pdf
from data import (
    DIAMETERS_SET_1, DIAMETERS_SET_2, DIAMETERS_SET_3,
     TRANSLATIONS, ZESTAWY
)

app = Flask(__name__)
# app.secret_key = "zmien_na_bezpieczny_secret"

# init DB (idempotent)
init_db()

def get_lang():
    lang = request.cookies.get("lang")
    return lang if lang in ("pl", "de") else "pl"

@app.route('/set_lang/<lang_code>')
def set_lang(lang_code):
    if lang_code not in ("pl", "de"):
        lang_code = "pl"
    resp = make_response(redirect(request.referrer or url_for('index')))
    resp.set_cookie("lang", lang_code, max_age=60*60*24*365)
    return resp

@app.route("/", methods=["GET", "POST"])
def index():
    lang = get_lang()
    t = TRANSLATIONS[lang]

    if request.method == "POST":
        satznummer = request.form.get("satznummer") or generate_unique_satznummer()
        machine_number = request.form.get("machine_number", "")
        selected_set = request.form.get("diameter_set", "3")
        stone_type = request.form.get("stone_type", "ND")
        operator = request.form.get("operator", "")

        codes, diameters = [], []
        i = 0
        while True:
            code = request.form.get(f"code{i}")
            diameter = request.form.get(f"diameter{i}")
            if code is None and diameter is None:
                break
            if code:
                codes.append(code.strip())
            diameters.append(float(diameter) if diameter else 0.0)
            i += 1

        set_name = ZESTAWY.get(selected_set, "")

        pdf_bytes = generate_pdf_bytes(
            codes=codes,
            satznummer=satznummer,
            diameters=diameters,
            machine_number=machine_number,
            stone_count=len([c for c in codes if c]),
            stone_type=stone_type,
            set_name=set_name,
            operator=operator,
        )

        try:
            local_time = datetime.now(zoneinfo.ZoneInfo("Europe/Warsaw")).strftime("%Y-%m-%d %H:%M:%S")
            save_history(satznummer, machine_number, selected_set, local_time)
            save_details(satznummer, codes, diameters)
        except Exception:
            pass

        pdf_bytes.seek(0)
        return send_file(pdf_bytes, as_attachment=True,
                         download_name=f"Satzkarten_{satznummer}.pdf",
                         mimetype="application/pdf")

    generated_satznummer = generate_unique_satznummer()
    return render_template(
        "index.html",
        diams=DIAMETERS_SET_3,
        generated_satznummer=generated_satznummer,
        lang=lang,
        t=t,
        set1=DIAMETERS_SET_1,
        set2=DIAMETERS_SET_2,
        set3=DIAMETERS_SET_3
    )

@app.route("/history")
def history():
    lang = get_lang()
    t = TRANSLATIONS[lang]

    # numer strony z query string, domyślnie 1
    page = int(request.args.get("page", 1))
    per_page = 50  # np. 50 rekordów na stronę

    filters = {
        "satznummer": request.args.get("satznummer", ""),
        "machine": request.args.get("machine", ""),
        "zestaw": request.args.get("zestaw", ""),
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
        "code": request.args.get("code", ""),
        "diameter": request.args.get("diameter", "")
    }

    history_rows = get_history_filtered(
        satznummer=filters["satznummer"],
        machine=filters["machine"],
        zestaw=filters["zestaw"],
        date_from=filters["date_from"],
        date_to=filters["date_to"]
    )

    details_rows = get_details_filtered(
        satznummer=filters["satznummer"],
        machine=filters["machine"],
        zestaw=filters["zestaw"],
        date_from=filters["date_from"],
        date_to=filters["date_to"],
        code=filters["code"],
        diameter=filters["diameter"],
        page=page,
        per_page=per_page
    )

    return render_template(
        "history.html",
        history=history_rows,
        details=details_rows,
        filters=filters,
        page=page,
        per_page=per_page,
        lang=lang,
        t=t
    )

@app.route("/export_card/<satznummer>")
def export_card(satznummer):
    excel_bytes = export_to_excel_transposed(satznummer=satznummer)
    excel_bytes.seek(0)
    return send_file(
        excel_bytes,
        as_attachment=True,
        download_name=f"export_karta_{satznummer}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/download_pdf/<satznummer>")
def download_pdf(satznummer):
    card_data = get_card_data(satznummer)
    if not card_data:
        return "Nie znaleziono karty", 404

    machine, zestaw, details = card_data
    codes = [row[0] for row in details]
    diameters = [row[1] for row in details]
    set_name = ZESTAWY.get(str(zestaw), "")

    pdf_bytes = generate_pdf_bytes(
        codes=codes,
        satznummer=satznummer,
        diameters=diameters,
        machine_number=machine,
        stone_count=len(codes),
        stone_type="ND",
        set_name=set_name,
        operator="",
    )

    pdf_bytes.seek(0)
    return send_file(pdf_bytes, as_attachment=True,
                     download_name=f"Satzkarten_{satznummer}.pdf",
                     mimetype="application/pdf")

@app.route("/delete/<satznummer>", methods=["POST"])
def delete_card_route(satznummer):
    delete_card(satznummer)
    return redirect(url_for("history"))

@app.route("/delete_stone/<int:stone_id>", methods=["POST"])
def delete_stone_route(stone_id):
    delete_stone(stone_id)
    return redirect(url_for("history"))

@app.route("/generate_label_direct", methods=["POST"])
def generate_label_direct():
    satznummer = request.form.get("satznummer") or generate_unique_satznummer()
    selected_set = request.form.get("diameter_set", "3")
    set_name = ZESTAWY.get(selected_set, "Zestaw")
    stone_count = len([k for k in request.form.keys() if k.startswith("code")])
    pdf_bytes = generate_label_pdf(set_name=set_name, stone_count=stone_count, uuid_code=satznummer)
    pdf_bytes.seek(0)
    return send_file(pdf_bytes, as_attachment=True,
                     download_name=f"naklejka_{satznummer}.pdf",
                     mimetype="application/pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
