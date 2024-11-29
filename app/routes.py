from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app import get_db_connection
from datetime import datetime

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return render_template("bienvenida.html", title="Home")

@main.route("/about")
def about():
    return render_template("about.html", title="About")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        dni = request.form.get("dni")

        # Consulta para verificar si el DNI existe en la vista
        query = "SELECT * FROM Vista_Entidad_Completa WHERE DNI = ?"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (dni,))
            user = cursor.fetchone()

        if user:
            # Redirigir al dashboard con el DNI del usuario
            return redirect(url_for('main.dashboard', dni=dni))
        else:
            return jsonify({"message": "DNI no encontrado"}), 404
    else:
        # Renderizar el formulario de login si es un método GET
        return render_template("login.html", title="Login")

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        tipo = request.args.get("tipo")
        if tipo == "jugador":
            equipos_query = "SELECT NroEquipo, nombre FROM Equipo"
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(equipos_query)
                equipos = cursor.fetchall()
                equipos_serializables = [{"id": equipo[0], "nombre": equipo[1]} for equipo in equipos]
            return jsonify(equipos_serializables)
        return render_template("login.html")

    elif request.method == "POST":
        data = request.form
        tipo = data.get("tipo")
        dni = data.get("dni")
        nombre = data.get("nombre")
        apellido = data.get("apellido")
        fecha_nacimiento = data.get("fecha_nacimiento")
        direccion = data.get("direccion")
        telefono = data.get("telefono")
        equipo_seleccionado = data.get("equipo")

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Validaciones para el tipo seleccionado
                if tipo == "jugador":
                    url_foto = data.get("url_foto")

                    # Obtener categoría del jugador
                    query_categoria = """
                        SELECT TOP 1 idCategoria
                        FROM Categoria
                        WHERE DATEDIFF(YEAR, ?, GETDATE()) BETWEEN Edad_minima AND Edad_maxima
                    """
                    cursor.execute(query_categoria, (fecha_nacimiento,))
                    categoria = cursor.fetchone()

                    if not categoria:
                        return jsonify({"error": "No se encontró una categoría adecuada para la edad"}), 400

                    id_categoria = categoria[0]

                    # Verificar que el equipo seleccionado pertenece a la misma categoría
                    query_equipo_categoria = """
                        SELECT idCategoria_perteneceFK
                        FROM Equipo
                        WHERE NroEquipo = ?
                    """
                    cursor.execute(query_equipo_categoria, (equipo_seleccionado,))
                    equipo_categoria = cursor.fetchone()

                    if not equipo_categoria or equipo_categoria[0] != id_categoria:
                        return jsonify({"error": "El equipo seleccionado no pertenece a la misma categoría que el jugador"}), 400

                elif tipo == "dt":
                    experiencia = data.get("experiencia")
                    if not experiencia:
                        return jsonify({"error": "Debe proporcionar experiencia para el director técnico"}), 400

                elif tipo == "encargado":
                    anios_experiencia = data.get("anios_experiencia")
                    if not anios_experiencia:
                        return jsonify({"error": "Debe proporcionar años de experiencia para el encargado"}), 400

                elif tipo == "arbitro":
                    nivel_experiencia = data.get("nivel_experiencia")
                    tiene_certificacion = data.get("tiene_certificacion")
                    tiene_certificacion = 1 if tiene_certificacion == "si" else 0  # Convertir a 0 o 1
                    if not nivel_experiencia:
                        return jsonify({"error": "Debe proporcionar nivel de experiencia para el árbitro"}), 400

                # Si las validaciones pasaron, realiza las inserciones
                query_persona = """
                    INSERT INTO Persona (DNI, Nombre, Apellido, FechaNacimiento)
                    VALUES (?, ?, ?, ?)
                """
                cursor.execute(query_persona, (dni, nombre, apellido, fecha_nacimiento))

                query_direccion = """
                    INSERT INTO Persona_Direccion (DNI_Persona, Direccion)
                    VALUES (?, ?)
                """
                cursor.execute(query_direccion, (dni, direccion))

                query_telefono = """
                    INSERT INTO PERSONA_TELEFONO (DNI_Persona, Telefono)
                    VALUES (?, ?)
                """
                cursor.execute(query_telefono, (dni, telefono))

                if tipo == "jugador":
                    query_jugador = """
                        INSERT INTO Jugador (DNI_Jugador, URL_Foto, idCategoria_perteneceFK, nroEquipo_pertenece)
                        VALUES (?, ?, ?, ?)
                    """
                    cursor.execute(query_jugador, (dni, url_foto, id_categoria, equipo_seleccionado))

                elif tipo == "dt":
                    query_dt = """
                        INSERT INTO DIRECTOR_TECNICO (DNI_DT, Experiencia)
                        VALUES (?, ?)
                    """
                    cursor.execute(query_dt, (dni, experiencia))

                elif tipo == "encargado":
                    query_encargado = """
                        INSERT INTO Encargado (DNI_ENCARGADO, AñosDeExperiencia)
                        VALUES (?, ?)
                    """
                    cursor.execute(query_encargado, (dni, anios_experiencia))

                elif tipo == "arbitro":
                    query_arbitro = """
                        INSERT INTO Arbitro (DNI_Arbitro, NivelExperiencia, TieneCertificacion)
                        VALUES (?, ?, ?)
                    """
                    cursor.execute(query_arbitro, (dni, nivel_experiencia, tiene_certificacion))
                    
                conn.commit()

            return jsonify({"success": "Usuario registrado exitosamente"}), 200

        except Exception as e:
            print(f"Error al registrar usuario: {e}")
            return jsonify({"error": "Ocurrió un error al registrar el usuario"}), 500


 

