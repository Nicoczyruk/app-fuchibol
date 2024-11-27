from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app import get_db_connection


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
            return jsonify({
                "message": "Login exitoso",
                "user": {
                    "DNI": user[0],
                    "Nombre": user[1],
                    "Tipo": user[2]  # Asegúrate de que esto coincida con los índices de tu vista
                }
            })
        else:
            return jsonify({"message": "DNI no encontrado"}), 404
    else:
        # Renderizar el formulario de login si es un método GET
        return render_template("login.html", title="Login")

@main.route('/register', methods=['POST'])
def register():
    data = request.form
    tipo = data.get('tipo')

    dni = data.get('dni')
    nombre = data.get('nombre')
    apellido = data.get('apellido')
    fecha_nacimiento = data.get('fecha_nacimiento')
    direccion = data.get('direccion')
    telefono = data.get('telefono')

    # Inicializamos los campos que pueden ser NULL
    nroEquipo_pertenece = None  
    idTorneo_inscribe = None  
    idTorneo_inscribeEquip = None  

    if tipo == 'jugador':
        nro_socio = data.get('nro_socio')
        url_foto = data.get('url_foto')
        
    elif tipo == 'dt':
        experiencia = data.get('experiencia')
        
    elif tipo == 'encargado':
        anios_experiencia = data.get('anios_experiencia')
    elif tipo == 'arbitro':
        nivel_experiencia = data.get('nivel_experiencia')
        tiene_certificacion = data.get('tiene_certificacion')

    # Insertar en la tabla Persona
    query_persona = """
        INSERT INTO Persona (DNI, Nombre, Apellido, FechaNacimiento)
        VALUES (?, ?, ?, ?)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query_persona, (dni, nombre, apellido, fecha_nacimiento))

    # Insertar en la tabla Persona_Direccion
    query_direccion = """
        INSERT INTO Persona_Direccion (DNI_Persona, Direccion)
        VALUES (?, ?)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query_direccion, (dni, direccion))

    # Insertar en la tabla Persona_Telefono
    query_telefono = """
        INSERT INTO PERSONA_TELEFONO (DNI_Persona, Telefono)
        VALUES (?, ?)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query_telefono, (dni, telefono))

    # Insertar en la tabla específica del tipo de usuario
    if tipo == 'jugador':
        query_jugador = """
            INSERT INTO Jugador (DNI_Jugador, NroSocio, URL_Foto, nroEquipo_pertenece, idTorneo_inscribe)
            VALUES (?, ?, ?, ?, ?)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query_jugador, (dni, nro_socio, url_foto, nroEquipo_pertenece, idTorneo_inscribe))
    
    elif tipo == 'dt':
        query_dt = """
            INSERT INTO DIRECTOR_TECNICO (DNI_DT, Experiencia, idTorneo_inscribeEquip)
            VALUES (?, ?, ?)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query_dt, (dni, experiencia, idTorneo_inscribeEquip))
    
    elif tipo == 'encargado':
        query_encargado = """
            INSERT INTO ENCARGADO (DNI_ENCARGADO, AñosDeExperiencia)
            VALUES (?, ?)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query_encargado, (dni, anios_experiencia))
    
    elif tipo == 'arbitro':
        tiene_certificacion = data.get('tiene_certificacion')
        
        # Convertir el valor 'no' o 'yes' a 0 o 1 para el campo bit
        tiene_certificacion = 1 if tiene_certificacion == 'yes' else 0
        
        query_arbitro = """
            INSERT INTO ARBITRO (DNI_Arbitro, NivelExperiencia, TieneCertificacion)
            VALUES (?, ?, ?)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query_arbitro, (dni, nivel_experiencia, tiene_certificacion))

    # Confirmar los cambios en la base de datos
    with get_db_connection() as conn:
        conn.commit()

    return redirect(url_for('main.login'))  # Redirige al login
