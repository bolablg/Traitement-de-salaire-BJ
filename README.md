# 🇧🇯 Benin Salary Calculator API

A Google Cloud Functions API for calculating salary conversions (gross to net, net to gross) according to Benin's 2025 Finance Law.

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

## Tax Configuration (2025)

| Income Bracket | Tax Rate |
|----------------|----------|
| ≤ 60,000 fCFA | 0% |
| 60,001 - 150,000 fCFA | 10% |
| 150,001 - 250,000 fCFA | 15% |
| 250,001 - 500,000 fCFA | 19% |
| > 500,000 fCFA | 30% |

**Social Contribution Rate:** 3.6%

## Development

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bolablg/benin-salaire-api.git
   cd benin-salaire-api
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up service account:**
   - Create a Google Cloud service account
   - Download the JSON key file as `intelytix-sa.json`
   - Enable Google Sheets API

4. **Test locally:**
   ```bash
   functions-framework --target=main --debug
   ```

### Testing

Test with curl:
```bash
# Test gross to net
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"brut": 500000}'

# Test net to gross
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"net": 400000}'
```

## Deployment

### Automatic Deployment (GitHub Actions)

1. **Set up GitHub Secrets:**
   - `GCP_SA_KEY`: Your service account JSON key (base64 encoded)
   - `GCP_PROJECT_ID`: Your Google Cloud project ID
   - `GCP_REGION`: Deployment region (e.g., `us-central1`)

2. **Deploy:**
   ```bash
   git push origin main
   ```

The GitHub Action will automatically deploy to Cloud Functions.

### Manual Deployment

```bash
gcloud functions deploy benin-salaire-calculator \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=main \
  --trigger-http \
  --allow-unauthenticated
```

## Rate Limiting

- **Limit:** 10 requests per hour per IP address
- **Storage:** Google Sheets logging
- **Response:** 429 status code when exceeded

## Security Features

- Input validation and sanitization
- Rate limiting by IP address
- Error logging and monitoring
- CORS headers configuration
- Service account authentication

## Error Handling

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Invalid request format |
| 422 | Input value too high |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

## Frontend Integration

This API is used by the [BOLABLG Salary Calculator](https://app.bolablg.com/salaire_benin) frontend application.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Author

**Bolaji BALOGOUN** - Data Science & AI Engineer
- Website: [bolablg.com](https://bolablg.com)
- GitHub: [@bolablg](https://github.com/bolablg)
- LinkedIn: [bolablg](https://linkedin.com/in/bolablg)