# Base de Datos Avanzadas · Proyecto 2 (Flask + MongoDB)

Aplicación web en **Flask** con **MongoDB** para administrar los datos de una empresa: empleados, departamentos, proyectos, asignaciones de horas y dependientes. Incluye un panel con estadísticas, búsqueda y filtros, operaciones CRUD completas y una API JSON.

Proyecto de la materia de Bases de Datos Avanzadas, Universidad Autónoma de Chihuahua (UACH).

## Funcionalidades

- **Panel de inicio** con totales de empleados, departamentos, proyectos, asignaciones y dependientes, además de salario promedio, máximo y mínimo (*pipeline* de agregación de MongoDB).
- **Empleados:** alta, edición y baja; búsqueda por nombre, apellido o SSN; filtro por departamento; validación de SSN duplicado.
- **Departamentos:** CRUD con múltiples ubicaciones, jefe asignado y número de empleados por departamento.
- **Proyectos:** CRUD con departamento responsable y conteo de trabajadores asignados.
- **Asignaciones (works_on):** relación empleado-proyecto con horas trabajadas.
- **Dependientes:** CRUD de los dependientes de cada empleado.
- **API JSON** de solo lectura para integraciones.

## Colecciones de MongoDB

Base de datos: `empresa_db`

| Colección | Contenido |
|---|---|
| `employee` | Datos personales, salario, supervisor y departamento (`Dno`) |
| `department` | Nombre, número, jefe (`Mgr_ssn`) y fecha de inicio |
| `dept_locations` | Ubicaciones de cada departamento |
| `project` | Nombre, número, ubicación y departamento |
| `works_on` | Empleado (`Essn`), proyecto (`Pno`) y horas |
| `dependent` | Dependientes por empleado y parentesco |

## Endpoints principales

| Ruta | Descripción |
|---|---|
| `/` | Panel con estadísticas |
| `/employees`, `/departments`, `/projects`, `/works_on`, `/dependents` | Listados |
| `/<módulo>/new`, `/<módulo>/edit/<id>`, `/<módulo>/delete/<id>` | Alta, edición y baja |
| `/api/employees` | Empleados en JSON |
| `/api/projects` | Proyectos en JSON |

## Tecnologías

- Python 3, Flask y Jinja2
- MongoDB con PyMongo
- HTML (plantillas en `templates/`)

## Cómo ejecutarlo

### Requisitos

- Python 3.10 o superior
- MongoDB en ejecución (local o remoto)

### Pasos

1. Clona el repositorio:
   ```bash
   git clone https://github.com/CourRam/Base-de-datos-Av-2.git
   cd Base-de-datos-Av-2
   ```
2. Instala las dependencias:
   ```bash
   pip install flask pymongo
   ```
3. (Opcional) Define la conexión a MongoDB. Por defecto usa `mongodb://localhost:27017/`:
   ```bash
   export MONGO_URI="mongodb://usuario:clave@host:27017/"
   ```
4. Carga los datos de ejemplo en la base `empresa_db`. <!-- [COMPLETAR: indica cómo se cargan los datos (mongoimport, script, etc.)] -->
5. Inicia la aplicación:
   ```bash
   python app.py
   ```
6. Abre `http://localhost:5000`.

## Estructura del proyecto

```
├── app.py          # Rutas, lógica y conexión a MongoDB
└── templates/      # Vistas HTML de cada módulo
```

## Autor

**Joseph Daniel Ramírez Torres** · [GitHub](https://github.com/CourRam)
