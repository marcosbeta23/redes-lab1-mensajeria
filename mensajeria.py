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

import datetime
import getpass
import hashlib
import os
import socket
import sys
import threading


MAX_LARGO_MENSAJE = 255

# Protocolo (TCP), formato de los mensajes que mandamos y recibimos:
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

# FUNCIONES DE LECTURA

def recv_line(sock):
    """Lee bytes hasta \\r\\n. Devuelve la linea sin terminador (str) o None."""
    data = bytearray()
    while True:
        chunk = sock.recv(1)
        if not chunk:
            return None if not data else data.decode(errors="replace").rstrip("\r\n")
        data += chunk
        if data.endswith(b"\r\n"):
            return data[:-2].decode(errors="replace")

def recv_bytes(sock, n):
    """Lee exactamente n bytes. Devuelve None si la conexion se cierra antes."""
    data = bytearray()
    while len(data) < n:
        chunk = sock.recv(min(4096, n - len(data)))
        if not chunk:
            return None
        data += chunk
    return bytes(data)

# MODULO A — AUTENTICACION

def autenticar(ip_auth, port_auth):
    """Se conecta al servidor de autenticacion, pide usuario y clave,
    y devuelve el nombre de usuario si la autenticacion fue correcta.
    Si algo falla, devuelve None."""
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

# MODULO B — RECEPTOR

def handle_client(client_socket, client_addr):
    """Procesa una unica conexion entrante (MSG o FILE).
    Corre en un hilo separado por cada conexion."""
    try:
        header = recv_line(client_socket)
        if header is None:
            return

        partes = header.split()
        tipo   = partes[0] if partes else ""
        ts     = datetime.datetime.now().strftime("%Y.%m.%d %H:%M")

        # ── MSG <usuario> <ip_emisor> <largo> ───────────────────────────────
        if tipo == "MSG" and len(partes) == 4:
            usuario   = partes[1]
            ip_emisor = partes[2]
            try:
                largo = int(partes[3])
            except ValueError:
                return

            data = recv_bytes(client_socket, largo)
            if data is None:
                return

            mensaje = data.decode("utf-8", errors="replace")
            # [2026.06.23 17:02] 192.168.33.15 nwirth dice: Feliz Cumple!!!!!
            print(f"[{ts}] {ip_emisor} {usuario} dice: {mensaje}", flush=True)

        # ── FILE <usuario> <ip_emisor> <nombre_archivo> <tamano> ────────────
        elif tipo == "FILE" and len(partes) == 5:
            # TODO: implementar recepcion de archivos
            pass

        # Si el tipo no es MSG ni FILE, ignoramos la conexion

    except OSError:
        pass  # conexion cortada abruptamente — no crashear
    finally:
        try:
            client_socket.close()
        except OSError:
            pass

def bucle_receptor(port):
    """Escucha en 0.0.0.0:port y despacha cada conexion en un hilo separado.
    El timeout de 1s en accept() permite chequear _running sin bloquearse."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", port))
    srv.listen(10)
    srv.settimeout(1.0)

    while _running:
        try:
            client_sock, client_addr = srv.accept()
            threading.Thread(
                target=handle_client,
                args=(client_sock, client_addr),
                daemon=True
            ).start()
        except socket.timeout:
            continue
        except OSError:
            break

    try:
        srv.close()
    except OSError:
        pass

# MODULO C — EMISOR

def obtener_ip_local(ip_destino, port_destino):
    """Averigua cual es nuestra IP local para llegar al destino.
    Usamos un socket UDP porque no manda datos, solo nos dice que IP usaria."""
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
    """Convierte un nombre de host o IP en una IP numerica.
    Si no puede resolverlo, avisa y devuelve None."""
    try:
        return socket.gethostbyname(destino)
    except socket.gaierror:
        print(f"Error: no se pudo resolver el destino {destino}")
        return None

def enviar_mensaje_texto(destino, port_destino, usuario, mensaje):
    """Manda un mensaje de texto al destino indicado."""
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

def enviar_archivo(destino, port_destino, usuario, path_archivo):
    # TODO: implementar envio de archivos
    pass

def bucle_emisor(port_destino, usuario):
    """Lee lo que escribe el usuario y lo manda al destino.
    El formato de entrada es:
        destino mensaje
        destino &file path/archivo
        * mensaje          (manda a todos)
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
            # TODO (modulo E - senales): el manejador de senal se tiene que ocupar de esto
            pass
        except EOFError:
            sys.exit(0)

# MODULO E — SENALES Y CIERRE LIMPIO
# TODO (modulo E): implementar manejador de senales

# MAIN

def main():
    if len(sys.argv) != 4:
        print("Uso: python mensajeria.py <port> <ipAuth> <portAuth>")
        sys.exit(1)

    port = int(sys.argv[1])
    ip_auth = sys.argv[2]
    port_auth = int(sys.argv[3])

    # TODO (modulo E): registrar signal.signal(SIGINT) y signal.signal(SIGTERM)

    usuario = autenticar(ip_auth, port_auth)

    if usuario is None:
        print("Error: no se pudo autenticar el usuario")
        sys.exit(1)

    # Receptor en hilo separado
    hilo_rx = threading.Thread(target=bucle_receptor, args=(port,), daemon=True)
    hilo_rx.start()

    # Emisor en hilo principal
    bucle_emisor(port, usuario)


if __name__ == "__main__":
    main()