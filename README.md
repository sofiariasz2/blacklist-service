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

## Monitoreo con New Relic

El agente de Python (`newrelic`) se inicializa en `application.py` y se configura solo con variables de entorno, sin `newrelic.ini`. Sin `NEW_RELIC_LICENSE_KEY` el agente no se activa y la app funciona igual.

| Variable | Valor |
|---|---|
| `NEW_RELIC_LICENSE_KEY` | Licencia de ingesta de la cuenta (secreta). En Fargate sale de Parameter Store: `/blacklist-service/NEW_RELIC_LICENSE_KEY`. |
| `NEW_RELIC_APP_NAME` | `blacklist-service` (ya viene en el Dockerfile). |

Ambiente de desarrollo, sin Docker:

```bash
export NEW_RELIC_LICENSE_KEY=<licencia>
export NEW_RELIC_APP_NAME=blacklist-service-local
python application.py            # o: gunicorn --bind :8000 application:application
```

Con Docker:

```bash
docker build -t blacklist-service .
docker run --rm -p 8000:8000 -e JWT_SECRET_KEY=dev \
  -e NEW_RELIC_LICENSE_KEY=<licencia> -e NEW_RELIC_APP_NAME=blacklist-service-local \
  blacklist-service
```

En el log debe aparecer `New Relic Python Agent (14.x)` y, tras unas peticiones, la app aparece en New Relic → APM & Services en uno o dos minutos.

## Desplegar en Beanstalk (manual)

Comprimir el **contenido** de la carpeta (no la carpeta) sin `.venv`:

```bash
zip -r app.zip . -x ".venv/*" "*.db" "__pycache__/*" ".git/*"
```

Subir el zip en la consola de Beanstalk (plataforma Python). Health check path: `/ping`.
