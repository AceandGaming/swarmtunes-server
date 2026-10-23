# Swarmtunes Server Setup

This guide explains how to configure and run the Swarmtunes server using Docker or a local development environment.

## Optional Requirements

### 1. Google API Credentials

Google API credentials are required for automatically downloading songs.

1. Open the [Google Cloud Console](https://console.cloud.google.com/) and create a project.
2. Navigate to **APIs & Services** and enable the required APIs:
   - Google Drive API
   - YouTube API
3. Configure the OAuth consent screen:
   - Set the audience to **External**.
   - Add your Google account under **Test users**.
4. Navigate to **Credentials** and create an **OAuth client ID** with the application type **Desktop app**.
5. Download the credentials JSON file and save it as `credentials.json`.

Keep your credentials private. Do not commit them to Git.

### 2. HTTPS Certificates

HTTPS certificates are required when running the server directly over HTTPS for cross-origin connections. You will need a certificate (`cert.pem`) and a private key (`key.pem`).

Choose one of the following methods.

**Using [mkcert](https://github.com/FiloSottile/mkcert)**

```bash
mkcert -install
mkcert -key-file key.pem -cert-file cert.pem localhost.com
```

Use a hostname that matches the address your client will connect to. For local development, this may be `localhost` or another locally configured hostname.

**Using OpenSSL**

```bash
openssl req -new -newkey rsa:4096 -x509 -sha256 \
  -days 365 -nodes \
  -out cert.pem -keyout key.pem
```

These certificates are suitable for development and testing. Production deployments should use appropriately trusted certificates.

### 3. Song Artwork

You may need to download artwork for songs separately. Artwork is available from the following sources:

- [Neuro and Evil covers](https://images.swarmtunes.com)
- [Disc covers](https://drive.google.com/drive/folders/1Pr53j8IHp_hJTLafCellHFz4kUiTzuUy)

**Copyright notice:** These links and assets are not managed by Swarmtunes. Artwork remains the property of its respective copyright holders and is subject to their rights.

## Installation

For self hosting, **Docker is recommended for most users**. 

For development, **running from source is recommended**.

### Option 1: Docker

> **Note:** The Docker setup uses HTTP. For HTTPS, use a reverse proxy such as Nginx.

#### Step 1: Pull the image

```bash
docker pull aceandgaming/swarmtunesserver:v2
```

#### Step 2: Prepare configuration and secrets

Create local directories for the files the server needs:

- `secrets/` — Google credentials and any required SSL certificates and keys.
- `config/` — server configuration files.
- `backups/` — optional database backups.
- `logs/` — optional log files.

The directories you mount must contain the files expected by the server. Copy and configure the appropriate example configuration files before starting the container.

#### Step 3: Start the container

```bash
docker run -it \
  -p 8000:8000 \
  -v /path/to/secrets:/secrets \
  -v /path/to/config:/config \
  aceandgaming/swarmtunesserver:v2
```

Replace `/path/to/secrets` and `/path/to/config` with the actual paths on your machine.

You can also pass environment variables using `-e` or an environment file:

```bash
docker run -it \
  -p 8000:8000 \
  --env-file /path/to/.env \
  -v /path/to/secrets:/secrets \
  -v /path/to/config:/config \
  aceandgaming/swarmtunesserver:v2
```

The server starts on port `8000`. The example publishes that port on your host, so adjust the mapping if necessary.

### Option 2: Run from Source

#### Step 1: Clone the repository

Clone the repository you want to work with:

```bash
git clone https://github.com/AceandGaming/swarmtunes.git
cd swarmtunes-server
```

If you are working from a fork, replace the URL with your fork's URL.

#### Step 2: Install dependencies

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if you haven't already, then run:

```bash
uv sync
```

This creates or synchronizes the project's virtual environment and installs its dependencies.

#### Step 3: Configure secrets and settings (If using Google API)

1. Place `credentials.json` and any required SSL certificates and keys in the secrets directory expected by the server.
2. Copy the example configuration files and rename them as needed. For example:

   ```bash
   cp config/.env.example config/.env
   ```

3. Edit the configuration files to match your environment.

#### Step 4: Start the server

For HTTP:

```bash
uv run st
```

For HTTPS:

```bash
uv run st --https
```

The HTTPS option requires the certificates and keys to be configured in `/secrets`

---

## Configuration

The server supports several configuration options. The primary settings are defined through its `.env` configuration file; consult the example configuration for available options and their descriptions.

Depending on the deployment, you may also need to configure Google credentials, SSL certificates, database settings, and logging.

### Docker runtime parameters

The Docker container supports the following parameters:

| Parameter | Description |
|---|---|
| `migrate` | Runs Alembic database migrations without starting the server. |
| `stamp <revision>` | Stamps the database with the specified Alembic revision. |
| `debug` | Starts the container without running its normal startup process. |
| *(none)* | Runs database migrations and starts the FastAPI server. |
