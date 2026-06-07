# 🔧 Guía de Trabajo con Git y GitHub — Redes Lab 1

> **Para quién es esto:** para todos los integrantes del grupo, especialmente los que nunca trabajaron en equipo con Git. Leelo de arriba a abajo la primera vez. Después usalo como referencia.

---

## 📋 Índice

1. [Estructura de ramas](#1-estructura-de-ramas)
2. [Configuración inicial — hacelo UNA sola vez](#2-configuración-inicial--hacelo-una-sola-vez)
3. [Primera vez que trabajás en una rama](#3-primera-vez-que-trabajás-en-una-rama)
4. [Flujo de trabajo diario](#4-flujo-de-trabajo-diario)
5. [Mensajes de commit estandarizados](#5-mensajes-de-commit-estandarizados)
6. [Cómo crear un Pull Request](#6-cómo-crear-un-pull-request)
7. [Cómo revisar el PR de otro](#7-cómo-revisar-el-pr-de-otro)
8. [Resolver conflictos](#8-resolver-conflictos)
9. [Qué NO hacer nunca](#9-qué-no-hacer-nunca)
10. [Comandos de referencia rápida](#10-comandos-de-referencia-rápida)
11. [FAQ — Preguntas frecuentes](#11-faq--preguntas-frecuentes)

---

## 1. Estructura de ramas

```
main                        ← código estable y probado, solo para entrega
└── develop                 ← integración de todos los módulos
    ├── feature/autenticacion   ← módulo A: auth TCP contra redes-auth
    ├── feature/receptor        ← módulo B: socket servidor, mensajes y archivos
    ├── feature/emisor          ← módulo C: stdin, broadcast, envío de archivos
    └── feature/senales         ← módulo E: SIGINT, SIGTERM, cierre limpio
```

**Reglas que no se negocian:**
- ❌ Nunca commitear directo a `main`
- ❌ Nunca commitear directo a `develop` (solo merges desde feature branches)
- ✅ Cada integrante trabaja en su rama `feature/xxx`
- ✅ Para pasar código a `develop` siempre se crea un Pull Request

### ¿Quién trabaja en qué rama?

| Módulo | Rama | Responsable |
|--------|------|-------------|
| Autenticación TCP | `feature/autenticacion` | (asignarlo) |
| Receptor de mensajes y archivos | `feature/receptor` | (asignarlo) |
| Emisor, broadcast, &file | `feature/emisor` | (asignarlo) |
| Señales y cierre limpio | `feature/senales` | (asignarlo) |

---

## 2. Configuración inicial — hacelo UNA sola vez

Esto se hace una vez por máquina. Si ya lo hiciste antes, saltá al paso 3.

### 2.1 Instalar Git (si no lo tenés)

```bash
# Ubuntu / Debian
sudo apt install git

# Verificar que funciona
git --version
```

### 2.2 Configurar tu identidad en Git

```bash
# Esto aparece en cada commit que hacés
git config --global user.name "Tu Nombre Apellido"
git config --global user.email "tu_email@ejemplo.com"

# Verificar que quedó bien
git config --list
```

> ⚠️ Usá el mismo email que registraste en GitHub, así tus commits aparecen asociados a tu cuenta.

### 2.3 Clonar el repositorio

```bash
# Clonar el repo en tu máquina (hacelo UNA sola vez)
git clone https://github.com/marcosbeta23/redes-lab1-mensajeria.git

# Entrar a la carpeta del proyecto
cd redes-lab1-mensajeria

# Ver en qué rama estás (debería decir main)
git branch
```

### 2.4 Ver todas las ramas disponibles

```bash
# Ver ramas remotas (las que están en GitHub)
git branch -r

# Deberías ver algo como:
# origin/main
# origin/develop
# origin/feature/autenticacion
# origin/feature/receptor
# origin/feature/emisor
# origin/feature/senales
```

---

## 3. Primera vez que trabajás en una rama

> **Situación:** ya clonaste el repo y querés empezar a trabajar en tu módulo.

Las ramas `feature/xxx` ya existen en GitHub. No hay que crearlas. Hay que "bajarlas" a tu máquina local.

### 3.1 Primero actualizá develop

```bash
# Ir a develop
git checkout develop

# Bajar los últimos cambios de GitHub
git pull origin develop
```

### 3.2 Conectarte a tu rama feature

```bash
# Ejemplo: si tu módulo es el receptor
git checkout feature/receptor

# Git va a detectar automáticamente que esa rama existe en GitHub
# y la va a configurar para que haga tracking con origin/feature/receptor
```

> 💡 **¿Qué es tracking?** Significa que tu rama local queda vinculada con la rama remota en GitHub. Cuando hagas `git pull` o `git push`, Git sabe a dónde ir sin que le tengas que decir explícitamente.

### 3.3 Verificar que estás en el lugar correcto

```bash
# Verificar en qué rama estás
git branch

# Debería aparecer con asterisco tu rama:
#   develop
# * feature/receptor
#   main
```

Listo, ya podés empezar a codear.

---

## 4. Flujo de trabajo diario

Cada vez que te sentás a trabajar, seguí estos pasos en orden.

### Paso 1: Antes de empezar — sincronizate con develop

```bash
# Ir a develop y bajarte lo último
git checkout develop
git pull origin develop

# Volver a tu rama feature
git checkout feature/receptor

# Traer los cambios de develop a tu rama
# (por si alguien mergeó algo mientras vos no estabas)
git merge develop
```

> ⚠️ Este paso es crítico para evitar conflictos más adelante. Hacelo **siempre** antes de empezar a trabajar.

### Paso 2: Trabajar — hacer cambios en el código

```bash
# Ver qué archivos modificaste
git status

# Ver exactamente qué cambiaste dentro de los archivos
git diff
```

### Paso 3: Agregar cambios al staging area

```bash
# Agregar un archivo específico (recomendado)
git add mensajeria.py

# Agregar todos los cambios (usar con cuidado)
git add .

# Verificar qué va a entrar en el commit
git status
```

> 💡 **Qué es el staging area:** es como una "sala de espera" antes del commit. Los archivos que agregás con `git add` van ahí. El commit guarda todo lo que está en el staging area.

### Paso 4: Hacer el commit

```bash
git commit -m "feat: agrega socket servidor que escucha en puerto"
```

> ✅ Hacé commits frecuentes y pequeños. Es mucho mejor hacer 10 commits de 20 líneas que 1 commit de 200 líneas. Si algo falla, es más fácil encontrar en dónde.

### Paso 5: Subir cambios a GitHub

```bash
git push origin feature/receptor
```

Después de esto, tus cambios están en GitHub y tus compañeros los pueden ver.

### Paso 6: Repetir

Volvé al Paso 2 y seguí trabajando. Hacé commits seguido.

---

## 5. Mensajes de commit estandarizados

Un mensaje de commit claro sirve para que todos entiendan qué cambió sin tener que leer el código.

### Formato

```
tipo: descripción corta en minúsculas (máx 72 caracteres)
```

### Tipos disponibles

| Tipo | Cuándo usarlo |
|------|---------------|
| `feat` | Agregás funcionalidad nueva |
| `fix` | Corregís un bug |
| `refactor` | Reorganizás código sin cambiar comportamiento |
| `docs` | Cambiás comentarios o documentación |
| `test` | Agregás o modificás tests |
| `chore` | Tareas de configuración, limpieza, etc. |

### Ejemplos buenos ✅

```bash
git commit -m "feat: agrega socket TCP receptor que escucha en puerto"
git commit -m "feat: implementa autenticación MD5 contra redes-auth"
git commit -m "fix: corrige formato de timestamp en salida del receptor"
git commit -m "fix: maneja correctamente desconexión abrupta del cliente"
git commit -m "refactor: separa lectura de archivos en función propia"
git commit -m "docs: agrega comentario explicando protocolo MSG/FILE"
```

### Ejemplos malos ❌

```bash
git commit -m "arreglo"
git commit -m "cambios"
git commit -m "listo"
git commit -m "no se que hice"
git commit -m "aaaaaa"
```

---

## 6. Cómo crear un Pull Request

Un Pull Request (PR) es la forma de proponer que tu código entre a `develop`. Otro integrante lo revisa y aprueba antes de que se mergee.

### ¿Cuándo crear un PR?

- Tu feature está completa y funciona
- La probaste y no rompe nada
- Empujaste tus últimos cambios con `git push`

### Pasos desde GitHub web

1. Ir a https://github.com/marcosbeta23/redes-lab1-mensajeria
2. Click en la pestaña **"Pull requests"**
3. Click en **"New pull request"**
4. Configurar:
   - **Base:** `develop`
   - **Compare:** `feature/tu-rama` (ej: `feature/receptor`)
5. Click en **"Create pull request"**
6. Completar el formulario:

```
Título: feat: implementa receptor de mensajes TCP con timestamp

Descripción:
## Qué hace este PR
- Abre socket TCP en el puerto pasado por argumento
- Acepta conexiones en un hilo separado
- Imprime mensajes con formato [YYYY.MM.DD HH:MM] IP usuario dice: msg

## Cómo probarlo
1. Ejecutar: python mensajeria.py 22764 192.168.1.240 3456
2. Desde otra terminal: echo "..." | nc localhost 22764
3. Verificar que el formato de salida coincide con el enunciado

## Checklist
- [x] El código funciona
- [x] Lo probé con casos de error
- [x] Agregué comentarios donde era necesario
```

7. Asignar a otro integrante como **Reviewer**
8. Click **"Create pull request"**

### Después de que te aprueben el PR

1. Click en **"Merge pull request"**
2. Elegir **"Squash and merge"** (agrupa todos tus commits en uno solo, más limpio)
3. Click **"Confirm squash and merge"**
4. Opcionalmente borrar la rama feature (podés seguir usándola igual)

---

## 7. Cómo revisar el PR de otro

Cuando te asignen como reviewer de un PR:

### Pasos

1. Ir al PR en GitHub
2. Leer la descripción para entender qué hace
3. Click en **"Files changed"** para ver el código
4. Podés comentar línea por línea haciendo click en el `+` que aparece al pasar por una línea
5. Si querés probarlo localmente:

```bash
# Bajar la rama de tu compañero
git fetch origin
git checkout feature/autenticacion

# Probarlo
python mensajeria.py 22764 192.168.1.240 3456
```

6. Al terminar la revisión, ir a la pestaña **"Files changed"** y hacer click en **"Review changes"**:
   - **Approve** — si todo está bien ✅
   - **Request changes** — si hay algo que corregir ❌ (dejá un comentario explicando qué)
   - **Comment** — si tenés dudas o sugerencias sin bloquear el merge

### ¿Qué revisar?

- ¿El código hace lo que dice el PR?
- ¿El formato de salida coincide exactamente con el enunciado?
- ¿Los casos de error están manejados?
- ¿El código es legible? ¿Tiene comentarios donde se necesita?
- ¿No rompe lo que ya funcionaba?

---

## 8. Resolver conflictos

Un conflicto ocurre cuando dos personas modificaron las mismas líneas de código. Git no sabe con cuál quedarse y te pide que lo resolvás a mano.

### Cómo aparece un conflicto

```
<<<<<<< HEAD
# Tu código (lo que tenés en tu rama)
    print(f"[{timestamp}] {ip} {usuario} dice: {mensaje}")
=======
# Código de develop (lo que hay en la otra rama)
    print(f"[{timestamp}] {ip_emisor} {usuario} dice: {mensaje}")
>>>>>>> origin/develop
```

### Cómo resolverlo paso a paso

```bash
# 1. Traer los últimos cambios de develop a tu rama
git checkout feature/receptor
git fetch origin
git merge origin/develop

# 2. Git te va a decir qué archivos tienen conflictos
# CONFLICT (content): Merge conflict in mensajeria.py

# 3. Abrir el archivo en conflicto con tu editor
# Buscar las marcas <<<<<<, =======, >>>>>>>

# 4. Decidir qué código mantener:
#    - ¿Tu versión? Borrás el bloque de develop
#    - ¿La versión de develop? Borrás tu bloque
#    - ¿Las dos? Combinás ambas versiones a mano
#    - Borrás SIEMPRE las marcas <<<<<<, =======, >>>>>>>

# 5. Agregar el archivo resuelto
git add mensajeria.py

# 6. Completar el merge
git commit -m "merge: resuelve conflicto en formato de salida del receptor"

# 7. Subir
git push origin feature/receptor
```

### Cómo evitar conflictos

- Sincronizate con `develop` **antes de empezar** a trabajar cada día (ver Paso 1 del flujo diario)
- Hacé PRs frecuentes, no acumulés días de trabajo
- Coordiná con el equipo quién está tocando qué archivo

---

## 9. Qué NO hacer nunca

### Comandos peligrosos — pensalos dos veces

```bash
# ❌ NUNCA esto — borra el historial del repo para todos
git push --force

# ❌ NUNCA esto en develop o main — deshace commits de otros
git reset --hard

# ❌ NUNCA esto sin entender qué hace
git rebase (en ramas compartidas)
```

### Comportamientos prohibidos

| ❌ No hacer | ✅ Hacer en cambio |
|-------------|-------------------|
| Commitear a `main` directamente | Siempre PR desde `develop` |
| Commitear a `develop` directamente | Trabajar en `feature/xxx` |
| Mergear tu propio PR sin revisión | Esperar aprobación de otro integrante |
| Subir `__pycache__/` o `.pyc` | Están en `.gitignore`, no pasa |
| Commits con mensajes vacíos o sin sentido | Mensajes descriptivos con el tipo correcto |
| Guardar contraseñas o tokens en el código | Nunca hardcodear credenciales |
| Trabajar días enteros sin commitear | Commits pequeños y frecuentes |

---

## 10. Comandos de referencia rápida

### Navegación básica

```bash
git status                      # ver qué archivos cambiaste
git branch                      # ver en qué rama estás
git branch -a                   # ver todas las ramas (locales y remotas)
git log --oneline --graph       # historial de commits visual
git diff                        # ver qué cambió en los archivos
git diff --staged               # ver qué está en staging (git add ya hecho)
```

### Moverse entre ramas

```bash
git checkout develop            # ir a develop
git checkout feature/receptor   # ir a tu rama feature
git checkout -b feature/nueva   # crear rama nueva Y moverse a ella
```

### Ciclo de trabajo

```bash
git pull origin develop         # bajar últimos cambios de develop
git add mensajeria.py           # agregar archivo al staging
git add .                       # agregar todos (con cuidado)
git commit -m "feat: ..."       # hacer commit
git push origin feature/receptor # subir al GitHub
```

### Sincronizar tu rama con develop

```bash
git checkout develop
git pull origin develop
git checkout feature/receptor
git merge develop
```

### Comandos de emergencia

```bash
# Deshacer cambios en un archivo (volver a como estaba en el último commit)
git checkout -- mensajeria.py

# Cancelar el último commit (SIN perder los cambios, antes de push)
git reset --soft HEAD~1

# Ver qué pasó en el historial (útil para deshacer errores)
git reflog

# Si hiciste git add por error, sacar del staging
git reset HEAD mensajeria.py
```

---

## 11. FAQ — Preguntas frecuentes

**¿Cómo sé en qué rama estoy?**
```bash
git branch
# La rama con * es en la que estás
```

---

**Hice cambios en la rama equivocada, ¿qué hago?**
```bash
# Guardá tus cambios temporalmente sin commitear
git stash

# Cambiarte a la rama correcta
git checkout feature/receptor

# Traer de vuelta tus cambios
git stash pop
```

---

**Alguien mergeó algo a develop y yo no tengo esos cambios**
```bash
git checkout develop
git pull origin develop
git checkout feature/mi-rama
git merge develop
# Si hay conflictos, ver sección 8
```

---

**¿Cómo veo los cambios que hizo otro en su rama?**
```bash
git fetch origin                    # bajar info de todas las ramas sin aplicar
git checkout feature/autenticacion  # moverte a su rama
git log --oneline                   # ver sus commits
```

---

**Pusheé algo que no debería, ¿cómo lo deshago?**

Antes de hacer nada, avisale al equipo. Luego:
```bash
# Ver el historial para encontrar el commit al que querés volver
git log --oneline

# Revertir un commit específico (crea un nuevo commit que deshace el anterior)
# Esto es seguro porque no borra historial
git revert <hash-del-commit>
git push origin feature/mi-rama
```

---

**¿Por qué mi `git push` falla con "rejected"?**

Alguien más hizo push antes que vos. Primero bajate sus cambios:
```bash
git pull origin feature/mi-rama
# Resolver conflictos si los hay
git push origin feature/mi-rama
```

---

**¿Qué es un "merge commit" vs "squash and merge"?**

- **Merge commit:** conserva todos tus commits individuales en el historial de develop
- **Squash and merge:** agrupa todos tus commits en uno solo antes de mergear

Para este proyecto usamos **Squash and merge** porque mantiene el historial de `develop` más limpio.

---

**Corrí `git pull` y me dice "Your local changes would be overwritten"**

Significa que tenés cambios sin commitear que chocan con lo que viene del remoto. Tenés dos opciones:

```bash
# Opción 1: Guardá tus cambios primero con stash
git stash
git pull origin feature/mi-rama
git stash pop

# Opción 2: Commitealos antes de hacer pull
git add .
git commit -m "wip: guardando cambios antes de pull"
git pull origin feature/mi-rama
```

---

## 📞 Recordatorio de comunicación

Antes de empezar a trabajar, avisale al grupo qué vas a hacer.
Cuando termines una feature, avisale al grupo y pedí revisión.
Si hay algo que no entendés de Git, preguntá antes de hacer algo.

---

**Repositorio:** https://github.com/marcosbeta23/redes-lab1-mensajeria  
**Trello:** https://trello.com/b/JDNfTx0V  
**Entrega:** 7 de junio 2026 a las 23:59 UYT  
**Última actualización:** 2026-05-20
