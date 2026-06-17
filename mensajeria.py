# Redes de Computadoras - Lab 1
# Integrantes:
# CI: 5.597.183-2 - Joaquin Pintos
# CI: 5.470.443-0 - Marcos Betancor
# CI: 5.363.039-9 - Gaston Groso
# CI: 5.453.743-7 - Santiago Bove

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
import signal
import socket
import sys
import threading


MAX_LARGO_MENSAJE = 255
_running = True

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

def _ts():
    """Timestamp: YYYY.MM.DD HH:MM"""
    return datetime.datetime.now().strftime("%Y.%m.%d %H:%M")

def handle_client(client_socket, client_addr):
    """Procesa una unica conexion entrante (MSG o FILE).
    Corre en un hilo separado por cada conexion."""
    try:
        header = recv_line(client_socket)
        if header is None:
            return

        partes = header.split()
        tipo   = partes[0] if partes else ""

        # ── MSG <usuario> <ip_emisor> <largo> ───────────────────────────────
        if tipo == "MSG" and len(partes) == 4:
            usuario   = partes[1]
            ip_emisor = partes[2]
            try:
                largo = int(partes[3])
            except ValueError:
                return

            if largo < 0 or largo > MAX_LARGO_MENSAJE:
                return

            data = recv_bytes(client_socket, largo)
            if data is None:
                return

            mensaje = data.decode("utf-8", errors="replace")
            # [2026.06.23 17:02] 192.168.33.15 nwirth dice: Feliz Cumple!!!!!
            print(f"[{_ts()}] {ip_emisor} {usuario} dice: {mensaje}", flush=True)

        # ── FILE <usuario> <ip_emisor> <nombre_archivo> <tamano> ────────────
        elif tipo == "FILE" and len(partes) == 5:
            usuario = partes[1]
            ip_emisor = partes[2]
            nombre_archivo = os.path.basename(partes[3])

            try:
                tamano = int(partes[4])
            except ValueError:
                print(f"[{_ts()}] {ip_emisor} <Error Recibiendo Archivo de {usuario}>", flush=True)
                return

            if tamano < 0 or nombre_archivo == "":
                print(f"[{_ts()}] {ip_emisor} <Error Recibiendo Archivo de {usuario}>", flush=True)
                return

            datos_archivo = recv_bytes(client_socket, tamano)

            ruta_salida = f"./{nombre_archivo}"

            if datos_archivo is None:
                print(f"[{_ts()}] {ip_emisor} <Error Recibiendo Archivo de {usuario}>", flush=True)
                return

            try:
                with open(ruta_salida, "wb") as archivo:
                    archivo.write(datos_archivo)

                print(f"[{_ts()}] {ip_emisor} <Recibido {ruta_salida} de {usuario}>", flush=True)

            except OSError:
                print(f"[{_ts()}] {ip_emisor} <Error Recibiendo Archivo de {usuario}>", flush=True)

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

def _procesar_udp(header_str, payload, ip_fuente):
    """Procesa un datagrama UDP de broadcast (mismo protocolo que TCP)."""
    partes = header_str.split()
    tipo   = partes[0] if partes else ""
 
    # ── MSG ────────────────────────────────────────────────────────────────
    if tipo == "MSG" and len(partes) == 4:
        usuario   = partes[1]
        ip_emisor = partes[2]
        try:
            largo = int(partes[3])
        except ValueError:
            return
        mensaje = payload[:largo].decode("utf-8", errors="replace")
        print(f"[{_ts()}] {ip_emisor} {usuario} dice: {mensaje}", flush=True)
 
    # ── FILE ───────────────────────────────────────────────────────────────
    elif tipo == "FILE" and len(partes) == 5:
        usuario        = partes[1]
        ip_emisor      = partes[2]
        nombre_archivo = os.path.basename(partes[3])
        try:
            tamano = int(partes[4])
        except ValueError:
            print(f"[{_ts()}] {ip_emisor} <Error Recibiendo Archivo de {usuario}>", flush=True)
            return
 
        datos = payload[:tamano]
        if len(datos) == tamano and nombre_archivo:
            try:
                with open(f"./{nombre_archivo}", "wb") as f:
                    f.write(datos)
                print(f"[{_ts()}] {ip_emisor} <Recibido ./{nombre_archivo} de {usuario}>", flush=True)
            except OSError:
                print(f"[{_ts()}] {ip_emisor} <Error Recibiendo Archivo de {usuario}>", flush=True)
        else:
            print(f"[{_ts()}] {ip_emisor} <Error Recibiendo Archivo de {usuario}>", flush=True)
 
 
def bucle_receptor_udp(port):
    """Escucha datagramas UDP de broadcast en 0.0.0.0:port."""
    try:
        srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        srv.bind(("0.0.0.0", port))
        srv.settimeout(1.0)
    except OSError as e:
        print(f"Error iniciando receptor UDP: {e}", flush=True)
        return

    while _running:
        try:
            data, addr = srv.recvfrom(65535)
            # Separar header (\r\n) 
            idx = data.find(b"\r\n")
            if idx == -1:
                continue
            try:
                header_str = data[:idx].decode("utf-8")
            except UnicodeDecodeError:
                continue
            payload = data[idx + 2:]
            _procesar_udp(header_str, payload, addr[0])
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

