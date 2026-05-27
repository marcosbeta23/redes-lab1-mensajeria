# Redes de Computadoras — Laboratorio 1
## Mensajería con Sockets TCP/UDP

** Tecnólogo en Informática — 2026**

---

## Descripción

Aplicación Python que permite enviar y recibir mensajes y archivos entre pares mediante sockets TCP. El programa consta de una parte receptora y una emisora que corren en paralelo mediante hilos.

## Invocación

```bash
python mensajeria.py <port> <ipAuth> <portAuth>
```

### Ejemplo
```bash
python mensajeria.py 22764 192.168.1.240 3456
```

## Entrega
- **Fecha límite:** 7 de junio 2026 a las 23:59 UYT
- **Archivos:** `mensajeria.py`, `comentarios.txt`, empaquetados en `redes-lab.tar.gz`

## Estructura de ramas

```
main          ← código estable, solo via PR aprobado
└── develop   ← integración continua
    ├── feature/autenticacion
    ├── feature/receptor
    ├── feature/emisor
    └── feature/senales
```

## Reglas de trabajo con Git

Ver [`GITHUB_RULES.md`](./GITHUB_RULES.md) para el flujo de trabajo completo.
