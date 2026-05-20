# 🔧 Reglas de Trabajo con GitHub — Redes Lab 1

## 📌 Estructura de Ramas

```
main                   ← código estable, solo merges aprobados
└── develop            ← integración continua
    ├── feature/autenticacion   ← módulo auth TCP contra redes-auth
    ├── feature/receptor        ← socket servidor, mensajes y archivos
    ├── feature/emisor          ← stdin, broadcast, enviar archivos
    └── feature/senales         ← SIGINT, SIGTERM, cierre limpio
```

**Regla de oro:**
- ❌ NUNCA hacer commits directos a `main`
- ✅ TODO pasa por Pull Request revisado desde `develop`

---

## 🚀 Flujo de Trabajo

### 1. Comenzar una tarea

```bash
# Asegurarte de estar en develop actualizado
git checkout develop
git pull origin develop

# Crear tu rama de feature
git checkout -b feature/autenticacion  # o la que te toque
```

### 2. Trabajar y commitear

```bash
git add mensajeria.py
git commit -m "feat: implementa autenticación con servidor MD5"
git push origin feature/autenticacion
```

### 3. Crear Pull Request cuando termines

- Base: `develop` ← Compare: `feature/tu-rama`
- Título claro, descripción de cambios, cómo probar
- Al menos **1 aprobación** antes de mergear
- Elegir **Squash and merge** si hay muchos commits pequeños

---

## 📝 Mensajes de Commit Estandarizados

```
feat:     nueva funcionalidad
fix:      corrección de bug
refactor: refactorización sin cambiar funcionalidad
docs:     cambios en documentación
test:     agregar o modificar tests
chore:    tareas menores (configuración, etc.)
```

### Ejemplos
```bash
git commit -m "feat: agrega receptor de mensajes TCP"
git commit -m "fix: corrige formato de timestamp en logs"
git commit -m "refactor: separa lógica de autenticación"
```

---

## ⚠️ Qué NO Hacer

- ❌ `git push --force` (destruye historial)
- ❌ Commitear sin probar
- ❌ Mergear tu propio PR sin revisión
- ❌ Trabajar en `main` directamente
- ❌ Subir `__pycache__`, archivos `.pyc`

---

## 🎯 Merge a Main (solo para entrega)

Solo cuando:
- Todas las features están integradas en `develop`
- El programa fue probado end-to-end completo
- `comentarios.txt` está actualizado
- Falta menos de 1 semana para la entrega

---

## 📦 Checklist Entrega Final

```bash
git checkout main
git pull origin main
python mensajeria.py 22764 192.168.1.240 3456  # prueba final
tar -czvf redes-lab.tar.gz mensajeria.py comentarios.txt
```

---

## 🛠️ Comandos Ütiles

```bash
git status                    # estado actual
git branch -a                 # ver todas las ramas
git log --oneline --graph     # historial visual
git checkout develop          # volver a develop
git pull origin develop       # actualizar develop
git reset --soft HEAD~1       # cancelar último commit (antes de push)
```

---

**Última actualización:** 2026-05-20  
**Repositorio:** https://github.com/marcosbeta23/redes-lab1-mensajeria
