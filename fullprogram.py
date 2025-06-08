import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from flask import request
from tabulate import tabulate

# Configuration des tranches d'imposition selon la loi de finance 2025 (Bénin)
TAX_BRACKETS = [
    {"min": 0, "max": 60000, "rate": 0.0},
    {"min": 60001, "max": 150000, "rate": 0.1},
    {"min": 150001, "max": 250000, "rate": 0.15},
    {"min": 250001, "max": 500000, "rate": 0.19},
    {"min": 500001, "max": float('inf'), "rate": 0.3}
]

# Cotisation sociale (3.6% du salaire brut)
SOCIAL_CONTRIBUTION_RATE = 0.036

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = "TON_SHEET_ID_ICI"
SHEET_RANGE = "Feuille1"
CREDENTIALS_FILE = "creds.json"
RATE_LIMIT = 5

def log_to_sheet(ip, mode, montant, statut, message):
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_RANGE)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [now, ip, mode, montant, statut, message]
        sheet.append_row(row)
    except Exception as e:
        print(f"[WARN] Erreur lors du log: {e}")

def check_rate_limit(ip):
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_RANGE)
        rows = sheet.get_all_values()[1:]  # skip header
        count = 0
        now = datetime.now()
        for row in rows:
            ts_str, row_ip = row[0], row[1]
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            if row_ip == ip and (now - ts) <= timedelta(hours=1):
                count += 1
        return count < RATE_LIMIT
    except Exception as e:
        print(f"[WARN] Erreur vérification quota IP: {e}")
        return True

def calculate_tax_details(gross_salary):
    """
    Calcule les taxes à partir du salaire brut et retourne le détail par tranche + le net
    Args:
        gross_salary (float): Salaire brut
        month (str, optional): Mois pour la redevance ORTB ('march' ou 'june')
    Returns:
        dict: Détail des taxes et salaire net
    """
    remaining = gross_salary
    tax_details = []
    total_tax = 0
    
    # 1. Calcul de la cotisation sociale (3.6% du brut)
    social_contribution = gross_salary * SOCIAL_CONTRIBUTION_RATE
    total_tax += social_contribution
    
    # 2. Calcul de l'impôt par tranche
    for bracket in TAX_BRACKETS:
        if remaining <= 0:
            break
        
        bracket_min = bracket["min"]
        bracket_max = bracket["max"]
        rate = bracket["rate"]
        
        # Ne considérer que la partie du salaire dans cette tranche
        taxable_in_bracket = min(remaining, bracket_max - bracket_min + 1) if bracket_max != float('inf') else remaining
        if remaining > bracket_min:
            taxable_in_bracket = min(remaining - bracket_min, taxable_in_bracket)
        else:
            taxable_in_bracket = 0
        
        if taxable_in_bracket > 0:
            tax_in_bracket = taxable_in_bracket * rate
            tax_details.append({
                "tranche": f"{bracket_min:,} - {bracket_max:,} FCFA",
                "taux": f"{rate*100:.0f}%",
                "montant_imposable": round(taxable_in_bracket),
                "impot": round(tax_in_bracket)
            })
            total_tax += tax_in_bracket
    
    net_salary = gross_salary - total_tax
    
    return {
        "salaire_brut": round(gross_salary),
        "details_cotisations": [
            {
                "libelle": "Cotisation sociale",
                "taux": f"{SOCIAL_CONTRIBUTION_RATE*100:.1f}%",
                "montant": round(social_contribution)
            }
        ],
        "details_impot": tax_details,
        "total_cotisations": round(social_contribution),
        "total_impot": round(total_tax - social_contribution),  # Impôt seulement (hors cotisation)
        "total_prelevements": round(total_tax),  # Total cotisation + impôt
        "salaire_net": round(net_salary)
    }

