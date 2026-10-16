import socket

from app import create_app

# Beanstalk (plataforma Python) busca la variable "application" en application.py
application = create_app()


@application.get("/deploy")
def deploy_info():
    return {
        "deploy": "rolling-additional-batch",
        "build": "v4-additional",
        "host": socket.gethostname(),
    }


if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=True)