def obtener_broadcast():
    """
    Calcula la direccion de broadcast de la interfaz principal.
    Asume mascara /24 (la mas comun en labs). Si falla, usa 255.255.255.255.
    """
    try:
        ip_local = obtener_ip_local("8.8.8.8", 80)
        # Para /24: reemplazar ultimo octeto con 255
        return ip_local.rsplit(".", 1)[0] + ".255"
    except Exception:
        return "255.255.255.255"

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
    """Envia un archivo por TCP al destino indicado."""
    if not os.path.isfile(path_archivo):
        print(f"Error: el archivo {path_archivo} no existe")
        return
    
    try:
        with open(path_archivo, "rb") as f:
            datos = f.read()
    except OSError as e:
        print(f"Error leyendo el archivo {path_archivo}: {e}")
        return
    
    nombre_base = os.path.basename(path_archivo)
    tamano = len(datos)

    ip_destino = resolver_destino(destino)
    if ip_destino is None:
        return
    
    ip_emisor = obtener_ip_local(ip_destino, port_destino)
    header = f"FILE {usuario} {ip_emisor} {nombre_base} {tamano}\r\n".encode("utf-8")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((ip_destino, port_destino))
            s.sendall(header + datos)
    except ConnectionRefusedError:
        print(f"Error: conexion rechazada por {destino}:{port_destino}")
    except (socket.timeout, TimeoutError):
        print(f"Error: tiempo de conexion agotado con {destino}:{port_destino}")
    except OSError as e:
        print(f"Error enviando mensaje a {destino}: {e}")

def _enviar_udp_broadcast(port, payload_bytes):
    """Envia un datagrama UDP a la direccion de broadcast de la red local."""
    ip_bcast = obtener_broadcast()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(payload_bytes, (ip_bcast, port))
    except OSError as e:
        print(f"Error en broadcast: {e}")
 
 
def broadcast_mensaje(port, usuario, mensaje):
    """Envia un mensaje de texto a todos los hosts de la red via UDP broadcast."""
    mensaje_bytes = mensaje.encode("utf-8")
    largo = len(mensaje_bytes)
 
    if largo > MAX_LARGO_MENSAJE:
        print(f"Error: el mensaje supera el largo maximo de {MAX_LARGO_MENSAJE} bytes")
        return
 
    ip_emisor = obtener_ip_local("8.8.8.8", 80)
    header    = f"MSG {usuario} {ip_emisor} {largo}\r\n".encode("utf-8")
    _enviar_udp_broadcast(port, header + mensaje_bytes)
 
 
def broadcast_archivo(port, usuario, path_archivo):
    """Envia un archivo a todos los hosts de la red via UDP broadcast.
    Limitado al tamano maximo de un datagrama UDP (~65 KB)."""
    if not os.path.isfile(path_archivo):
        print(f"Error: no existe el archivo '{path_archivo}'")
        return
 
    try:
        with open(path_archivo, "rb") as f:
            datos = f.read()
    except OSError as e:
        print(f"Error leyendo archivo '{path_archivo}': {e}")
        return
 
    if len(datos) > 65000:
        print("Error: archivo demasiado grande para broadcast UDP (maximo ~65 KB)")
        return
 
    nombre_base = os.path.basename(path_archivo)
    tamano      = len(datos)
    ip_emisor   = obtener_ip_local("8.8.8.8", 80)
    header      = f"FILE {usuario} {ip_emisor} {nombre_base} {tamano}\r\n".encode("utf-8")
    _enviar_udp_broadcast(port, header + datos)


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
                print("Formato invalido. Use: destino mensaje  o  destino &file path")
                continue
 
            destino  = partes[0].strip()
            contenido = partes[1]
 
            # Detectar si es envio de archivo
            es_archivo = contenido.startswith("&file ")
            if es_archivo:
                path = contenido[6:].strip()
                if not path:
                    print("Error: especifica el path del archivo")
                    continue
            else:
                mensaje = contenido
                if not mensaje.strip():
                    print("Error: el mensaje no puede estar vacio")
                    continue
 
            # Despachar segun destino
            if destino == "*":
                if es_archivo:
                    broadcast_archivo(port_destino, usuario, path)
                else:
                    broadcast_mensaje(port_destino, usuario, mensaje)
            else:
                if es_archivo:
                    enviar_archivo(destino, port_destino, usuario, path)
                else:
                    enviar_mensaje_texto(destino, port_destino, usuario, mensaje)
 
        except KeyboardInterrupt:
            # La senal SIGINT ya fue registrada — simplemente ignorar aqui
            pass
        except EOFError:
            sys.exit(0)

# MODULO E — SENALES Y CIERRE LIMPIO

def _cerrar(sig, frame):
    """Manejador de SIGINT y SIGTERM. Imprime el mensaje del enunciado y sale."""
    global _running
    _running = False
    print("\nCTRL + C Recibido.... Cerrando Sesion", flush=True)
    sys.exit(0)

# MAIN

def main():
    if len(sys.argv) != 4:
        print("Uso: python mensajeria.py <port> <ipAuth> <portAuth>")
        sys.exit(1)

    port = int(sys.argv[1])
    ip_auth = sys.argv[2]
    port_auth = int(sys.argv[3])

    # Registrar senales antes de arrancar hilos
    signal.signal(signal.SIGINT,  _cerrar)
    signal.signal(signal.SIGTERM, _cerrar)

    usuario = autenticar(ip_auth, port_auth)

    if usuario is None:
        print("Error: no se pudo autenticar el usuario")
        sys.exit(1)

    # Receptor TCP (unicast) en hilo separado
    hilo_tcp = threading.Thread(target=bucle_receptor, args=(port,), daemon=True)
    hilo_tcp.start()
 
    # Receptor UDP (broadcast) en hilo separado
    hilo_udp = threading.Thread(target=bucle_receptor_udp, args=(port,), daemon=True)
    hilo_udp.start()
 
    # Emisor en el hilo principal (bloquea en input())
    bucle_emisor(port, usuario)
 
 
if __name__ == "__main__":
    main()