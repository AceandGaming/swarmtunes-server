# Contributing

## Helping

This project is open to contributions. The following guide will help you set up and run the server locally.

## Setup

[Python](https://www.python.org/) is required to run this project. Optionally [uv](https://docs.astral.sh/uv/) can be used to manage this project.

1. Fork the project

2. Clone the fork with `git`

    ```bash
    git clone https://github.com/{your-user}/swarmtunes-server.git
    cd swarmtunes-server
    ```

3. Install the project from `pyproject.toml`

    * If using `uv`

    ```bash
    uv sync
    ```

    * If using `pip`

    ```bash
    pip install -e .
    ```

4. Google Drive API is required to automatically download songs. Here is one way to get a key:

    1. Go to console.cloud.google.com and create a new project

    2. Go to APIs & Services

    3. Enable -> Google Drive API

    4. OAuth Client Services

        i. Setup (fill in) -> External

        ii. Audience -> Ensure your account is under Test Users

    5. Credentials -> Create -> Desktop App -> Download JSON -> credentials.json

5. HTTPS is required for CORS connections. This requires a `cert.pem` and `key.pem`.

    * If using [`mkcert`](https://github.com/FiloSottile/mkcert)

    ```bash
    mkcert -install
    mkcert -key-file key.pem -cert-file cert.pem localhost.com
    ```

    b. If using `openssl`

    ```bash
    openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out cert.pem -keyout key.pem
    ```

## Running

This project uses [`uvicorn`](https://uvicorn.dev/) to run the server.

The basic command to run the server is:

```bash
DATA_PATH=data LOCAL=true uvicorn server:app --host 0.0.0.0 --port 8001 --reload --ssl-certfile="./cert.pem" --ssl-keyfile="./key.pem"
```

Environment Variables:

* `DATA_PATH` defines where to look for songs/mp3s. It also causes the server to not download any new songs.

  * WARNING: Running without this variable will cause the server to auto-download every song covered! This is around 4-8GB of data for which the server will NOT be active while downloading.

* `LOCAL` if set, will disable `nginx` functions so that the server can run locally

Additional scripts:

* `dev.sh` runs the server in development mode
* `run.sh` runs the server in production mode

## Pull Requests

After pushing changes to your fork, you can create a [Pull Request](https://github.com/AceandGaming/swarmtunes-server/pulls)
