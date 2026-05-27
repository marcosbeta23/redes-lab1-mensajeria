# Redes de Computadoras - Lab 1
# Integrantes:
# CI: X.XXX.XXX-X - Nombre Apellido
# CI: X.XXX.XXX-X - Nombre Apellido
# CI: X.XXX.XXX-X - Nombre Apellido
# CI: X.XXX.XXX-X - Nombre Apellido

"""
mensajeria.py - Aplicacion de mensajeria con sockets TCP

Uso: python mensajeria.py <port> <ipAuth> <portAuth>

La logica se distribuira
en este archivo unico siguiendo los modulos:
  - Autenticacion (modulo A)
  - Receptor (modulo B)
  - Emisor (modulo C)
  - Manejo de senales (modulo E)
"""

import getpass
import hashlib
import socket
import sys

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

def recv_line(sock):
    data = bytearray()
    while True:
        chunk = sock.recv(1)
        if not chunk:
            return None if not data else data.decode(errors="replace").rstrip("\r\n")
        data += chunk
        if data.endswith(b"\r\n"):
            return data[:-2].decode(errors="replace")


def autenticar(ip_auth, port_auth):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip_auth, port_auth))

        saludo = recv_line(sock)
        if saludo is None:
            return None

        usuario = input("Usuario: ")
        clave = getpass.getpass("Clave: ")
        clave_md5 = hashlib.md5(clave.encode()).hexdigest()
        credenciales = f"{usuario}-{clave_md5}\r\n".encode()
        sock.sendall(credenciales)

        respuesta = recv_line(sock)
        if respuesta is None:
            return None

        if respuesta == "SI":
            nombre = recv_line(sock)
            if nombre is None:
                return None
            print(f"Bienvenido {nombre}")
            return usuario

        if respuesta == "NO":
            return None

        return None


def main():
    if len(sys.argv) != 4:
        print("Uso: python mensajeria.py <port> <ipAuth> <portAuth>")
        sys.exit(1)

    _port = int(sys.argv[1])
    ip_auth = sys.argv[2]
    port_auth = int(sys.argv[3])

    if autenticar(ip_auth, port_auth) is None:
        sys.exit(1)


if __name__ == "__main__":
    main()
