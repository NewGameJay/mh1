# DataForSEO Quick Reference

## API Endpoints (V3)

### Google Organic SERP (Live)
`POST https://api.dataforseo.com/v3/serp/google/organic/live/advanced`

Payload:
```json
[
  {
    "language_code": "en",
    "location_code": 2840,
    "keyword": "your keyword"
  }
]
```

### Location Codes
- **United States**: 2840
- **United Kingdom**: 2826
- **Canada**: 2124
- **Australia**: 2036
- **Germany**: 2276
- **France**: 2250
- **Spain**: 2724

### Language Codes
- **English**: "en"
- **Spanish**: "es"
- **French**: "fr"
- **German**: "de"

## Python Snippet

```python
import requests

url = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
payload = [{"keyword": "test", "location_code": 2840, "language_code": "en"}]
headers = {
    'Authorization': 'Basic <BASE64_CREDS>',
    'Content-Type': 'application/json'
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```



