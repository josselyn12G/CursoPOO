import json
import pyodbc
from model.Curso import Curso


# Clase encargada de gestionar todas las operaciones CRUD de Cursos.
class GestorCursos:

    # Constructor de la clase.
    def __init__(self):
        try:
            # Se abre y lee el archivo config.json.
            with open("config.json", "r") as archivo_config:
                config = json.load(archivo_config)

            # Se obtienen los datos de configuración.
            name_server = config["nameServer"]
            database = config["database"]
            username = config["username"]
            password = config["password"]
            controlador_odbc = config["controladorODBC"]

            # Se construye la cadena de conexión.
            self.connection_string = f'DRIVER={controlador_odbc};SERVER={name_server};DATABASE={database};UID={username};PWD={password}'

            # Se establece la conexión con SQL Server.
            self.conexion = pyodbc.connect(self.connection_string)

            # Mensaje de conexión exitosa.
            print("\nConexión exitosa a la base de datos.\n")

        # Manejo de errores relacionados con la base de datos.
        except pyodbc.Error as e:
            print("\nError de conexión o de base de datos:")
            print(e)
            self.conexion = None

        # Manejo de cualquier otro error inesperado.
        except Exception as e:
            print("\nError inesperado:")
            print(e)
            self.conexion = None

    # Método para solicitar un texto obligatorio.
    def pedir_texto_obligatorio(self, mensaje, max_longitud=None):
        while True:
            # Se solicita el valor y se eliminan espacios innecesarios.
            valor = input(mensaje).strip()

            # Validación de campo vacío.
            if valor == "":
                print("Error: este campo es obligatorio y no puede estar vacío.")

            # Validación de longitud máxima.
            elif max_longitud and len(valor) > max_longitud:
                print(f"Error: el texto no puede superar {max_longitud} caracteres.")

            # Si todo es correcto, retorna el valor.
            else:
                return valor

    # Método para solicitar un número entero obligatorio.
    def pedir_entero_obligatorio(self, mensaje):
        while True:
            try:
                # Conversión del dato ingresado a entero.
                valor = int(input(mensaje).strip())

                # Validación de número positivo.
                if valor <= 0:
                    print("Error: el ID debe ser un número entero positivo.")
                else:
                    return valor

            # Manejo de error si el valor no es entero.
            except ValueError:
                print("Error: debe ingresar un número entero válido.")

    # Método para solicitar un número decimal obligatorio.
    def pedir_decimal_obligatorio(self, mensaje):
        while True:
            try:
                # Conversión del dato ingresado a decimal.
                valor = float(input(mensaje).strip())

                # Validación de valor positivo.
                if valor <= 0:
                    print("Error: el valor debe ser mayor a cero.")
                else:
                    return valor

            # Manejo de error si el valor no es decimal.
            except ValueError:
                print("Error: debe ingresar un número decimal válido.")

    # Método para insertar un nuevo curso.
    def insertar_registro(self):
        try:
            print("\n\tINSERTAR CURSO\n")

            # Se solicitan los datos del curso.
            idcurso = self.pedir_entero_obligatorio("Ingrese ID del curso: ")
            nombre = self.pedir_texto_obligatorio("Ingrese nombre del curso: ", max_longitud=255)
            descripcion = self.pedir_texto_obligatorio("Ingrese descripción: ", max_longitud=500)
            precio_hora = self.pedir_decimal_obligatorio("Ingrese precio por hora: ")
            tipo_curso = self.pedir_texto_obligatorio("Ingrese tipo de curso: ", max_longitud=50)

            # Se crea el objeto Curso.
            curso = Curso(idcurso, nombre, descripcion, precio_hora, tipo_curso)

            # Se crea el cursor para ejecutar consultas SQL.
            cursor = self.conexion.cursor()

            # Consulta para verificar si el ID ya existe.
            cursor.execute("SELECT COUNT(*) FROM Cursos WHERE IDCurso = ?", (curso.idcurso,))
            existe = cursor.fetchone()[0]

            # Validación de curso duplicado.
            if existe > 0:
                print("\nError: ya existe un curso registrado con ese ID.")
                return

            # Consulta SQL para insertar el curso.
            sql = """
                INSERT INTO Cursos 
                (IDCurso, NombreCurso, Descripcion, PrecioxHora, TipoCurso)
                VALUES (?, ?, ?, ?, ?)
            """

            # Ejecución de la consulta.
            cursor.execute(sql, (
                curso.idcurso,
                curso.nombre,
                curso.descripcion,
                curso.precio_hora,
                curso.tipo_curso
            ))

            # Confirmación de cambios en la base de datos.
            self.conexion.commit()

            # Mensaje de éxito.
            print("\nCurso insertado correctamente.")

        # Manejo de errores de integridad.
        except pyodbc.IntegrityError as e:
            print("\nError de integridad: no se pudo insertar el curso.")
            print("Detalle:", e)

        # Manejo de cualquier otro error.
        except Exception as e:
            self.conexion.rollback()
            print("\nError al insertar:", e)

    # Método para consultar todos los cursos.
    def consultar_registros(self):
        try:
            print("\n\tLISTA DE CURSOS\n")

            # Se crea el cursor.
            cursor = self.conexion.cursor()

            # Consulta SQL para obtener los cursos.
            sql = """
                SELECT IDCurso, NombreCurso, Descripcion, PrecioxHora, TipoCurso
                FROM Cursos
            """

            # Ejecución de la consulta.
            cursor.execute(sql)

            # Obtención de registros.
            registros = cursor.fetchall()

            # Encabezado de la tabla.
            print("-" * 100)
            print(f"{'ID':<5} {'NOMBRE':<25} {'DESCRIPCIÓN':<30} {'PRECIO/HORA':>12} {'TIPO':<15}")
            print("-" * 100)

            # Validación de registros existentes.
            if len(registros) == 0:
                print("No existen cursos registrados.")
            else:
                # Recorrido de registros.
                for r in registros:
                    print(
                        f"{r.IDCurso:<5} "
                        f"{r.NombreCurso:<25} "
                        f"{str(r.Descripcion):<30} "
                        f"{float(r.PrecioxHora):>12.2f} "
                        f"{r.TipoCurso:<15}"
                    )

            # Pie de tabla.
            print("-" * 100)
            print(f"Total de registros: {len(registros)}\n")

        # Manejo de errores.
        except Exception as e:
            print("\nError al consultar:", e)

    # Método para actualizar un curso.
    def actualizar_registro(self):
        try:
            print("\n\tACTUALIZAR CURSO\n")

            # Solicitud del ID del curso.
            idcurso = self.pedir_entero_obligatorio("Ingrese ID del curso a actualizar: ")

            # Creación del cursor.
            cursor = self.conexion.cursor()

            # Consulta para buscar el curso.
            sql_buscar = """
                SELECT IDCurso, NombreCurso, Descripcion, PrecioxHora, TipoCurso
                FROM Cursos
                WHERE IDCurso = ?
            """

            # Ejecución de consulta.
            cursor.execute(sql_buscar, (idcurso,))
            curso_encontrado = cursor.fetchone()

            # Validación si el curso no existe.
            if curso_encontrado is None:
                print("\nError: no existe un curso con el ID ingresado.")
                return

            # Muestra de información actual.
            print("\nCurso encontrado:")
            print(f"ID: {curso_encontrado.IDCurso}")
            print(f"Nombre actual: {curso_encontrado.NombreCurso}")
            print(f"Descripción actual: {curso_encontrado.Descripcion}")
            print(f"Precio actual: {curso_encontrado.PrecioxHora}")
            print(f"Tipo actual: {curso_encontrado.TipoCurso}")

            # Solicitud de nuevos datos.
            nombre = self.pedir_texto_obligatorio("\nNuevo nombre: ", max_longitud=255)
            descripcion = self.pedir_texto_obligatorio("Nueva descripción: ", max_longitud=500)
            precio_hora = self.pedir_decimal_obligatorio("Nuevo precio por hora: ")
            tipo_curso = self.pedir_texto_obligatorio("Nuevo tipo de curso: ", max_longitud=50)

            # Creación del objeto actualizado.
            curso = Curso(idcurso, nombre, descripcion, precio_hora, tipo_curso)

            # Consulta SQL para actualizar.
            sql_actualizar = """
                UPDATE Cursos
                SET NombreCurso = ?, 
                    Descripcion = ?, 
                    PrecioxHora = ?, 
                    TipoCurso = ?
                WHERE IDCurso = ?
            """

            # Ejecución de actualización.
            cursor.execute(sql_actualizar, (
                curso.nombre,
                curso.descripcion,
                curso.precio_hora,
                curso.tipo_curso,
                curso.idcurso
            ))

            # Confirmación de cambios.
            self.conexion.commit()

            # Mensaje de éxito.
            print("\nCurso actualizado correctamente.")

        # Manejo de errores.
        except Exception as e:
            self.conexion.rollback()
            print("\nError al actualizar:", e)

    # Método para eliminar un curso.
    def eliminar_registro(self):
        try:
            print("\n\tELIMINAR CURSO\n")

            # Solicitud del ID del curso.
            idcurso = self.pedir_entero_obligatorio("Ingrese ID del curso a eliminar: ")

            # Creación del cursor.
            cursor = self.conexion.cursor()

            # Consulta SQL de eliminación.
            sql = "DELETE FROM Cursos WHERE IDCurso = ?"

            # Ejecución de eliminación.
            cursor.execute(sql, (idcurso,))

            # Validación si el curso no existe.
            if cursor.rowcount == 0:
                print("\nError: no existe un curso con el ID ingresado.")
                return

            # Confirmación de cambios.
            self.conexion.commit()

            # Mensaje de éxito.
            print("\nCurso eliminado correctamente.")

        # Manejo de errores de integridad.
        except pyodbc.IntegrityError as e:
            self.conexion.rollback()

            mensaje_error = str(e)

            # Validación de restricciones por claves foráneas.
            if "547" in mensaje_error:
                print("\nError: no se puede eliminar el curso porque tiene registros relacionados en otra tabla.")
                print("Debe eliminar primero los registros dependientes o revisar las relaciones de clave foránea.")
            else:
                print("\nError de integridad al eliminar el curso.")
                print("Detalle:", e)

        # Manejo de otros errores.
        except Exception as e:
            self.conexion.rollback()
            print("\nError al eliminar:", e)

    # Método para mostrar las opciones del menú CRUD.
    def mostrar_opciones_crud(self):
        print("\n\t----------------------------")
        print("\t   SISTEMA CRUD CURSOS")
        print("\t----------------------------")
        print("\t1. Crear curso")
        print("\t2. Consultar cursos")
        print("\t3. Actualizar curso")
        print("\t4. Eliminar curso")
        print("\t5. Salir\n")

    # Método principal que ejecuta el menú.
    def ejecutar_menu(self):

        # Validación de conexión.
        if self.conexion is None:
            print("No se puede ejecutar el sistema porque no hay conexión a la base de datos.")
            return

        try:
            # Bucle infinito del menú.
            while True:

                # Mostrar menú.
                self.mostrar_opciones_crud()

                # Solicitar opción.
                opcion = input("Seleccione una opción (1-5): ").strip()

                # Validación de opciones.
                if opcion == "1":
                    self.insertar_registro()

                elif opcion == "2":
                    self.consultar_registros()

                elif opcion == "3":
                    self.actualizar_registro()

                elif opcion == "4":
                    self.eliminar_registro()

                elif opcion == "5":
                    print("\nSaliendo del programa...")
                    break

                else:
                    print("Opción inválida. Debe seleccionar una opción entre 1 y 5.")

        # Finalmente se cierra la conexión.
        finally:
            self.cerrar_conexion()

    # Método para cerrar la conexión con la base de datos.
    def cerrar_conexion(self):

        # Validación de conexión activa.
        if self.conexion is not None:

            # Cierre de conexión.
            self.conexion.close()

            # Mensaje de cierre.
            print("\nConexión cerrada.")