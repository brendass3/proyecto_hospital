from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)


app = Flask(__name__)

app.secret_key = "vida-sana-clave-local-2026"


# =====================================
# CONEXIÓN CON MONGODB
# =====================================

cliente = MongoClient(
    "mongodb://127.0.0.1:27017/"
)

db = cliente["hospital_vida_sana"]

usuarios = db["usuarios"]
pacientes = db["pacientes"]
medicos = db["medicos"]
enfermeria = db["enfermeria"]
citas = db["citas"]
mensajes = db["mensajes"]
inventario = db["inventario"]


# No permite dos usuarios con el mismo correo
usuarios.create_index(
    "correo",
    unique=True
)


# =====================================
# USUARIO ADMINISTRADOR INICIAL
# =====================================

def crear_administrador():

    administrador = usuarios.find_one({
        "correo": "admin@vidasana.mx"
    })

    if not administrador:

        usuarios.insert_one({
            "nombre": "Administrador",
            "correo": "admin@vidasana.mx",
            "password": generate_password_hash("123456"),
            "rol": "administrador",
            "estado": "Activo",
            "fecha_creacion": datetime.now()
        })


# =====================================
# DECORADORES
# =====================================

def login_required(funcion):

    @wraps(funcion)
    def funcion_protegida(*args, **kwargs):

        if "usuario_id" not in session:

            flash(
                "Debes iniciar sesión para acceder.",
                "danger"
            )

            return redirect(url_for("login"))

        return funcion(*args, **kwargs)

    return funcion_protegida


def administrador_required(funcion):

    @wraps(funcion)
    def funcion_protegida(*args, **kwargs):

        if session.get("usuario_rol") != "administrador":

            flash(
                "Solo el administrador puede acceder.",
                "danger"
            )

            return redirect(url_for("panel"))

        return funcion(*args, **kwargs)

    return funcion_protegida


# =====================================
# CONVERSIÓN DE ID
# =====================================

def convertir_id(valor):

    try:
        return ObjectId(valor)

    except Exception:
        return None


# =====================================
# PÁGINA PRINCIPAL
# =====================================

@app.route("/")
def inicio():

    return render_template(
        "inicio.html"
    )


# =====================================
# REGISTRO
# =====================================

@app.route(
    "/registro",
    methods=["GET", "POST"]
)
def registro():

    if request.method == "POST":

        nombre = request.form.get(
            "nombre",
            ""
        ).strip()

        correo = request.form.get(
            "correo",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirmar_password = request.form.get(
            "confirmar_password",
            ""
        )

        rol = request.form.get(
            "rol",
            "paciente"
        )

        errores = []

        if len(nombre) < 3:

            errores.append(
                "El nombre debe tener al menos 3 caracteres."
            )

        if "@" not in correo or "." not in correo:

            errores.append(
                "Escribe un correo electrónico válido."
            )

        if len(password) < 6:

            errores.append(
                "La contraseña debe tener al menos 6 caracteres."
            )

        if password != confirmar_password:

            errores.append(
                "Las contraseñas no coinciden."
            )

        usuario_existente = usuarios.find_one({
            "correo": correo
        })

        if usuario_existente:

            errores.append(
                "Ese correo ya está registrado."
            )

        if errores:

            for error in errores:

                flash(
                    error,
                    "danger"
                )

            return render_template(
                "registro.html",
                nombre=nombre,
                correo=correo
            )

        nuevo_usuario = {
            "nombre": nombre,
            "correo": correo,
            "password": generate_password_hash(password),
            "rol": rol,
            "estado": "Activo",
            "fecha_creacion": datetime.now()
        }

        try:

            usuarios.insert_one(
                nuevo_usuario
            )

        except DuplicateKeyError:

            flash(
                "Ese correo ya está registrado.",
                "danger"
            )

            return render_template(
                "registro.html",
                nombre=nombre,
                correo=correo
            )

        flash(
            "Cuenta creada correctamente.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "registro.html"
    )


# =====================================
# INICIO DE SESIÓN
# =====================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        correo = request.form.get(
            "correo",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        usuario = usuarios.find_one({
            "correo": correo
        })

        if not usuario:

            flash(
                "No existe una cuenta con ese correo.",
                "danger"
            )

            return render_template(
                "login.html"
            )

        contraseña_correcta = check_password_hash(
            usuario["password"],
            password
        )

        if not contraseña_correcta:

            flash(
                "La contraseña es incorrecta.",
                "danger"
            )

            return render_template(
                "login.html"
            )

        if usuario.get("estado") != "Activo":

            flash(
                "Esta cuenta está desactivada.",
                "danger"
            )

            return render_template(
                "login.html"
            )

        session["usuario_id"] = str(
            usuario["_id"]
        )

        session["usuario_nombre"] = usuario[
            "nombre"
        ]

        session["usuario_rol"] = usuario[
            "rol"
        ]

        flash(
            f"Bienvenido, {usuario['nombre']}.",
            "success"
        )

        return redirect(
            url_for("panel")
        )

    return render_template(
        "login.html"
    )


# =====================================
# CERRAR SESIÓN
# =====================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Sesión cerrada correctamente.",
        "success"
    )

    return redirect(
        url_for("inicio")
    )


