# Contributing

Swarmtunes is open to contributions! The following guide will help you set up and run the server locally.

## Requirements

1. Google API is required to automatically download songs. Here is one way to get a key:

    1. Go to console.cloud.google.com and create a new project

    2. Go to APIs & Services

    3. Enable -> Google Drive API and Youtube

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

3. You will need to download your own artwork for the songs. These images can be found from varius locations
    - [Neuro and Evil Covers](https://images.swarmtunes.com)
    - [Disc Covers](https://drive.google.com/drive/folders/1Pr53j8IHp_hJTLafCellHFz4kUiTzuUy)
    
    **Note**: *The above links and assets are the property of their respective copyright holders (`All rights reserved`)*

## Setup

For *most users*, **Docker is the recommended way** to run the server, which ensures consistent dependencies and environment setup. However running manually is supported for development.

### Option 1: Docker

1. Pull the image

    ```bash
    docker pull aceandgaming/swarmtunesserver:latest
    ```

2. Create certs folder\
You will need to create a folder for `.pem` files and `credentials.json`. Add this to the docker container as a folder called `secrets`

### Option 2: Copy from source

1. Fork the project

2. Clone the fork with `git`

    ```bash
    git clone https://github.com/{your-user}/swarmtunes-server.git
    cd swarmtunes-server
    ```

3. Install the project from `pyproject.toml`

    ```bash
    cd app
    pip install -e .
    ```

4. Copy `credentials.json` and your **ssl keys** into `/secrets` 

5. Copy or rename the *example configs* in `/config`

    `.env.example` -> `.env`


## Running

### Docker

```bash
docker run -it -p 8000:8000 \
  -v /path/to/secrets:/secrets \
  aceandgaming/swarmtunesserver:2.0
```
- Make sure to replace `path/to/secrets`
- Environment variables can be passed with -e or via an .env file
- The server will start automatically on port 8000

### Shell

This project uses [`uvicorn`](https://uvicorn.dev/) to run the server.

The basic command to run the server is:
```bash
bash tools/http.sh
```
or
```bash
bash tools/https.sh
```

You may also run the server manually
```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --ssl-certfile="../secrets/cert.pem" --ssl-keyfile="../secrets/key.pem"
```
## Config

There are many configs you can change in the server. The main one is `.env` for which the options are documented in the file.

## Pull Requests

After pushing changes to your fork, you can create a [Pull Request](https://github.com/AceandGaming/swarmtunes-server/pulls)
