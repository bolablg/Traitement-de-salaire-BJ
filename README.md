# 🇧🇯 Calculette Salaire Bénin 2025 (Brut ↔ Net)


[![Déployé sur Google Cloud Functions](https://img.shields.io/badge/Google%20Cloud-Function-blue)](https://console.cloud.google.com/functions)

Cette application permet aux salariés et chercheurs d'emploi au Bénin d’estimer leur **salaire net à partir d’un brut** ou **le salaire brut nécessaire à partir d’un net souhaité**, selon la **loi de finances 2025** du Bénin. Elle applique automatiquement le calcul de l’impôt progressif et de la cotisation sociale, avec un détail transparent de tous les prélèvements.

🔗 Démo en ligne : [https://app.bolablg.com/salaire_benin](https://app.bolablg.com/salaire_benin)

![Aperçu de l'application](./salaire_benin.png)



---

## 🚀 Fonctionnalités

- Conversion brut → net
- Conversion net → brut
- Détail des impôts par tranches
- Intégration de la cotisation sociale (3.6%)
- API REST disponible en ligne (Google Cloud Functions)
- Journalisation automatique dans Google Sheets (IP, montant, statut)
- Limitation à 10 requêtes par heure et par adresse IP

---

## 📁 Structure du projet

```
benin-salaire-api/
├── api/                  # Code Python de l'API pour Google Cloud Function
│   ├── main.py
│   ├── requirements.txt
│   └── intelytix-sa.json # la clé json de votre service account pour sauvegarder les logs dans un google sheets
├── notebooks/             # Scripts de test locaux (simulateur brut ↔ net)
│   ├── traitement_its_benin.ipynb
│   └── traitement_its_benin.py
├── web/                  # Interface HTML connectée à l’API
│   └── index.html        # Interface html déployé sur LWS
└── README.md
```

---

## ☁️ Déploiement sur Google Cloud Functions

Pour déployer le service `brut ↔ net` :

```bash
git clone https://github.com/bolablg/Traitement-de-salaire-BJ.git
cd api/
gcloud functions deploy beninSalaireAPI \
  --entry-point main \
  --runtime python310 \
  --trigger-http \
  --allow-unauthenticated
```

Assurez-vous d’avoir activé les APIs suivantes :
- Cloud Functions
- Google Sheets API
- Google Drive API

Et d’avoir un fichier `credentials.json` pour accéder au Google Sheet des logs. Si vous ne savez pas comment vous y prendre, consulter ce [tutoriel](https://blog.bolablg.com/p/google-dev-service-account) sur mon [blog](https://blog.bolablg.com).

---

## 🧪 Tests en local

Les calculs peuvent être simulés localement **sans déploiement**, à l’aide des fichiers dans le dossier `notebooks/`. Ils permettent d’explorer différents scénarios de salaire et d'affiner la logique de calcul.

Exécuter localement :

```bash
cd notebooks/
jupyter notebook traitement_its_benin.ipynb
```

---

## 🔐 Limitation & Journalisation

Chaque requête envoyée à l’API est :
- Limitée à **10 appels par heure** par adresse IP
- Journalisée dans un Google Sheet partagé, avec :
  - Adresse IP
  - Mode (brut ou net)
  - Montant
  - Statut de la requête (succès, échec, rejetée)
  - Message d'erreur éventuel

---

## 📄 Loi de référence

Les calculs sont basés sur la [loi de finances 2025 du Bénin (PDF)](https://finances.bj/wp-content/uploads/2025/01/Benin-Code-General-des-Impots-2025.pdf).

---

## 👨‍💻 Auteur

Projet développé par **Bolaji** • [bolablg.com](https://bolablg.com)

---

N’hésitez pas à proposer des améliorations via *issue* ou *pull request*.

---

## 📜 Licence

Ce projet est distribué sous la licence **GNU General Public License v3.0**.

Vous êtes libre de :
- Utiliser, copier, modifier et redistribuer le code
- Tant que vous conservez la même licence (copyleft)

➡️ [Voir la licence complète](https://www.gnu.org/licenses/gpl-3.0.html)