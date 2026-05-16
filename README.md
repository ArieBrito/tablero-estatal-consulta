# tablero-estatal-consulta

# Tablero de Implementación

Sistema institucional de seguimiento al **Programa de Implementación de la Política Estatal Anticorrupción**. Permite a las instituciones ejecutoras registrar y dar seguimiento a las acciones comprometidas en cada línea estratégica.

## Características

- Autenticación por usuario, contraseña, institución y rol.
- Registro de acciones alineadas a líneas estratégicas y estrategias del programa.
- Captura en formato tabular con múltiples filas por sesión.
- Guardado en estado **borrador** o **enviado**.
- Lectura de catálogos desde archivos Excel locales.
- Persistencia de registros en CSV.

## Estructura del proyecto

```
tablero-implementacion/
├── app.py
├── templates/
│   ├── base.html
│   ├── index.html
│   └── carga.html
└── static/
    ├── css/
    │   └── style.css
    └── assets/
        ├── base/
        │   ├── usuarios.xlsx
        │   ├── pi-actores.xlsx
        │   └── alineacion_pi.xlsx
        ├── data/
        │   └── data_acciones.csv
        ├── icons/
        └── logo/
```

## Requisitos

- Python 3.10+
- Flask
- pandas
- openpyxl

Instalación de dependencias:

```bash
pip install flask pandas openpyxl
```

## Archivos base

Dentro de `static/assets/base/` deben existir:

- **`usuarios.xlsx`** — columnas: `usuario`, `password`, `institucion`, `rol`.
- **`pi-actores.xlsx`** — columnas: `Actor`, `Línea de acción`.
- **`alineacion_pi.xlsx`** — columnas: `Línea de acción`, `Estrategia`.

## Ejecución

```bash
python app.py
```

## Flujo de uso

1. El usuario inicia sesión desde la pantalla principal.
2. Accede al módulo de **Carga** donde ve las líneas de acción asignadas a su institución.
3. Registra una o varias acciones con fechas y tipo.
4. Guarda como **borrador** o realiza el **envío** definitivo.
5. Los registros se almacenan en `static/assets/data/data_acciones.csv`.

## Notas

- Evita ubicar el proyecto dentro de carpetas sincronizadas con OneDrive o Dropbox, ya que pueden bloquear los archivos durante la lectura/escritura.
- Cierra los archivos Excel antes de ejecutar la aplicación.