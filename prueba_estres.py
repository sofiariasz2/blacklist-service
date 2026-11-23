import random
import threading
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone

import requests

DIRECCION_BASE = "http://blacklist-alb-1914931237.us-east-1.elb.amazonaws.com"
TOKEN_ACCESO = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc5NTM5ODEzMywianRpIjoiM2YzN2ViNDAtZTM2Yi00NjMwLTg1MGMtNTBlN2YyYzk0YTFiIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImJsYWNrbGlzdC1jbGllbnQiLCJuYmYiOjE3OTUzOTgxMzN9.IrZGkhSM5OZZAwlamvgeY8WnxUClY9bJ7RMGT9Wd8QM"
CANTIDAD_HILOS = 20
DURACION_SEGUNDOS = 300
IDENTIFICADOR_APLICACION = "123e4567-e89b-12d3-a456-426614174000"
CORREO_DUPLICADO = "duplicado_prueba_estres@ejemplo.com"

cerrojo_resultados = threading.Lock()
cantidad_por_codigo_estado = defaultdict(int)
suma_tiempos_por_codigo_estado = defaultdict(float)
correos_creados = []


def registrar_resultado(codigo_estado, segundos_transcurridos):
    # Guardar el resultado de la petición de forma segura entre hilos
    with cerrojo_resultados:
        cantidad_por_codigo_estado[codigo_estado] += 1
        suma_tiempos_por_codigo_estado[codigo_estado] += segundos_transcurridos


def enviar_peticion(sesion, metodo, ruta, cuerpo=None, con_token=True):
    # Construir las cabeceras de la petición
    cabeceras = {}
    if con_token:
        cabeceras["Authorization"] = f"Bearer {TOKEN_ACCESO}"

    # Medir el tiempo de respuesta desde el cliente
    instante_inicial = time.time()
    try:
        respuesta = sesion.request(
            metodo, DIRECCION_BASE + ruta, json=cuerpo, headers=cabeceras, timeout=30
        )
        codigo_estado = respuesta.status_code
    except requests.RequestException:
        codigo_estado = "error_de_conexion"
    registrar_resultado(codigo_estado, time.time() - instante_inicial)


def ejecutar_hilo(instante_final):
    sesion = requests.Session()

    while time.time() < instante_final:
        sorteo = random.random()

        if sorteo < 0.40:
            # Crear un correo nuevo en la lista negra (201)
            correo_nuevo = f"{uuid.uuid4().hex[:12]}@ejemplo.com"
            enviar_peticion(sesion, "POST", "/blacklists", {
                "email": correo_nuevo,
                "app_uuid": IDENTIFICADOR_APLICACION,
                "blocked_reason": "Prueba de estres",
            })
            with cerrojo_resultados:
                correos_creados.append(correo_nuevo)

        elif sorteo < 0.75:
            # Consultar un correo, creado o inexistente (200)
            with cerrojo_resultados:
                hay_correos = len(correos_creados) > 0
                correo_consultado = random.choice(correos_creados) if hay_correos else CORREO_DUPLICADO
            if random.random() < 0.3:
                correo_consultado = f"{uuid.uuid4().hex[:12]}@limpio.com"
            enviar_peticion(sesion, "GET", f"/blacklists/{correo_consultado}")

        elif sorteo < 0.85:
            # Enviar un identificador de aplicación inválido (400)
            enviar_peticion(sesion, "POST", "/blacklists", {
                "email": f"{uuid.uuid4().hex[:12]}@ejemplo.com",
                "app_uuid": "identificador-invalido",
            })

        elif sorteo < 0.95:
            # Enviar una petición sin token de autorización (401)
            enviar_peticion(sesion, "POST", "/blacklists", {
                "email": "sin_token@ejemplo.com",
                "app_uuid": IDENTIFICADOR_APLICACION,
            }, con_token=False)

        else:
            # Repetir un correo ya registrado (409)
            enviar_peticion(sesion, "POST", "/blacklists", {
                "email": CORREO_DUPLICADO,
                "app_uuid": IDENTIFICADOR_APLICACION,
            })


def main():
    # Crear el correo que luego se repetirá para provocar el código 409
    sesion_inicial = requests.Session()
    enviar_peticion(sesion_inicial, "POST", "/blacklists", {
        "email": CORREO_DUPLICADO,
        "app_uuid": IDENTIFICADOR_APLICACION,
    })

    instante_inicio = datetime.now(timezone.utc)
    print(f"Inicio en UTC {instante_inicio.strftime('%H:%M:%S')}")

    instante_final = time.time() + DURACION_SEGUNDOS
    hilos = [
        threading.Thread(target=ejecutar_hilo, args=(instante_final,))
        for _ in range(CANTIDAD_HILOS)
    ]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    instante_fin = datetime.now(timezone.utc)
    print(f"Fin en UTC {instante_fin.strftime('%H:%M:%S')}")

    # Mostrar el resumen de resultados por código de estado
    for codigo_estado, cantidad in sorted(cantidad_por_codigo_estado.items(), key=str):
        promedio_milisegundos = suma_tiempos_por_codigo_estado[codigo_estado] / cantidad * 1000
        print(f"Código {codigo_estado} peticiones {cantidad} promedio {promedio_milisegundos:.0f} ms")


if __name__ == "__main__":
    main()