# Contributing

Swarmtunes is open to contributions! The following guide will help you set up and run the server locally.

## Requirements

1. Google Drive API is required to automatically download songs. Here is one way to get a key:

    1. Go to console.cloud.google.com and create a new project

    2. Go to APIs & Services

    3. Enable -> Google Drive API

    4. OAuth Client Services

        i. Setup (fill in) -> External

        ii. Audience -> Ensure your account is under Test Users

    5. Credentials -> Create -> Desktop App -> Download JSON -> credentials.json

2. HTTPS is required for CORS connections. This requires a `cert.pem` and `key.pem`.

    a. If using [`mkcert`](https://github.com/FiloSottile/mkcert)

    ```bash
    mkcert -install
    mkcert -key-file key.pem -cert-file cert.pem localhost.com
    ```

    b. If using `openssl`

    ```bash
    openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out cert.pem -keyout key.pem
    ```

## Setup

For most users, **Docker is the recommended way** to run the server, which ensures consistent dependencies and environment setup. However running manually is supported.

### Option 1: Docker

1. Pull the image
```Bash
docker pull aceandgaming/swarmtunesserver:latest
```

2. Create certs folder\
You will need to create a folder for `.pem` files and `credentials.json`

### Option 2: Copy from source

1. Fork the project

2. Clone the fork with `git`

    ```bash
    git clone https://github.com/{your-user}/swarmtunes-server.git
    cd swarmtunes-server
    ```

3. Install the project from `pyproject.toml`

    ```bash
    pip install -e .
    ```

4. Copy `credentials.json` and your **ssl keys** into `/secrets` 

## Running

### Docker

```bash
docker run -it --rm -p 8000:8000 \
  -v /path/to/secrets:/secrets \
  -e MAINTENANCE=false \
  aceandgaming/swarmtunesserver:latest
```
- Make sure to replace `path/to/secrets`
- Environment variables can be passed with -e or via an .env file
- The server will start automatically on port 8000

### Manually

This project uses [`uvicorn`](https://uvicorn.dev/) to run the server.

The basic command to run the server is:
```bash
bash dev.sh #runs the server under http
```
or

```bash
export CORS=false
uvicorn server:app --host 0.0.0.0 --port 8000 --reload --ssl-certfile="./secrets/cert.pem" --ssl-keyfile="./secrets/key.pem"
```

## Environment Variables

The server can be configured using environment variables. Below is a full list with descriptions and default values:

| Variable | Description | Default |
|---|---|---|
| `MAINTENANCE`                         | Enables automatic maintenance tasks (downloads, cleanup, album regeneration). First run may take 20–60 minutes to download initial data. | `false` |
| `CORS`                                | Enables CORS domain checks. Changing the allowed domain requires rebuilding. | `true` |
|---|---|---|
| `DATA_PATH`                           | Directory where the server stores data (songs, albums, playlists, etc.). | `data` |
| `SECRETS_PATH`                        | Directory for Google Drive API credentials and SSL keys. | `secrets` |
|---|---|---|
| `USER_MAX_PLAYLISTS`                  | Maximum number of playlists a user can create. | `30` |
| `USER_MIN_PASSWORD_LENGTH`            | Minimum required length for user passwords. | `8` |
| `USER_MAX_PASSWORD_LENGTH`            | Maximum allowed length for user passwords. | `128` |
| `TOKEN_EXPIRATION_DAYS`               | Validity of renewable login tokens in days. | `30` |
| `SESSION_EXPIRATION_HOU`              | Validity of non-renewable login sessions in hours. | `12` |
|---|---|---|
| `MAX_DELETED_FILES_SIZE`              | Maximum total size (bytes) of deleted files the server retains. | `2e8` |
|---|---|---|
| `MAX_MAINTENANCE_DOWNLOAD_PERCENT`    | Max percent of files maintenance can download relative to song count. | `1.0` |
| `MAX_MAINTENANCE_DELETE_PERCENT`      | Max percent of files maintenance can delete relative to song count. | `0.1` |
| `MAX_MAINTENANCE_REPLACE_PERCENT`     | Max percent of files maintenance can replace relative to song count. | `0.2` |
| `MAX_MAINTENANCE_REDOWNLOAD_PERCENT`  | Max percent of files maintenance can redownload relative to song count. | `0.4` |

## Pull Requests

After pushing changes to your fork, you can create a [Pull Request](https://github.com/AceandGaming/swarmtunes-server/pulls)