# =====================================
# PANEL PRINCIPAL
# =====================================

@app.route("/panel")
@login_required
def panel():

    proximas_citas = list(
        citas.find()
        .sort([
            ("fecha", 1),
            ("hora", 1)
        ])
        .limit(8)
    )

    return render_template(
        "panel.html",
        total_citas=citas.count_documents({}),
        total_pacientes=pacientes.count_documents({}),
        total_medicos=medicos.count_documents({
            "estado": "Activo"
        }),
        total_enfermeria=enfermeria.count_documents({}),
        ultimas_citas=proximas_citas
    )


# =====================================
# CITAS
# =====================================

@app.route(
    "/citas",
    methods=["GET", "POST"]
)
@login_required
def modulo_citas():

    if request.method == "POST":

        paciente_id = convertir_id(
            request.form.get("paciente_id")
        )

        medico_id = convertir_id(
            request.form.get("medico_id")
        )

        fecha = request.form.get(
            "fecha",
            ""
        )

        hora = request.form.get(
            "hora",
            ""
        )

        paciente = pacientes.find_one({
            "_id": paciente_id
        })

        medico = medicos.find_one({
            "_id": medico_id
        })

        if not paciente or not medico:

            flash(
                "Selecciona un paciente y un médico válidos.",
                "danger"
            )

            return redirect(
                url_for("modulo_citas")
            )

        cita_existente = citas.find_one({
            "medico_id": str(medico_id),
            "fecha": fecha,
            "hora": hora
        })

        if cita_existente:

            flash(
                "El médico ya tiene una cita en ese horario.",
                "danger"
            )

            return redirect(
                url_for("modulo_citas")
            )

        nueva_cita = {
            "paciente_id": str(paciente_id),
            "paciente_nombre": paciente["nombre"],
            "medico_id": str(medico_id),
            "medico_nombre": medico["nombre"],
            "especialidad": request.form.get(
                "especialidad"
            ),
            "fecha": fecha,
            "hora": hora,
            "motivo": request.form.get(
                "motivo",
                ""
            ),
            "estado": "Pendiente",
            "fecha_creacion": datetime.now()
        }

        citas.insert_one(
            nueva_cita
        )

        flash(
            "Cita registrada correctamente.",
            "success"
        )

        return redirect(
            url_for("modulo_citas")
        )

    lista_pacientes = list(
        pacientes.find().sort(
            "nombre",
            1
        )
    )

    lista_medicos = list(
        medicos.find({
            "estado": "Activo"
        }).sort(
            "nombre",
            1
        )
    )

    lista_citas = list(
        citas.find().sort([
            ("fecha", 1),
            ("hora", 1)
        ])
    )

    return render_template(
        "citas.html",
        pacientes=lista_pacientes,
        medicos=lista_medicos,
        citas=lista_citas
    )


@app.post(
    "/citas/eliminar/<id>"
)
@login_required
def eliminar_cita(id):

    identificador = convertir_id(
        id
    )

    if identificador:

        citas.delete_one({
            "_id": identificador
        })

    flash(
        "Cita eliminada correctamente.",
        "success"
    )

    return redirect(
        url_for("modulo_citas")
    )


# =====================================
# PACIENTES
# =====================================

