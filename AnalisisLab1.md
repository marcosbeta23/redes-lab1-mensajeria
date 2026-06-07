# Análisis — Lab 1

---

## 1. Resumen del Laboratorio

Hay que implementar `mensajeria.py`, una aplicación Python de mensajería **peer-to-peer** que:
- Se autentica contra un servidor externo (`redes-auth`)
- Recibe mensajes y archivos en todo momento (proceso/hilo receptor)
- Envía mensajes y archivos a otros peers (proceso/hilo emisor)
- Soporta broadcast (`*`)
- Maneja señales del sistema correctamente
- Libera recursos al cerrar

---

## 2. Qué Pide Exactamente

### Entregables obligatorios
| Archivo | Contenido |
|---|---|
| `mensajeria.py` | Solución completa + comentario con CI y nombres |
| `comentarios.txt` | Observaciones, errores conocidos, decisiones de diseño |
| `redes-lab.tar.gz` | Comprimido con ambos archivos |

### Formato de invocación
```
python mensajeria.py port ipAuth portAuth
```

### Restricciones críticas
- `MAX_LARGO_MENSAJE = 255`
- Los fines de línea del servidor auth son `\r\n`
- El formato de salida **debe coincidir exactamente** con los ejemplos
- Cierre limpio ante `SIGINT`, `SIGTERM`, `SIGKILL`
- Fecha de entrega: **domingo 7 de junio a las 23:59 UYT**
- Grupos de hasta 4 personas (inscripción antes del 18 de mayo)

---

## 3. Partes en las que Conviene Dividirlo

```
┌─────────────────────────────────────────────────────────────┐
│                      mensajeria.py                          │
│                                                             │
│  [A] Autenticación  ──────────────────────────────────────  │
│       └── Conectar a redes-auth por TCP                     │
│       └── Intercambiar usuario/clave en MD5                 │
│       └── Obtener nombre completo                           │
│                                                             │
│  [B] Receptor (hilo/fork)  ───────────────────────────────  │
│       └── Escuchar en `port` por TCP                        │
│       └── Recibir mensajes → imprimir con formato           │
│       └── Recibir archivos → guardar en FS                  │
│                                                             │
│  [C] Emisor (hilo/fork)  ─────────────────────────────────  │
│       └── Leer stdin                                        │
│       └── Resolver hostname → IP si es nombre               │
│       └── Enviar mensaje a IP:port                          │
│       └── Enviar archivo a IP:port                          │
│       └── Broadcast: enviar a toda la subred                │
│                                                             │
│  [D] Protocolo de mensajes  ──────────────────────────────  │
│       └── Definir cómo distinguir mensaje vs archivo        │
│       └── Definir formato del payload enviado               │
│       └── Manejar límite de 255 bytes                       │
│                                                             │
│  [E] Señales y cierre limpio  ────────────────────────────  │
│       └── SIGINT, SIGTERM                                   │
│       └── Cerrar sockets, hilos, memoria                    │
└─────────────────────────────────────────────────────────────┘
```

### Dependencias entre partes

```
[A] Autenticación
    ↓
[D] Protocolo de mensajes  ←──────────────┐
    ↓                                     │
[B] Receptor ─────────────────────────────┤
[C] Emisor  ──────────────────────────────┘
    ↓
[E] Señales (transversal a todo)
```

**[A] debe resolverse primero** — bloquea el inicio de todo. **[D] debe diseñarse antes de implementar B y C.**

---

## 4. Riesgos y Puntos Difíciles

| Parte | Riesgo | Por qué es difícil |
|---|---|---|
| **Autenticación** | Formato exacto del protocolo | `\r\n`, recibir "SI\r\nNombre\r\n" vs "NO\r\n" |
| **Receptor concurrente** | Hilo vs fork, compartir recursos | Si se usa threading, cuidado con stdout compartido |
| **Protocolo de mensajes** | Distinguir mensaje de archivo | El receptor debe saber qué está recibiendo |
| **Broadcast** | Calcular dirección de broadcast correctamente | Requiere conocer la IP local y máscara |
| **Archivos** | TCP no garantiza recepción completa en un recv() | Hay que implementar lectura en bucle |
| **Señales** | SIGINT llega al hilo principal, no a todos | Hay que propagar el cierre |
| **Formato de salida** | El ejemplo es exacto, cualquier diferencia es error | Fecha, espacios, corchetes, todo importa |

---

## 5. Plan de Ataque

### Orden recomendado

```
— Diseño y base
  → Leer enunciado completo todos juntos
  → Definir protocolo de mensajes (D)
  → Implementar autenticación (A)
  → Probar auth contra ti.esi.edu.uy:33

— Núcleo
  → Implementar receptor básico (B): mensajes de texto
  → Implementar emisor básico (C): un mensaje a IP directa
  → Probar que dos instancias se comunican

— Funcionalidad completa
  → Agregar envío/recepción de archivos
  → Agregar resolución de hostname
  → Agregar broadcast

— Cierre y robustez
  → Señales y cierre limpio (E)
  → Validar formato de salida exacto
  → Pruebas de borde: mensaje largo, archivo grande, broadcast

— Entrega
  → comentarios.txt
  → Empaquetar redes-lab.tar.gz
  → Revisión final
```

---

## 6. Organización por Integrantes (grupo de 4)

| Módulo principal | Apoyo |
|---|---|
| [A] Autenticación | [E] Señales |
| [B] Receptor (texto + archivos) | [D] Protocolo |
| [C] Emisor (texto + archivos + broadcast) | [D] Protocolo |
| [D] Diseño del protocolo + integración + pruebas | todos |

> ⚠️ **Importante:** el protocolo de mensajes (D) hay que definirlo **entre todos** antes de que B y C empiecen a codear, o van a tener que rehacer trabajo.

---

## 7. Cronograma Sugerido

| Objetivo | Checkpoint |
|---|---|
| Diseño + Auth + Receptor/Emisor básico | Dos instancias se hablan |
| Archivos + Broadcast + Hostname | Demo completa funcional |
| Señales + Formato exacto + Pruebas | Todo según ejemplos |
| Documentación + Empaquetado | `redes-lab.tar.gz` listo |

---

## 8. Diseño del Protocolo de Mensajes (decisión crítica)

Esto hay que definirlo **antes de codear**. Propuesta:

El emisor envía un payload TCP con este formato:

```
TIPO usuario IP_EMISOR\r\n
[contenido]\r\n
```

Donde `TIPO` puede ser:
- `MSG` → mensaje de texto (contenido = el texto)
- `FILE nombre_archivo\r\n` → archivo (contenido = bytes del archivo)

> ⚠️ Esta decisión afecta al receptor y al emisor. Hay que acordarla entre todos antes de empezar.

Alternativa más simple: primer byte indica tipo, segundo bloque indica longitud, luego datos.

---

## 9. Próximo Paso Recomendado

**Ahora mismo:**

1. **Probar el servidor de auth** que está en `ti.esi.edu.uy:33` con `telnet` o `nc`:
```bash
nc ti.esi.edu.uy 33
# Deberías recibir: Redes 2026 - Laboratorio - Autenticación de Usuarios
# Enviá: aturing-50bc36a72e099d0ae1e78186a0859d46
# Respuesta esperada: SI\r\nAlan_Mathison_Turing\r\n
```

2. **Definir el protocolo de mensajes** entre todos (qué manda el emisor, qué entiende el receptor).

3. **Implementar la autenticación** — es lo primero que ejecuta el programa y lo más concreto.
