import os
import psycopg2
from flask import Flask
from dotenv import load_dotenv
from .models import db, Base, migrate
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text


def create_postgres_db_if_not_exists(db_name, user, password, host=os.getenv("HOST"), port=os.getenv("PORT")): # host="dpg-d11it5ffte5s7399ff3g-a", port=5432)
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(dbname='postgres', user=user, password=password, host=host, port=port)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cur = conn.cursor()
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
        exists = cur.fetchone()

        if not exists:
            cur.execute(f"CREATE DATABASE {db_name};")
            print(f"✅ Database '{db_name}' created.")
        else:
            print(f"⚠️ Database '{db_name}' already exists.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Failed to create database: {e}")


engine = create_engine(os.getenv("DATABASE_URL"))  # Replace with your actual URL

def reset_database():
    with engine.connect() as conn:
        trans = conn.begin()

        try:
            # Get all table names (except protected ones)
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename NOT IN ('your_core_table1', 'your_core_table2')
            """))
            tables = [row[0] for row in result]

            for table in tables:
                conn.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE;'))

            trans.commit()
        except Exception as e:
            trans.rollback()
            raise e

    # Recreate any missing tables
    Base.metadata.create_all(engine)


def create_app():
    load_dotenv()
    create_postgres_db_if_not_exists(os.getenv("DBNAME"), os.getenv("DB_USER"), os.getenv("DB_PASSWORD")) #("ivyleague", "render", "vUrYJ2HGlN7pu3kohoaNfglsujbNb1OW")
    # reset_database()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("FLASK_APP_SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # db.drop_all() # For development purposes
        db.create_all()

    # Import and register routes
    from app.routes import register_routes
    register_routes(app)

    from flask_cors import CORS

    CORS(app, resources={r"/api/*": {
        "origins": ["http://localhost:5173", "https://bear-deciding-wren.ngrok-free.app", "https://studentportal.ivyleaguenigeria.com"],  # Or specify your frontend domain
        "methods": ["GET", "POST", "OPTIONS", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization", "ngrok-skip-browser-warning"],
        "supports_credentials": True
    }})  # Use specific origin instead of "*" in production


    return app
