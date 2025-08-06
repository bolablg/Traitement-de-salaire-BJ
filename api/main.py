from flask import jsonify, request
from flask import make_response
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta

# --- Configuration ---
TAX_BRACKETS = [
    {"min": 0, "max": 60000, "rate": 0.0},
    {"min": 60000, "max": 150000, "rate": 0.1},
    {"min": 150000, "max": 250000, "rate": 0.15},
    {"min": 250000, "max": 500000, "rate": 0.19},
    {"min": 500000, "max": float('inf'), "rate": 0.3}
]
SOCIAL_CONTRIBUTION_RATE = 0.036
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = "1w6JQd9ldI92LwAIvi4gqO-0ts8gvpDKzHJ-pGpZfHc0"
SHEET_NAME = "Logs"
CREDENTIALS_FILE = "./intelytix-sa.json"
RATE_LIMIT = 10

# --- Fonctions fiscales ---
def calculate_tax_details(gross_salary):
    remaining = gross_salary
    tax_details = []
    total_tax = 0
    social_contribution = gross_salary * SOCIAL_CONTRIBUTION_RATE
    total_tax += social_contribution

    for bracket in TAX_BRACKETS:
        if remaining <= 0:
            break
        bracket_min = bracket["min"]
        bracket_max = bracket["max"]
        rate = bracket["rate"]

        taxable_in_bracket = min(remaining, bracket_max - bracket_min) if bracket_max != float('inf') else remaining
        
        if remaining > bracket_min:
            taxable_in_bracket = min(remaining - bracket_min, taxable_in_bracket)
        else:
            taxable_in_bracket = 0

        if taxable_in_bracket > 0:
            tax_in_bracket = taxable_in_bracket * rate
            tax_details.append({
                "tranche": (
                    f"<= {bracket_max:,} fCFA" if bracket_min == 0 else
                    f"> {bracket_min:,} fCFA" if bracket_max == float('inf') else
                    f"{bracket_min:,} - {bracket_max:,} fCFA"
                ),
                "taux": f"{rate*100:.0f}%",
                "montant_imposable": round(taxable_in_bracket),
                "impot": round(tax_in_bracket)
            })
            total_tax += tax_in_bracket

    net_salary = gross_salary - total_tax

    return {
        "salaire_brut": round(gross_salary),
        "details_cotisations": [{"libelle": "Cotisation sociale", "taux": f"{SOCIAL_CONTRIBUTION_RATE*100:.1f}%", "montant": round(social_contribution)}],
        "details_impot": tax_details,
        "total_cotisations": round(social_contribution),
        "total_impot": round(total_tax - social_contribution),
        "total_prelevements": round(total_tax),
        "salaire_net": round(net_salary)
    }


def calculate_gross_from_net(desired_net):
    def estimate_gross(net):
        gross = net * (1 + SOCIAL_CONTRIBUTION_RATE)
        tolerance = 1
        max_iterations = 100
        iteration = 0
        while iteration < max_iterations:
            tax_info = calculate_tax_details(gross)
            diff = tax_info["salaire_net"] - net
            if abs(diff) <= tolerance:
                return gross
            adjustment = max(abs(diff), 1000)
            gross += adjustment if diff < 0 else -adjustment
            iteration += 1
        return gross

    estimated_gross = estimate_gross(desired_net)
    tax_details = calculate_tax_details(estimated_gross)
    
    return {
        "salaire_net_desire": round(desired_net),
        "salaire_brut_requis": round(estimated_gross),
        "details_cotisations": tax_details["details_cotisations"],
        "details_impot": tax_details["details_impot"],
        "total_cotisations": tax_details["total_cotisations"],
        "total_impot": tax_details["total_impot"],
        "total_prelevements": tax_details["total_prelevements"]
    }


# --- Logging ---
def log_to_sheet(ip, mode, montant, statut, message):
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([now, ip, mode, montant, statut, message])
    except Exception as e:
        print(f"[LogError] {e}")

def check_rate_limit(ip):
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        rows = sheet.get_all_values()[1:]
        now = datetime.now()
        count = sum(1 for row in rows if row[1] == ip and (now - datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")) <= timedelta(hours=1))
        return count < RATE_LIMIT
    except Exception as e:
        print(f"[RateLimitError] {e}")
        return True

# --- Entrée principale ---
def main(request):
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if not check_rate_limit(ip):
        log_to_sheet(ip, "inconnu", 0, "rejet", "trop de requêtes")
        response = make_response(jsonify({"error": "Doucement champion(ne)! Ça fait trop de requêtes toi aussi. Reviens dans une heure. 😅"}), 429)
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    data = request.get_json(silent=True)
    if not data:
        log_to_sheet(ip, "inconnu", 0, "échec", "requête vide")
        response = make_response(jsonify({"error": "Requête vide"}), 400)
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    try:
        if "brut" in data:
            montant = float(data["brut"])
            if montant > 15000000:
                log_to_sheet(ip, "brut", montant, "rejet", "montant trop élevé")
                response = make_response(jsonify({
                    "stop": f"\nPardon! Montant brut de {int(montant):,} fCFA tu dis? Donc de toutes les manières plus de 10.038.500 fCFA net? Même pour un salaire de debout-suspendu, tu veux utiliser le petit programme des débrouillard(e)s? Mouff! Quitte ici... 😅😂"
                }), 400)
                response.headers.add("Access-Control-Allow-Origin", "*")
                response.headers.add("Access-Control-Allow-Headers", "Content-Type")
                response.headers.add("Access-Control-Allow-Methods", "POST")
                return response
            result = calculate_tax_details(montant)
            log_to_sheet(ip, "brut", montant, "succès", "OK")
            response = make_response(jsonify(result))
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type")
            response.headers.add("Access-Control-Allow-Methods", "POST")
            return response
        elif "net" in data:
            montant = float(data["net"])
            if montant > 10038500:
                log_to_sheet(ip, "net", montant, "rejet", "montant trop élevé")
                response = make_response(jsonify({
                    "stop": f"\nPardon! Tu veux {int(montant):,} fCFA en net tu dis? Donc de toutes les manières plus de 15 millions fCFA brut? Même pour un salaire de debout-suspendu, tu veux utiliser le petit programme des débrouillard(e)s? Mouff! Quitte ici... 😅😂"
                }), 400)
                response.headers.add("Access-Control-Allow-Origin", "*")
                response.headers.add("Access-Control-Allow-Headers", "Content-Type")
                response.headers.add("Access-Control-Allow-Methods", "POST")
                return response
            result = calculate_gross_from_net(montant)
            log_to_sheet(ip, "net", montant, "succès", "OK")
            response = make_response(jsonify(result))
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type")
            response.headers.add("Access-Control-Allow-Methods", "POST")
            return response
        else:
            log_to_sheet(ip, "inconnu", 0, "échec", "champ manquant")
            response = make_response(jsonify({"error": "Champ brut ou net attendu"}), 400)
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type")
            response.headers.add("Access-Control-Allow-Methods", "POST")
            return response
    except Exception as e:
        log_to_sheet(ip, "erreur", 0, "échec", str(e))
        response = make_response(jsonify({"error": str(e)}), 500)
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response