@app.route(
    "/pacientes",
    methods=["GET", "POST"]
)
@login_required
def modulo_pacientes():

    if request.method == "POST":

        try:

            edad = int(
                request.form.get(
                    "edad",
                    0
                )
            )

        except ValueError:

            edad = 0

        paciente = {
            "nombre": request.form.get(
                "nombre",
                ""
            ).strip(),

            "edad": edad,

            "telefono": request.form.get(
                "telefono",
                ""
            ).strip(),

            "correo": request.form.get(
                "correo",
                ""
            ).strip(),

            "direccion": request.form.get(
                "direccion",
                ""
            ).strip(),

            "fecha_registro": datetime.now()
        }

        pacientes.insert_one(
            paciente
        )

        flash(
            "Paciente agregado correctamente.",
            "success"
        )

        return redirect(
            url_for("modulo_pacientes")
        )

    buscar = request.args.get(
        "buscar",
        ""
    ).strip()

    filtro = {}

    if buscar:

        filtro = {
            "$or": [
                {
                    "nombre": {
                        "$regex": buscar,
                        "$options": "i"
                    }
                },
                {
                    "telefono": {
                        "$regex": buscar,
                        "$options": "i"
                    }
                },
                {
                    "correo": {
                        "$regex": buscar,
                        "$options": "i"
                    }
                }
            ]
        }

    lista_pacientes = list(
        pacientes.find(filtro).sort(
            "nombre",
            1
        )
    )

    return render_template(
        "pacientes.html",
        pacientes=lista_pacientes,
        buscar=buscar
    )


@app.route(
    "/pacientes/editar/<id>",
    methods=["GET", "POST"]
)
@login_required
def editar_paciente(id):

    identificador = convertir_id(
        id
    )

    paciente = pacientes.find_one({
        "_id": identificador
    })

    if not paciente:

        flash(
            "Paciente no encontrado.",
            "danger"
        )

        return redirect(
            url_for("modulo_pacientes")
        )

    if request.method == "POST":

        pacientes.update_one(
            {
                "_id": identificador
            },
            {
                "$set": {
                    "nombre": request.form.get(
                        "nombre",
                        ""
                    ).strip(),

                    "edad": int(
                        request.form.get(
                            "edad",
                            0
                        )
                    ),

                    "telefono": request.form.get(
                        "telefono",
                        ""
                    ).strip(),

                    "correo": request.form.get(
                        "correo",
                        ""
                    ).strip(),

                    "direccion": request.form.get(
                        "direccion",
                        ""
                    ).strip()
                }
            }
        )

        flash(
            "Paciente actualizado correctamente.",
            "success"
        )

        return redirect(
            url_for("modulo_pacientes")
        )

    return render_template(
        "editar_paciente.html",
        paciente=paciente
    )


@app.post(
    "/pacientes/eliminar/<id>"
)
@login_required
def eliminar_paciente(id):

    identificador = convertir_id(
        id
    )

    if identificador:

        pacientes.delete_one({
            "_id": identificador
        })

    flash(
        "Paciente eliminado correctamente.",
        "success"
    )

    return redirect(
        url_for("modulo_pacientes")
    )


# =====================================
# MÉDICOS
# =====================================

@app.route(
    "/medicos",
    methods=["GET", "POST"]
)
@login_required
def modulo_medicos():

    if request.method == "POST":

        medico = {
            "nombre": request.form.get(
                "nombre",
                ""
            ).strip(),

            "especialidad": request.form.get(
                "especialidad",
                ""
            ).strip(),

            "cedula": request.form.get(
                "cedula",
                ""
            ).strip(),

            "telefono": request.form.get(
                "telefono",
                ""
            ).strip(),

            "correo": request.form.get(
                "correo",
                ""
            ).strip(),

            "horario": request.form.get(
                "horario",
                ""
            ).strip(),

            "estado": "Activo",
            "fecha_registro": datetime.now()
        }

        medicos.insert_one(
            medico
        )

        flash(
            "Médico agregado correctamente.",
            "success"
        )

        return redirect(
            url_for("modulo_medicos")
        )

    lista_medicos = list(
        medicos.find().sort(
            "nombre",
            1
        )
    )

    return render_template(
        "medicos.html",
        medicos=lista_medicos
    )


@app.post(
    "/medicos/eliminar/<id>"
)
@login_required
def eliminar_medico(id):

    identificador = convertir_id(
        id
    )

    if identificador:

        medicos.delete_one({
            "_id": identificador
        })

    flash(
        "Médico eliminado correctamente.",
        "success"
    )

    return redirect(
        url_for("modulo_medicos")
    )


