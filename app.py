import os
from flask import Flask
from routes.web import web
from config.database import Base, engine
from flask_cors import CORS

app = Flask(__name__)

# Aktifkan CORS (dapat dikonfigurasi via env CORS_ORIGINS)
# Gunakan '*' untuk semua origin, atau daftar origin dipisah koma.
origins_env = os.environ.get("CORS_ORIGINS", "*")
if origins_env.strip() == "*":
    allowed_origins = "*"
else:
    allowed_origins = [o.strip() for o in origins_env.split(",") if o.strip()]

CORS(
    app,
    resources={
        r"/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "Accept",
                "Origin",
                "Cache-Control",
                "Pragma",
            ],
            "expose_headers": [
                "Content-Type",
                "Authorization",
            ],
        }
    },
    supports_credentials=False,
    send_wildcard=(allowed_origins == "*"),
    max_age=86400,
)

# Buat tabel otomatis jika belum ada
Base.metadata.create_all(bind=engine)

# Daftarkan blueprint
app.register_blueprint(web)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    
    # WAJIB pakai 0.0.0.0 agar Railway bisa mengakses aplikasi
    app.run(host="0.0.0.0", port=port)
