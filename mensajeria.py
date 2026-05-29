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
    
def obtener_ip_local(ip_destino, port_destino):
    """
    Obtiene la IP local sin abrir una conexion TCP real.
    Se usa UDP porque connect() en UDP no envia datos, solo permite saber
    que IP local usaria el sistema para llegar al destino.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect((ip_destino, port_destino))
            return sock.getsockname()[0]
    except OSError:
        try:
            return socket.gethostbyname(socket.gethostname())
        except OSError:
            return "0.0.0.0"


def resolver_destino(destino):
    """
    Recibe una IP o nombre de host y devuelve una IP.
    Si no puede resolver, devuelve None.
    """
    try:
        return socket.gethostbyname(destino)
    except socket.gaierror:
        print(f"Error: no se pudo resolver el destino {destino}")
        return None


def enviar_mensaje_texto(destino, port_destino, usuario, mensaje):
    """
    Envia un mensaje de texto a un destino usando el protocolo definido:

    MSG <usuario> <ip_emisor> <largo_mensaje>\r\n
    [mensaje en bytes]
    """
    mensaje_bytes = mensaje.encode("utf-8")
    largo_mensaje = len(mensaje_bytes)

    if largo_mensaje > MAX_LARGO_MENSAJE:
        print("Error: el mensaje supera el largo maximo de 255 bytes")
        return

    ip_destino = resolver_destino(destino)
    if ip_destino is None:
        return

    ip_emisor = obtener_ip_local(ip_destino, port_destino)

    header = f"MSG {usuario} {ip_emisor} {largo_mensaje}\r\n"
    payload = header.encode("utf-8") + mensaje_bytes

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((ip_destino, port_destino))
            sock.sendall(payload)

    except ConnectionRefusedError:
        print(f"Error: conexion rechazada por {destino}:{port_destino}")
    except TimeoutError:
        print(f"Error: tiempo de conexion agotado con {destino}:{port_destino}")
    except OSError as e:
        print(f"Error enviando mensaje a {destino}: {e}")


def bucle_emisor(port_destino, usuario):
    """
    Lee lineas desde stdin con el formato:

    destino mensaje

    Ejemplos:
    192.168.33.15 Feliz Cumple!!!!!
    tecnoinf315.esi.edu.uy Feliz Cumple!!!!!
    tecnoinf315 Feliz Cumple!!!!!
    """
    while True:
        try:
            linea = input()

            if linea.strip() == "":
                continue

            partes = linea.split(" ", 1)

            if len(partes) != 2:
                print("Formato invalido. Use: destino mensaje")
                continue

            destino = partes[0].strip()
            mensaje = partes[1]

            if mensaje.strip() == "":
                print("Error: el mensaje no puede estar vacio")
                continue

            enviar_mensaje_texto(destino, port_destino, usuario, mensaje)

        except KeyboardInterrupt:
            print("CTRL + C Recibido.... Cerrando Sesion")
            sys.exit(0)
        except EOFError:
            sys.exit(0)

def main():
    if len(sys.argv) != 4:
        print("Uso: python mensajeria.py <port> <ipAuth> <portAuth>")
        sys.exit(1)

    port = int(sys.argv[1])
    ip_auth = sys.argv[2]
    port_auth = int(sys.argv[3])

    usuario = autenticar(ip_auth, port_auth)

    if usuario is None:
        print("Error: no se pudo autenticar el usuario")
        sys.exit(1)

    bucle_emisor(port, usuario)


if __name__ == "__main__":
    main()