# =====================================
# ENFERMERÍA
# =====================================

@app.route(
    "/enfermeria",
    methods=["GET", "POST"]
)
@login_required
def modulo_enfermeria():

    if request.method == "POST":

        personal = {
            "nombre": request.form.get(
                "nombre",
                ""
            ).strip(),

            "turno": request.form.get(
                "turno",
                ""
            ).strip(),

            "area": request.form.get(
                "area",
                ""
            ).strip(),

            "telefono": request.form.get(
                "telefono",
                ""
            ).strip(),

            "estado": "Disponible",
            "fecha_registro": datetime.now()
        }

        enfermeria.insert_one(
            personal
        )

        flash(
            "Personal de enfermería agregado.",
            "success"
        )

        return redirect(
            url_for("modulo_enfermeria")
        )

    buscar = request.args.get(
        "buscar",
        ""
    ).strip()

    filtro = {}

    if buscar:

        filtro = {
            "$or": [
                {
                    "nombre": {
                        "$regex": buscar,
                        "$options": "i"
                    }
                },
                {
                    "area": {
                        "$regex": buscar,
                        "$options": "i"
                    }
                },
                {
                    "turno": {
                        "$regex": buscar,
                        "$options": "i"
                    }
                }
            ]
        }

    personal = list(
        enfermeria.find(filtro).sort(
            "nombre",
            1
        )
    )

    return render_template(
        "enfermeria.html",
        personal=personal,
        buscar=buscar
    )


@app.post(
    "/enfermeria/eliminar/<id>"
)
@login_required
def eliminar_enfermero(id):

    identificador = convertir_id(
        id
    )

    if identificador:

        enfermeria.delete_one({
            "_id": identificador
        })

    flash(
        "Personal eliminado correctamente.",
        "success"
    )

    return redirect(
        url_for("modulo_enfermeria")
    )


# =====================================
# ADMINISTRACIÓN
# =====================================

@app.route(
    "/administracion"
)
@login_required
@administrador_required
def administracion():

    return render_template(
        "administracion.html",
        total_usuarios=usuarios.count_documents({}),
        total_inventario=inventario.count_documents({}),
        total_mensajes=mensajes.count_documents({})
    )


# =====================================
# USUARIOS ADMINISTRATIVOS
# =====================================