@main.route("/dashboard/<dni>")
def dashboard(dni):
    query = """
        SELECT *
        FROM Vista_Entidad_Completa
        WHERE DNI = ?
    """
    
    categorias_query = "SELECT idCategoria, Nombre FROM Categoria"
    divisiones_query = "SELECT codigoDiv, nombreDivision FROM Division"
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (dni,))
        user = cursor.fetchone()

        cursor.execute(categorias_query)
        categorias = [{"id": row[0], "nombre": row[1]} for row in cursor.fetchall()]

        cursor.execute(divisiones_query)
        divisiones = [{"codigoDiv": row[0], "nombreDivision": row[1]} for row in cursor.fetchall()]
        
    if user:
        # Extraer la fecha de nacimiento
        fecha_nacimiento = user[3]  # Asegúrate de que el índice 3 es FechaNacimiento
        edad = None
        if fecha_nacimiento:  # Verifica que no sea NULL
            if isinstance(fecha_nacimiento, datetime):
                # La base de datos ya devuelve un objeto datetime
                edad = datetime.now().year - fecha_nacimiento.year
                if (datetime.now().month, datetime.now().day) < (fecha_nacimiento.month, fecha_nacimiento.day):
                    edad -= 1
            else:
                # Si la base de datos devuelve una cadena, conviértela primero
                fecha_nacimiento = datetime.strptime(fecha_nacimiento.split(' ')[0], "%Y-%m-%d")
                edad = datetime.now().year - fecha_nacimiento.year
                if (datetime.now().month, datetime.now().day) < (fecha_nacimiento.month, fecha_nacimiento.day):
                    edad -= 1

        return render_template(
            "dashboard.html",
            user=user,
            categorias=categorias,
            divisiones=divisiones,
            edad=edad,  # Pasa la edad calculada al frontend
            title="Dashboard"
        )
    else:
        return "Usuario no encontrado", 404
    
@main.route("/crear_equipo", methods=["POST"])
def crear_equipo():
    data = request.form
    nombre_equipo = data.get("nombreEquipo")
    categoria_id = data.get("categoria")
    division_id = data.get("division")
    dni_director = data.get("dni_director")


    # Consulta para verificar si el director técnico ya tiene un equipo asignado
    check_equipo_query = """
        SELECT NroEquipo
        FROM Equipo
        WHERE DNI_DT_DIRIGE_FK = ?
    """

    query = """
        INSERT INTO Equipo (nombre, DNI_DT_DIRIGE_FK, idCategoria_perteneceFK, codigoDiv_perteneceFK)
        VALUES (?, ?, ?, ?)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
        # Verificar si ya dirige un equipo
            cursor.execute(check_equipo_query, (dni_director,))
            equipo_existente = cursor.fetchone()
        
            if equipo_existente:
                    return jsonify({"error": "El director técnico ya tiene un equipo asignado"}), 400
        
            cursor.execute(query, (nombre_equipo, dni_director, categoria_id, division_id))
            conn.commit()

            return jsonify({"success": "Equipo creado exitosamente"}), 200

    except Exception as e:
            print(f"Error al crear equipo: {e}")
            return jsonify({"error": "Ocurrió un error al crear el equipo"}), 500