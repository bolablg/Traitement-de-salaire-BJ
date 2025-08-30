# %%
from tabulate import tabulate

# %% [markdown]
# # --- Configuration ---

# %%
paliers = [
    {"min": 0, "max": 60000, "rate": 0.0},
    {"min": 60000, "max": 150000, "rate": 0.1},
    {"min": 150000, "max": 250000, "rate": 0.15},
    {"min": 250000, "max": 500000, "rate": 0.19},
    {"min": 500000, "max": float('inf'), "rate": 0.3}
]

# %%
taux_cnss = 0.036 # Taux de la CNSS (Caisse Nationale de Sécurité Sociale) = 3.6%

# %% [markdown]
# # --- Fonctions fiscales ---

# %%
def calculate_tax_details(gross_salary):

    if (isinstance(gross_salary, float) or isinstance(gross_salary, int)) and gross_salary >= 0:

        remaining = gross_salary
        tax_details = []
        total_tax = 0
        social_contribution = gross_salary * taux_cnss
        total_tax += social_contribution

        for bracket in paliers:
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

        result = {
            "salaire_brut": round(gross_salary),
            "details_cotisations": [{"libelle": "Cotisation sociale", "taux": f"{taux_cnss*100:.1f}%", "montant": round(social_contribution)}],
            "details_impot": tax_details,
            "total_cotisations": round(social_contribution),
            "total_impot": round(total_tax - social_contribution),
            "total_prelevements": round(total_tax),
            "salaire_net": round(net_salary)
        }

        print(f"\nSalaire brut: {result['salaire_brut']:,} fCFA\n")

        print("Détail des cotisations:")
        cot_table = [[c['libelle'], c['taux'], f"{c['montant']:,} fCFA"] for c in result["details_cotisations"]]
        print(tabulate(cot_table, headers=["Libellé", "Taux", "Montant"], tablefmt="grid"))

        print("\nDétail des impôts par tranche:")
        imp_table = [[i['tranche'], i['taux'], f"{i['montant_imposable']:,}", f"{i['impot']:,}"] for i in result["details_impot"]]
        print(tabulate(imp_table, headers=["Tranche", "Taux", "Montant imposable", "Impôt"], tablefmt="grid"))

        print(f"\nTotal cotisations: {result['total_cotisations']:,} fCFA")
        print(f"Total impôt: {result['total_impot']:,} fCFA")
        print(f"Total prélèvements: {result['total_prelevements']:,} fCFA")
        print(f"Salaire net: {result['salaire_net']:,} fCFA")
    else:
        print("Le salaire brut doit être un nombre positif (float ou int). Veuillez réessayer avec une valeur valide.")

# %%
def calculate_gross_from_net(desired_net):
    
    if (isinstance(desired_net, float) or isinstance(desired_net, int)) and desired_net >= 0:
        def estimate_gross(net):
            gross = net * (1 + taux_cnss)
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
        
        result = {
            "salaire_net_desire": round(desired_net),
            "salaire_brut_requis": round(estimated_gross),
            "details_cotisations": tax_details["details_cotisations"],
            "details_impot": tax_details["details_impot"],
            "total_cotisations": tax_details["total_cotisations"],
            "total_impot": tax_details["total_impot"],
            "total_prelevements": tax_details["total_prelevements"]
        }

        print(f"\nSalaire net désiré: {result['salaire_net_desire']:,} fCFA")
        print(f"Salaire brut estimé à demander: {result['salaire_brut_requis']:,} fCFA\n")

        print("Détail des cotisations estimées:")
        cot_table = [[c['libelle'], c['taux'], f"{c['montant']:,} fCFA"] for c in result["details_cotisations"]]
        print(tabulate(cot_table, headers=["Libellé", "Taux", "Montant"], tablefmt="grid"))

        print("\nDétail des impôts estimés par tranche:")
        imp_table = [[i['tranche'], i['taux'], f"{i['montant_imposable']:,}", f"{i['impot']:,}"] for i in result["details_impot"]]
        print(tabulate(imp_table, headers=["Tranche", "Taux", "Montant imposable", "Impôt"], tablefmt="grid"))

        print(f"\nTotal cotisations estimées: {result['total_cotisations']:,} fCFA")
        print(f"Total impôt estimé: {result['total_impot']:,} fCFA")
        print(f"Total prélèvements estimés: {result['total_prelevements']:,} fCFA")
    else:
        print("Le salaire net désiré doit être un nombre positif (float ou int). Veuillez réessayer avec une valeur valide.")

# %% [markdown]
# # --- Fonction Principale ---

# %%
def main():
    print("Calculateur d'impôt et de cotisations sociales au Bénin")
    print("1. Calculer les détails pour un salaire brut")
    print("2. Estimer le salaire brut à demander pour un salaire net désiré")
    choice = input("Choisissez une option (1 ou 2): ")

    if choice == "1":
        gross_salary = float(input("Entrez le salaire brut en fCFA: "))
        calculate_tax_details(gross_salary)
    elif choice == "2":
        desired_net = float(input("Entrez le salaire net désiré en fCFA: "))
        calculate_gross_from_net(desired_net)
    else:
        print("Option invalide. Veuillez choisir 1 ou 2.")

# %% [markdown]
# # --- Usage ---

# %%
if __name__ == "__main__":
    main()