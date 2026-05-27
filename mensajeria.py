# Redes de Computadoras - Lab 1
# Integrantes:
# CI: X.XXX.XXX-X - Nombre Apellido
# CI: X.XXX.XXX-X - Nombre Apellido
# CI: X.XXX.XXX-X - Nombre Apellido
# CI: X.XXX.XXX-X - Nombre Apellido

"""
mensajeria.py - Aplicacion de mensajeria con sockets TCP

Uso: python mensajeria.py <port> <ipAuth> <portAuth>

Este archivo es el punto de entrada. La logica se distribuira
en este archivo unico siguiendo los modulos:
  - Autenticacion (modulo A)
  - Receptor (modulo B)
  - Emisor (modulo C)
  - Manejo de senales (modulo E)
"""

MAX_LARGO_MENSAJE = 255

# Protocolo de payload (TCP). Cabecera ASCII con CRLF, campos separados por espacio.
# MSG <usuario> <ip_emisor> <largo_mensaje>\r\n
#   - largo_mensaje: entero decimal, cantidad de bytes del payload de texto (UTF-8).
#   - payload: exactamente largo_mensaje bytes. El fin del mensaje se determina por el largo.
#   - limite 255: el emisor NO envia MSG con largo_mensaje > 255; el receptor debe rechazar/ignorar y reportar error.
# FILE <usuario> <ip_emisor> <nombre_archivo> <tamano_bytes>\r\n
#   - tamano_bytes: entero decimal, cantidad de bytes del archivo.
#   - payload: exactamente tamano_bytes bytes (binario). No aplica limite 255.
#   - el fin del archivo se determina por tamano_bytes. No hay delimitador extra.
#
# El siguiente mensaje comienza inmediatamente despues del payload anterior.

# TODO: implementar
