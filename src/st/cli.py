import sys

import uvicorn


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--https":
        uvicorn.run(
            "st.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            ssl_keyfile="secrets/key.pem",
            ssl_certfile="secrets/cert.pem",
        )
    else:
        uvicorn.run("st.main:app", host="0.0.0.0", port=8000, reload=True)
