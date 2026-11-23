import os

# New Relic se inicializa antes de importar Flask para que pueda instrumentarlo.
# Se configura con variables NEW_RELIC_*; sin licencia no se activa.
if os.environ.get("NEW_RELIC_LICENSE_KEY"):
    import newrelic.agent

    newrelic.agent.initialize()

from app import create_app  # noqa: E402

# Beanstalk (plataforma Python) busca la variable "application" en application.py
application = create_app()

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=True)
