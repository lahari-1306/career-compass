import os
from waitress import serve
from app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Serving CareerCompass on 0.0.0.0:{port} with Waitress production server")
    print(f"Local URL: http://127.0.0.1:{port}")
    print(f"Network URL: http://192.168.1.9:{port}")
    serve(app, host="0.0.0.0", port=port, threads=6)
