# mpi-sda-twitter-scraper

## Description
This is a Satellite Image scraper that uses the SentinelHub API to scrape Images for a given location and date.

## Usage
```bash
cp .env.template .env
```
### Fill in the environment variables
- sh_client_id = {ENTER THE CLIENT ID}
- sh_client_secret = {ENTER CLIENT SECRET}
- HOST={THE HOSTNAME OF THE}
- PORT={THE PORT OF THE FASTAPI APP}

### Run the container
```bash
./run.sh
```

## Development
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```