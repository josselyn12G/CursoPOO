import json
import pyodbc
from model.Curso import Curso


class GestorCursos:
    def __init__(self):
        try:
            with open("config.json", "r") as archivo_config:
                config = json.load(archivo_config)

            name_server = config["nameServer"]
            database = config["database"]
            username = config["username"]
            password = config["password"]
            controlador_odbc = config["controladorODBC"]

            self.connection_string = f'DRIVER={controlador_odbc};SERVER={name_server};DATABASE={database};UID={username};PWD={password}'


            self.conexion = pyodbc.connect(self.connection_string)
            print("\nConexión exitosa a la base de datos.\n")

        except pyodbc.Error as e:
            print("\nError de conexión o de base de datos:")
            print(e)
            self.conexion = None

        except Exception as e:
            print("\nError inesperado:")
            print(e)
            self.conexion = None

    def pedir_texto_obligatorio(self, mensaje, max_longitud=None):
        while True:
            valor = input(mensaje).strip()

            if valor == "":
                print("Error: este campo es obligatorio y no puede estar vacío.")
            elif max_longitud and len(valor) > max_longitud:
                print(f"Error: el texto no puede superar {max_longitud} caracteres.")
            else:
                return valor

    def pedir_entero_obligatorio(self, mensaje):
        while True:
            try:
                valor = int(input(mensaje).strip())

                if valor <= 0:
                    print("Error: el ID debe ser un número entero positivo.")
                else:
                    return valor

            except ValueError:
                print("Error: debe ingresar un número entero válido.")

    def pedir_decimal_obligatorio(self, mensaje):
        while True:
            try:
                valor = float(input(mensaje).strip())

                if valor <= 0:
                    print("Error: el valor debe ser mayor a cero.")
                else:
                    return valor

            except ValueError:
                print("Error: debe ingresar un número decimal válido.")

    def insertar_registro(self):
        try:
            print("\n\tINSERTAR CURSO\n")

            idcurso = self.pedir_entero_obligatorio("Ingrese ID del curso: ")
            nombre = self.pedir_texto_obligatorio("Ingrese nombre del curso: ", max_longitud=255)
            descripcion = self.pedir_texto_obligatorio("Ingrese descripción: ", max_longitud=500)
            precio_hora = self.pedir_decimal_obligatorio("Ingrese precio por hora: ")
            tipo_curso = self.pedir_texto_obligatorio("Ingrese tipo de curso: ", max_longitud=50)

            curso = Curso(idcurso, nombre, descripcion, precio_hora, tipo_curso)

            cursor = self.conexion.cursor()

            cursor.execute("SELECT COUNT(*) FROM Cursos WHERE IDCurso = ?", (curso.idcurso,))
            existe = cursor.fetchone()[0]

            if existe > 0:
                print("\nError: ya existe un curso registrado con ese ID.")
                return

            sql = """
                INSERT INTO Cursos 
                (IDCurso, NombreCurso, Descripcion, PrecioxHora, TipoCurso)
                VALUES (?, ?, ?, ?, ?)
            """

            cursor.execute(sql, (
                curso.idcurso,
                curso.nombre,
                curso.descripcion,
                curso.precio_hora,
                curso.tipo_curso
            ))

            self.conexion.commit()
            print("\nCurso insertado correctamente.")

        except pyodbc.IntegrityError as e:
            print("\nError de integridad: no se pudo insertar el curso.")
            print("Detalle:", e)

        except Exception as e:
            self.conexion.rollback()
            print("\nError al insertar:", e)

    def consultar_registros(self):
        try:
            print("\n\tLISTA DE CURSOS\n")

            cursor = self.conexion.cursor()

            sql = """
                SELECT IDCurso, NombreCurso, Descripcion, PrecioxHora, TipoCurso
                FROM Cursos
            """

            cursor.execute(sql)
            registros = cursor.fetchall()

            print("-" * 100)
            print(f"{'ID':<5} {'NOMBRE':<25} {'DESCRIPCIÓN':<30} {'PRECIO/HORA':>12} {'TIPO':<15}")
            print("-" * 100)

            if len(registros) == 0:
                print("No existen cursos registrados.")
            else:
                for r in registros:
                    print(
                        f"{r.IDCurso:<5} "
                        f"{r.NombreCurso:<25} "
                        f"{str(r.Descripcion):<30} "
                        f"{float(r.PrecioxHora):>12.2f} "
                        f"{r.TipoCurso:<15}"
                    )

            print("-" * 100)
            print(f"Total de registros: {len(registros)}\n")

        except Exception as e:
            print("\nError al consultar:", e)

    def actualizar_registro(self):
        try:
            print("\n\tACTUALIZAR CURSO\n")

            idcurso = self.pedir_entero_obligatorio("Ingrese ID del curso a actualizar: ")

            cursor = self.conexion.cursor()

            sql_buscar = """
                SELECT IDCurso, NombreCurso, Descripcion, PrecioxHora, TipoCurso
                FROM Cursos
                WHERE IDCurso = ?
            """

            cursor.execute(sql_buscar, (idcurso,))
            curso_encontrado = cursor.fetchone()

            if curso_encontrado is None:
                print("\nError: no existe un curso con el ID ingresado.")
                return

            print("\nCurso encontrado:")
            print(f"ID: {curso_encontrado.IDCurso}")
            print(f"Nombre actual: {curso_encontrado.NombreCurso}")
            print(f"Descripción actual: {curso_encontrado.Descripcion}")
            print(f"Precio actual: {curso_encontrado.PrecioxHora}")
            print(f"Tipo actual: {curso_encontrado.TipoCurso}")

            nombre = self.pedir_texto_obligatorio("\nNuevo nombre: ", max_longitud=255)
            descripcion = self.pedir_texto_obligatorio("Nueva descripción: ", max_longitud=500)
            precio_hora = self.pedir_decimal_obligatorio("Nuevo precio por hora: ")
            tipo_curso = self.pedir_texto_obligatorio("Nuevo tipo de curso: ", max_longitud=50)

            curso = Curso(idcurso, nombre, descripcion, precio_hora, tipo_curso)

            sql_actualizar = """
                UPDATE Cursos
                SET NombreCurso = ?, 
                    Descripcion = ?, 
                    PrecioxHora = ?, 
                    TipoCurso = ?
                WHERE IDCurso = ?
            """

            cursor.execute(sql_actualizar, (
                curso.nombre,
                curso.descripcion,
                curso.precio_hora,
                curso.tipo_curso,
                curso.idcurso
            ))

            self.conexion.commit()
            print("\nCurso actualizado correctamente.")

        except Exception as e:
            self.conexion.rollback()
            print("\nError al actualizar:", e)

    def eliminar_registro(self):
        try:
            print("\n\tELIMINAR CURSO\n")

            idcurso = self.pedir_entero_obligatorio("Ingrese ID del curso a eliminar: ")

            cursor = self.conexion.cursor()

            sql = "DELETE FROM Cursos WHERE IDCurso = ?"

            cursor.execute(sql, (idcurso,))

            if cursor.rowcount == 0:
                print("\nError: no existe un curso con el ID ingresado.")
                return

            self.conexion.commit()
            print("\nCurso eliminado correctamente.")

        except pyodbc.IntegrityError as e:
            self.conexion.rollback()

            mensaje_error = str(e)

            if "547" in mensaje_error:
                print("\nError: no se puede eliminar el curso porque tiene registros relacionados en otra tabla.")
                print("Debe eliminar primero los registros dependientes o revisar las relaciones de clave foránea.")
            else:
                print("\nError de integridad al eliminar el curso.")
                print("Detalle:", e)

        except Exception as e:
            self.conexion.rollback()
            print("\nError al eliminar:", e)

    def mostrar_opciones_crud(self):
        print("\n\t----------------------------")
        print("\t   SISTEMA CRUD CURSOS")
        print("\t----------------------------")
        print("\t1. Crear curso")
        print("\t2. Consultar cursos")
        print("\t3. Actualizar curso")
        print("\t4. Eliminar curso")
        print("\t5. Salir\n")

    def ejecutar_menu(self):
        if self.conexion is None:
            print("No se puede ejecutar el sistema porque no hay conexión a la base de datos.")
            return

        try:
            while True:
                self.mostrar_opciones_crud()

                opcion = input("Seleccione una opción (1-5): ").strip()

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

        finally:
            self.cerrar_conexion()

    def cerrar_conexion(self):
        if self.conexion is not None:
            self.conexion.close()
            print("\nConexión cerrada.")