# Cloudflare Bypass Server for the [Ticker Scrapers](https://github.com/dhextras/ticker_scraper)

## Prerequisites

Make sure you have the following installed:

- **Python** (preferably version 3.6 or higher)
- **pip** (Python package installer)
- **virtualenv** (to create isolated Python environments)

If you don't have Python and pip installed, you can install them using the following command:

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## Setup

1. Clone the repository
2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create a `.env` or copy the `.env.example` file with the following variables:
```
CLOUDFLARE_BYPASS_SERVER_API_KEY=your_secret_api_key
```

5. Run the server
```bash
python server.py
```

## Usage

Send a POST request to `/bypass` endpoint:
```bash
curl -X POST http://localhost:5000/bypass \
    -H "Server-API-Key: your_secret_api_key" \
    -H "Content-Type: application/json" \
    -d '{"url":"https://example.com"}'
```
