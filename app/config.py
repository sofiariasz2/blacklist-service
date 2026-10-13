import os


def _database_url():
    """Prioridad: DATABASE_URL > variables RDS_* (Beanstalk con RDS adjunto) > SQLite local."""
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    if os.getenv("RDS_HOSTNAME"):
        return (
            f"postgresql://{os.environ['RDS_USERNAME']}:{os.environ['RDS_PASSWORD']}"
            f"@{os.environ['RDS_HOSTNAME']}:{os.getenv('RDS_PORT', '5432')}"
            f"/{os.getenv('RDS_DB_NAME', 'postgres')}"
        )
    return "sqlite:///local.db"


class Config:
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-local-cambiar-en-aws-por-una-clave-larga")
    # El token es estático (permitido por el enunciado): no expira
    JWT_ACCESS_TOKEN_EXPIRES = False
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
