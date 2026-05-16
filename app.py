from flask import (
    Flask, render_template, request,
    session, redirect, url_for
)

from functools import wraps
import pandas as pd
from datetime import datetime
import os


# ==================================================
# CONFIGURACIÓN APP
# ==================================================

app = Flask(__name__)
app.secret_key = "wh4xf5hu62qtf8u"
app.config["SESSION_PERMANENT"] = False


# ==================================================
# RUTAS LOCALES
# ==================================================

BASE_DIR = os.path.join(app.root_path, "static", "assets", "base")
DATA_DIR = os.path.join(app.root_path, "static", "assets", "data")

# Asegurar que las carpetas existen
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


# ==================================================
# FUNCIONES DE ARCHIVOS LOCALES
# ==================================================

def leer_excel_local(ruta):

    df = pd.read_excel(ruta)

    return df


def leer_csv_local(ruta):

    if not os.path.exists(ruta):
        return pd.DataFrame()

    try:

        df = pd.read_csv(ruta)

        return df

    except (pd.errors.EmptyDataError, FileNotFoundError):

        return pd.DataFrame()


def guardar_csv_local(df, ruta):

    df.to_csv(ruta, index=False)


# ==================================================
# USUARIOS
# ==================================================

def cargar_usuarios():

    ruta = os.path.join(BASE_DIR, "usuarios.xlsx")

    df = leer_excel_local(ruta)

    df.columns = df.columns.str.strip()

    usuarios = {}

    for _, row in df.iterrows():

        usuario = str(row["usuario"]).strip()

        usuarios[usuario] = {

            "password": str(row["password"]).strip(),
            "institucion": str(row["institucion"]).strip(),
            "rol": str(row["rol"]).strip().lower()

        }

    return usuarios

# ==================================================
# CARGAR BASES (DESDE LOCAL)
# ==================================================

df_actores = leer_excel_local(os.path.join(BASE_DIR, "pi-actores.xlsx"))
df_alineacion = leer_excel_local(os.path.join(BASE_DIR, "alineacion_pi.xlsx"))


df_actores.columns = df_actores.columns.str.strip()
df_alineacion.columns = df_alineacion.columns.str.strip()

df_actores["Actor"] = df_actores["Actor"].astype(str).str.strip()
df_actores["Línea de acción"] = df_actores["Línea de acción"].astype(str).str.strip()

df_alineacion["Línea de acción"] = df_alineacion["Línea de acción"].astype(str).str.strip()
df_alineacion["Estrategia"] = df_alineacion["Estrategia"].astype(str).str.strip()

alineacion_dict = dict(
    zip(df_alineacion["Línea de acción"], df_alineacion["Estrategia"])
)


# ==================================================
# LOGIN REQUIRED
# ==================================================

def login_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if "usuario" not in session:
            return redirect(url_for("home"))

        return f(*args, **kwargs)

    return wrapper

def admin_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if "usuario" not in session:
            return redirect(url_for("home"))

        if session.get("rol") != "administrador":
            return redirect(url_for("home"))

        return f(*args, **kwargs)

    return wrapper

# ==================================================
# FUNCIONES DE DATOS
# ==================================================

def obtener_lineas_accion(institucion):

    df_inst = df_actores[df_actores["Actor"] == str(institucion).strip()]

    return df_inst["Línea de acción"].dropna().unique().tolist()


def obtener_alineacion():

    return alineacion_dict


def obtener_acciones(institucion):

    ruta = os.path.join(DATA_DIR, "data_acciones.csv")

    df = leer_csv_local(ruta)

    if df.empty:
        return []

    df_inst = df[df["institucion"] == institucion]

    return df_inst.to_dict(orient="records")


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        usuario=session.get("usuario"),
        institucion=session.get("institucion"),
        error=None
    )

# ==================================================
# LOGIN
# ==================================================

@app.route("/login", methods=["POST"])
def login():

    usuarios = cargar_usuarios()

    user = request.form.get("usuario", "").strip()
    password = request.form.get("password", "").strip()

    if user in usuarios and usuarios[user]["password"] == password:

        session["usuario"] = user
        session["institucion"] = usuarios[user]["institucion"]
        session["rol"] = usuarios[user]["rol"]

        return redirect(url_for("home"))

    return render_template(
        "index.html",
        usuario=None,
        institucion=None,
        error="Credenciales inválidas"
    )

# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ==================================================
# CARGA
# ==================================================

@app.route("/carga")
@login_required
def carga():

    institucion = session.get("institucion")

    lineas_accion = obtener_lineas_accion(institucion)

    alineacion = obtener_alineacion()

    acciones = obtener_acciones(institucion)

    return render_template(
        "carga.html",
        usuario=session.get("usuario"),
        institucion=institucion,
        lineas_accion=lineas_accion,
        alineacion=alineacion,
        acciones=acciones
    )


# ==================================================
# GUARDAR
# ==================================================

@app.route("/guardar", methods=["POST"])
@login_required
def guardar():

    estado = request.form.get("estado", "borrador")

    lineas = request.form.getlist("linea_accion[]")
    estrategias = request.form.getlist("estrategia[]")
    acciones = request.form.getlist("accion[]")
    fechas_inicio = request.form.getlist("fecha_inicio[]")
    fechas_fin = request.form.getlist("fecha_fin[]")
    tipos = request.form.getlist("tipo[]")

    institucion = session.get("institucion")
    usuario = session.get("usuario")

    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    registros = []

    n = min(
        len(lineas),
        len(estrategias),
        len(acciones),
        len(fechas_inicio),
        len(fechas_fin),
        len(tipos)
    )

    for i in range(n):

        registros.append({

            "institucion": institucion,
            "usuario": usuario,
            "linea_accion": lineas[i],
            "estrategia": estrategias[i],
            "accion": acciones[i],
            "fecha_inicio": fechas_inicio[i],
            "fecha_fin": fechas_fin[i],
            "tipo": tipos[i],
            "estado": estado,
            "fecha_registro": timestamp
        })

    df_nuevo = pd.DataFrame(registros)

    ruta = os.path.join(DATA_DIR, "data_acciones.csv")

    df_existente = leer_csv_local(ruta)

    if not df_existente.empty:

        df_existente = df_existente[
            df_existente["institucion"] != institucion
        ]

    df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)

    guardar_csv_local(df_final, ruta)

    return redirect(url_for("carga"))


# ==================================================

if __name__ == "__main__":

    app.run(debug=True)