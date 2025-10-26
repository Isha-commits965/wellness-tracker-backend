import os
import uvicorn
import multiprocessing

# Get environment variables
PORT = int(os.getenv("PORT", 8000))
WEB_CONCURRENCY = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

if __name__ == "__main__":
    if DEBUG:
        # For local development with auto-reloading
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=PORT,
            reload=True,
            log_level="info"
        )
    else:
        # For production with Gunicorn
        os.system(f"gunicorn app.main:app --workers {WEB_CONCURRENCY} --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:{PORT}")