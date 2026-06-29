---
name: cloudflare_web_scraper
description: "Scrapea sitios que requieren JavaScript/Cloudflare usando Cloudflare Browser Rendering. Requiere variables de entorno CLOUDFLARE_ACCOUNT_ID y CLOUDFLARE_API_TOKEN."
version: 1.0.0
metadata:
  hermes:
    tags: [web, scraping, cloudflare, browser-rendering]
---

# Cloudflare Web Scraper

## Requisitos
- Python 3
- Paquetes: `requests`, `python-dotenv`
- Variables de entorno:
  - `CLOUDFLARE_ACCOUNT_ID`
  - `CLOUDFLARE_API_TOKEN`

## Instalación
```bash
pip install requests python-dotenv
```

## Uso
```python
from scripts.scrape import scrape

result = scrape("https://example.com", output_format="markdown")
print(result["content"])
```

## Formato salida
- `{"success": true, "content": "...", "format": "..."}`
- `{"success": false, "error": "..."}`