@app.route(
    "/administracion/usuarios",
    methods=["GET", "POST"]
)
@login_required
@administrador_required
def modulo_usuarios():

    if request.method == "POST":

        nombre = request.form.get(
            "nombre",
            ""
        ).strip()

        correo = request.form.get(
            "correo",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        rol = request.form.get(
            "rol",
            "paciente"
        )

        if usuarios.find_one({
            "correo": correo
        }):

            flash(
                "Ese correo ya está registrado.",
                "danger"
            )

            return redirect(
                url_for("modulo_usuarios")
            )

        if len(password) < 6:

            flash(
                "La contraseña debe tener mínimo 6 caracteres.",
                "danger"
            )

            return redirect(
                url_for("modulo_usuarios")
            )

        try:

            usuarios.insert_one({
                "nombre": nombre,
                "correo": correo,
                "password": generate_password_hash(
                    password
                ),
                "rol": rol,
                "estado": "Activo",
                "fecha_creacion": datetime.now()
            })

        except DuplicateKeyError:

            flash(
                "Ese correo ya está registrado.",
                "danger"
            )

            return redirect(
                url_for("modulo_usuarios")
            )

        flash(
            "Usuario creado correctamente.",
            "success"
        )

        return redirect(
            url_for("modulo_usuarios")
        )

    lista_usuarios = list(
        usuarios.find().sort(
            "nombre",
            1
        )
    )

    return render_template(
        "usuarios.html",
        usuarios=lista_usuarios
    )


# =====================================
# INVENTARIO
# =====================================

@app.route(
    "/administracion/inventario",
    methods=["GET", "POST"]
)
@login_required
@administrador_required
def modulo_inventario():

    if request.method == "POST":

        producto = {
            "nombre": request.form.get(
                "nombre",
                ""
            ).strip(),

            "categoria": request.form.get(
                "categoria",
                ""
            ).strip(),

            "cantidad": int(
                request.form.get(
                    "cantidad",
                    0
                )
            ),

            "stock_minimo": int(
                request.form.get(
                    "stock_minimo",
                    0
                )
            ),

            "fecha_actualizacion": datetime.now()
        }

        inventario.insert_one(
            producto
        )

        flash(
            "Producto agregado al inventario.",
            "success"
        )

        return redirect(
            url_for("modulo_inventario")
        )

    productos = list(
        inventario.find().sort(
            "nombre",
            1
        )
    )

    return render_template(
        "inventario.html",
        productos=productos
    )


# =====================================
# CONTACTO
# =====================================

@app.route(
    "/contacto",
    methods=["GET", "POST"]
)
def contacto():

    if request.method == "POST":

        mensaje = {
            "nombre": request.form.get(
                "nombre",
                ""
            ).strip(),

            "correo": request.form.get(
                "correo",
                ""
            ).strip(),

            "asunto": request.form.get(
                "asunto",
                ""
            ).strip(),

            "mensaje": request.form.get(
                "mensaje",
                ""
            ).strip(),

            "estado": "No leído",
            "fecha": datetime.now()
        }

        mensajes.insert_one(
            mensaje
        )

        flash(
            "Mensaje enviado correctamente.",
            "success"
        )

        return redirect(
            url_for("contacto")
        )

    return render_template(
        "contacto.html"
    )


# =====================================
# DATOS DE PRUEBA
# =====================================

@app.route(
    "/insertar-datos-prueba"
)
def insertar_datos_prueba():

    if pacientes.count_documents({}) == 0:

        pacientes.insert_many([
            {
                "nombre": "María González",
                "edad": 34,
                "telefono": "55 1234 5678",
                "correo": "maria@example.com",
                "direccion": "Tultepec, Estado de México",
                "fecha_registro": datetime.now()
            },
            {
                "nombre": "José Hernández",
                "edad": 51,
                "telefono": "55 9876 5432",
                "correo": "jose@example.com",
                "direccion": "Tultepec, Estado de México",
                "fecha_registro": datetime.now()
            },
            {
                "nombre": "Lucía Ramírez",
                "edad": 27,
                "telefono": "55 2468 1357",
                "correo": "lucia@example.com",
                "direccion": "Tultepec, Estado de México",
                "fecha_registro": datetime.now()
            }
        ])

    if medicos.count_documents({}) == 0:

        medicos.insert_many([
            {
                "nombre": "Dra. Ana Martínez",
                "especialidad": "Medicina general",
                "cedula": "1234567",
                "telefono": "55 1111 2222",
                "correo": "ana@vidasana.mx",
                "horario": "Lun-Vie 08:00-14:00",
                "estado": "Activo",
                "fecha_registro": datetime.now()
            },
            {
                "nombre": "Dr. Carlos Ruiz",
                "especialidad": "Cardiología",
                "cedula": "2345678",
                "telefono": "55 3333 4444",
                "correo": "carlos@vidasana.mx",
                "horario": "Lun-Vie 10:00-16:00",
                "estado": "Activo",
                "fecha_registro": datetime.now()
            },
            {
                "nombre": "Dra. Sofía Torres",
                "especialidad": "Pediatría",
                "cedula": "3456789",
                "telefono": "55 5555 6666",
                "correo": "sofia@vidasana.mx",
                "horario": "Mar-Sáb 09:00-15:00",
                "estado": "Activo",
                "fecha_registro": datetime.now()
            }
        ])

    if enfermeria.count_documents({}) == 0:

        enfermeria.insert_many([
            {
                "nombre": "Elena Cruz",
                "turno": "Matutino",
                "area": "Urgencias",
                "telefono": "55 7777 8888",
                "estado": "Disponible",
                "fecha_registro": datetime.now()
            },
            {
                "nombre": "Miguel Flores",
                "turno": "Vespertino",
                "area": "Hospitalización",
                "telefono": "55 9999 0000",
                "estado": "Disponible",
                "fecha_registro": datetime.now()
            },
            {
                "nombre": "Patricia Luna",
                "turno": "Nocturno",
                "area": "Consulta externa",
                "telefono": "55 2222 3333",
                "estado": "Disponible",
                "fecha_registro": datetime.now()
            }
        ])

    flash(
        "Datos de prueba insertados correctamente.",
        "success"
    )

    return redirect(
        url_for("panel")
    )


crear_administrador()


if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )