# [FitBit](http://github.com/wesselb/fitbit)

[![CI](https://github.com/wesselb/fitbit/workflows/CI/badge.svg?branch=main)](https://github.com/wesselb/fitbit/actions?query=workflow%3ACI)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Retrieve data from your FitBit

## Installation

1. Clone and enter the repo.

    ```bash
    git clone https://github.com/wesselb/fitbit
    cd fitbit
    ```

2. Make a virtual environment and install the package.

    ```bash
    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements.txt -e .
    ```
   
3. Install `matplotlib` and `pandas` for the scripts:

    ```bash
    pip install matplotlib pandas
    ```

4. Generate a self-signed SSL certificate.

    ```bash
    ./generate_key.sh
    ```
   
5. Go to [dev.fitbit.com/apps](dev.fitbit.com/apps) and register a new app.
    For every URL, enter `https://localhost:4444`.
    Use application type "Personal".

6. Create an empty configuration file called `config.toml` with the following contents:

    ```
    [app]
    client_id = "<CLIENT-ID>"
    client_secret = "<CLIENT-SECRET>"

    [session]
    token = ""
    refresh_token = ""
    token_expiry_timestamp_utc = 0
    last_api_request_timestamp_utc = 0
    ```
 
    Replace `<CLIENT-ID>` and `<CLIENT-SECRET>` with the client ID and client secret
    of your newly registered app.

You are good to go!
When you perform the first authentication with the FitBit API, the browser will likely
complain that the SSL certificate is self-signed.
Click the option to accept the risks and continue.
This should only happen once.


## Usage

1. `cd` to the repository.

    ```bash
    cd fitbit
    ```
   
2. Activate the virtual environment.
 
    ```bash
    . venv/bin/activate
    ```

You can now run any script, such as any of the below.

## Plot Today's Heart Rate

```bash
python scripts/hr.py
```

## Plot Today's Heart Rate Variability

```bash
python scripts/hrv.py
```

## Plot Today's Oxygenation

```bash
python scripts/spo2.py
```

## Show Today's Breathing Rate

```bash
python scripts/br.py
```

## Scrape Everything, Starting Yesterday

```bash
python scripts/scrape.py
```

After you're happy, run the following to collate the data into nice 
data frames:
```bash
python scripts/scrape_collate.py
```

After you've done this, you can do something with the scraped data:
```bash
python scripts/scrape_do.py
```
