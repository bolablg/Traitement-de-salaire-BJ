# 🇧🇯 Benin Salary Calculator API

[![Deployed on Google Cloud Functions](https://img.shields.io/badge/Google%20Cloud-Function-blue)](https://console.cloud.google.com/functions)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A Google Cloud Functions API for calculating salary conversions (gross to net, net to gross) according to **Benin's 2025 Finance Law**. This application helps employees and job seekers in Benin estimate their **net salary from gross** or determine the **required gross salary from desired net pay**.

🔗 **Live Demo:** [https://app.bolablg.com/salaire_benin](https://app.bolablg.com/salaire_benin)

## Features

- ✅ Gross salary to net salary conversion
- ✅ Net salary to gross salary conversion  
- ✅ Detailed tax bracket calculations
- ✅ Social contribution calculations
- ✅ Rate limiting and logging
- ✅ CORS support for web applications
- ✅ Input validation and error handling
- ✅ French number formatting

## API Endpoints

### POST `/` 
Calculate salary conversions

**Request Body:**
```json
// Gross to Net
{
  "brut": 500000
}

// Net to Gross  
{
  "net": 400000
}
```

**Response:**
```json
{
  "salaire_brut": 500000,
  "salaire_net": 463800,
  "details_cotisations": [
    {
      "libelle": "Cotisation sociale",
      "taux": "3.6%", 
      "montant": 18000
    }
  ],
  "details_impot": [
    {
      "tranche": "<= 60.000 fCFA",
      "taux": "0%",
      "montant_imposable": 60000,
      "impot": 0
    }
  ],
  "total_cotisations": 18000,
  "total_impot": 18200,
  "total_prelevements": 36200
}
```

## 💰 Tax Configuration (Benin 2025)

| Income Bracket (fCFA) | Tax Rate |
|----------------------|----------|
| ≤ 60,000 | 0% |
| 60,001 - 150,000 | 10% |
| 150,001 - 250,000 | 15% |
| 250,001 - 500,000 | 19% |
| > 500,000 | 30% |

**Social Contribution Rate:** 3.6%

> **Note:** fCFA = West African CFA franc (currency used in Benin)

## 📁 Project Structure

```
beninSalaireAPI/
├── main.py                 # Main Cloud Function entry point
├── requirements.txt        # Python dependencies
├── dev-requirements.txt    # Development dependencies
├── .env                    # Local environment variables (not committed)
├── local/                  # Local development files
│   ├── run-local.sh       # Local development server script
│   ├── traitement_its_benin.ipynb  # Jupyter notebook for testing
│   └── traitement_its_benin.py     # Python script version
├── tests/                  # Test files
│   ├── test_main.py       # Unit tests
│   └── run-tests.sh       # Test runner script
├── .github/workflows/     # CI/CD pipeline
│   └── deploy.yml         # GitHub Actions deployment
└── old/                   # Legacy project files
```

## 🚀 Development

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bolablg/Traitement-de-salaire-BJ.git
   cd Traitement-de-salaire-BJ
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r dev-requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `.env.example` to `.env` 
   - Configure your environment variables (see `.env.example` for reference)

4. **Set up service account:**
   - Create a Google Cloud service account
   - Download the JSON key file to your preferred location
   - Enable Google Sheets API and Google Drive API
   - Update your `.env` file with the correct path

5. **Run locally:**
   ```bash
   ./local/run-local.sh
   ```

### 🧪 Local Testing with Jupyter Notebook

Explore salary calculations interactively:

```bash
cd local/
jupyter notebook traitement_its_benin.ipynb
```

### 🧪 Testing

**Run tests:**
```bash
./tests/run-tests.sh
```

**Manual API testing:**
```bash
# Test gross to net conversion
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"brut": 500000}'

# Test net to gross conversion  
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"net": 400000}'
```

## ☁️ Deployment

### Automatic Deployment (GitHub Actions)

1. **Set up GitHub Secrets:**
   - `GCP_SA_KEY`: Your service account JSON key content
   - `GCP_PROJECT_ID`: Your Google Cloud project ID  
   - `GCP_REGION`: Deployment region
   - `SA_KEY_PATH`: Path for service account key file
   - `SHEET_ID`: Google Sheets ID for logging
   - `SHEET_NAME`: Sheet name for logging
   - Other environment variables as needed

2. **Deploy:**
   ```bash
   git push origin production
   ```

The GitHub Action will automatically deploy to Cloud Functions.

### Manual Deployment

**Note:** This project uses **2nd generation Google Cloud Functions**.

```bash
gcloud functions deploy beninSalaireAPI2 \
  --gen2 \
  --runtime=python310 \
  --region=$GCP_REGION \
  --source=. \
  --entry-point=main \
  --trigger-http \
  --allow-unauthenticated \
  --memory=256Mi \
  --timeout=60s
```

## 📊 Rate Limiting

- **Limit:** 10 requests per hour per IP address
- **Storage:** Google Sheets logging
- **Response:** 429 status code when exceeded

## 🔒 Security Features

- Input validation and sanitization
- Rate limiting by IP address
- Error logging and monitoring
- CORS headers configuration
- Service account authentication

## ⚠️ Error Handling

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Invalid request format |
| 422 | Input value too high |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

## 🌐 Frontend Integration

This API powers the [BOLABLG Salary Calculator](https://app.bolablg.com/salaire_benin) web application.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🔐 Rate Limiting & Logging

Each API request is:
- **Limited to 10 calls per hour** per IP address
- **Logged to a Google Sheet** with the following data:
  - IP address
  - Calculation mode (gross or net)
  - Amount
  - Request status (success, failure, rejected)
  - Error message (if any)

## 📄 Legal Reference

Calculations are based on [Benin's 2025 Finance Law](https://finances.bj/wp-content/uploads/2025/01/Benin-Code-General-des-Impots-2025.pdf).

## License

This project is distributed under the **GNU General Public License v3.0**.

You are free to:
- Use, copy, modify and redistribute the code
- As long as you keep the same license (copyleft)

➡️ [See full license](https://www.gnu.org/licenses/gpl-3.0.html)

## Author

**Bolaji BALOGOUN** - Data Science & AI Engineer

- 🌐 Website: [bolablg.com](https://bolablg.com)
- 🐱 GitHub: [@bolablg](https://github.com/bolablg)
- 💼 LinkedIn: [bolablg](https://linkedin.com/in/bolablg)

---

Feel free to suggest improvements via *issues* or *pull requests*!