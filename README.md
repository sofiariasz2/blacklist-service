# Blacklist Service — Entrega 1 DevOps

Microservicio Flask para gestionar la lista negra global de emails.

## Endpoints

| Método | Ruta | Auth | Respuesta |
|---|---|---|---|
| POST | `/blacklists` | Bearer | `201` agregado · `400` datos inválidos · `409` ya existe · `401` sin token |
| GET | `/blacklists/<email>` | Bearer | `200` `{"is_blacklisted": bool, "blocked_reason": str\|null}` |
| GET | `/ping` (y `/`) | No | `200` `{"status": "ok", "version": "..."}` — health check |

Body del POST:

```json
{
  "email": "cliente@correo.com",
  "app_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "blocked_reason": "Solicitó no recibir más correos"
}
```

Internamente se guardan también la IP de origen (`X-Forwarded-For` detrás del balanceador) y la fecha/hora.

## Correr localmente

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python application.py            # usa SQLite local si no hay DATABASE_URL
python generate_token.py         # imprime el token Bearer
python -m pytest -q              # pruebas
```

## Variables de entorno (configurar en Beanstalk)

| Variable | Para qué |
|---|---|
| `DATABASE_URL` | `postgresql://usuario:clave@endpoint-rds:5432/nombre_bd` |
| `JWT_SECRET_KEY` | Clave para firmar el token. **Igual** a la usada al generar el token. |
| `APP_VERSION` | Cámbienla en cada despliegue para validar las estrategias vía `/ping`. |

Si el RDS se crea adjunto al entorno de Beanstalk, la app también lee `RDS_HOSTNAME`, `RDS_USERNAME`, etc. automáticamente.

## Desplegar en Beanstalk (manual)

Comprimir el **contenido** de la carpeta (no la carpeta) sin `.venv`:

```bash
zip -r app.zip . -x ".venv/*" "*.db" "__pycache__/*" ".git/*"
```

Subir el zip en la consola de Beanstalk (plataforma Python). Health check path: `/ping`.
