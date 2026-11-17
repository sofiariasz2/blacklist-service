FROM public.ecr.aws/docker/library/python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY application.py .
COPY app ./app

RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# El agente de New Relic se configura con variables de entorno (NEW_RELIC_*).
# Sin NEW_RELIC_LICENSE_KEY la app arranca igual, solo no envía datos.
ENV NEW_RELIC_APP_NAME="blacklist-service" \
    NEW_RELIC_LOG=stdout \
    NEW_RELIC_LOG_LEVEL=info \
    NEW_RELIC_DISTRIBUTED_TRACING_ENABLED=true \
    NEW_RELIC_APPLICATION_LOGGING_FORWARDING_ENABLED=true

CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "application:application"]