def calculate_gross_from_net(desired_net):
    """
    Calcule le salaire brut nécessaire pour obtenir le salaire net désiré
    Args:
        desired_net (float): Salaire net désiré
        month (str, optional): Mois pour la redevance ORTB ('march' ou 'june')
    Returns:
        dict: Détail des taxes et salaire brut à demander
    """
    # Fonction pour estimer le brut à partir du net (méthode par approximation)
    def estimate_gross(net):
        # Estimation initiale en tenant compte de la cotisation sociale
        gross = net * (1 + SOCIAL_CONTRIBUTION_RATE)  # Première approximation
        tolerance = 1  # 1 FCFA de précision
        max_iterations = 100
        iteration = 0
        
        while iteration < max_iterations:
            tax_info = calculate_tax_details(gross)
            calculated_net = tax_info["salaire_net"]
            difference = calculated_net - desired_net
            
            if abs(difference) <= tolerance:
                return gross
            
            # Ajustement proportionnel
            adjustment = max(abs(difference), 1000)  # Au moins 1000 FCFA d'ajustement
            if calculated_net < desired_net:
                gross += adjustment
            else:
                gross -= adjustment
            
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

if __name__ == "__main__":
    print("=== Calculette Salaire (Bénin 2025) ===")
    mode = input("Souhaites-tu partir d’un salaire brut ou net ? ").strip().lower()

    if mode not in ["brut", "net"]:
        print("❌ Entrée invalide. Veuille saisir 'brut' ou 'net' s'il te plaît.")
        log_to_sheet(ip, mode, "", "erreur", "Entrée invalide ou échec de traitement")
        exit()

    montant = input(f"Entre le montant du salaire {mode} en FCFA : ").replace(" ", "")
    try:
        montant = int(montant)
    except ValueError:
        print("❌ Veuille saisir un nombre entier s'il te plaît.")
        log_to_sheet(ip, mode, montant, "erreur", "Entrée invalide ou échec de traitement")
        exit()

    try:
        if mode == "brut":
            result = calculate_tax_details(montant)
            log_to_sheet(ip, mode, montant, "succès", "OK")
            print(f"\nSalaire brut: {result['salaire_brut']:,} FCFA\n")

            print("Détail des cotisations:")
            cot_table = [[c['libelle'], c['taux'], f"{c['montant']:,} FCFA"] for c in result["details_cotisations"]]
            print(tabulate(cot_table, headers=["Libellé", "Taux", "Montant"], tablefmt="grid"))

            print("\nDétail des impôts par tranche:")
            imp_table = [[i['tranche'], i['taux'], f"{i['montant_imposable']:,}", f"{i['impot']:,}"] for i in result["details_impot"]]
            print(tabulate(imp_table, headers=["Tranche", "Taux", "Montant imposable", "Impôt"], tablefmt="grid"))

            print(f"\nTotal cotisations: {result['total_cotisations']:,} FCFA")
            print(f"Total impôt: {result['total_impot']:,} FCFA")
            print(f"Total prélèvements: {result['total_prelevements']:,} FCFA")
            print(f"Salaire net: {result['salaire_net']:,} FCFA")

        else:  # mode == "net"
            result = calculate_gross_from_net(montant)
            log_to_sheet(ip, mode, montant, "succès", "OK")
            print(f"\nSalaire net désiré: {result['salaire_net_desire']:,} FCFA")
            print(f"Salaire brut estimé à demander: {result['salaire_brut_requis']:,} FCFA\n")

            print("Détail des cotisations estimées:")
            cot_table = [[c['libelle'], c['taux'], f"{c['montant']:,} FCFA"] for c in result["details_cotisations"]]
            print(tabulate(cot_table, headers=["Libellé", "Taux", "Montant"], tablefmt="grid"))

            print("\nDétail des impôts estimés par tranche:")
            imp_table = [[i['tranche'], i['taux'], f"{i['montant_imposable']:,}", f"{i['impot']:,}"] for i in result["details_impot"]]
            print(tabulate(imp_table, headers=["Tranche", "Taux", "Montant imposable", "Impôt"], tablefmt="grid"))

            print(f"\nTotal cotisations estimées: {result['total_cotisations']:,} FCFA")
            print(f"Total impôt estimé: {result['total_impot']:,} FCFA")
            print(f"Total prélèvements estimés: {result['total_prelevements']:,} FCFA")
    except Exception:
        log_to_sheet(ip, mode, montant, "erreur", "Entrée invalide ou échec de traitement")
        raise