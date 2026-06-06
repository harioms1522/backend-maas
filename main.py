import uvicorn

from app.app import app
from app.core.config import ENV


def main():
    if ENV == "DEVELOPMENT":
        uvicorn.run("app.app:app", host="127.0.0.1", port=8000, reload=True)
    else:
        # In production, we want to run 
        # gunicorn server with multiple uvicorn workers for better performance
        # gunicorn app.app:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
        raise RuntimeError("Production: Use a Gunicorn command instead of running this script.")

if __name__ == "__main__":
    main()
