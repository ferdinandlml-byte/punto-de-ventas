from app.db import init_db, seed_sample_data

if __name__ == "__main__":
    init_db()
    seed_sample_data()
    print("Datos de ejemplo cargados.")
