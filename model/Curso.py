class Curso:
    # Constructor de la clase Curso, que inicializa los atributos del curso.
    def __init__(self, idcurso, nombre, descripcion, precio_hora, tipo_curso):
        self.idcurso = idcurso
        self.nombre = nombre
        self.descripcion = descripcion
        self.precio_hora = precio_hora
        self.tipo_curso = tipo_curso
    # Método para representar el objeto Curso como una cadena de texto.
    def __str__(self):
        return f"Curso(ID: {self.idcurso}, Nombre: {self.nombre}, Descripción: {self.descripcion}, Precio por Hora: {self.precio_hora}, Tipo de Curso: {self.tipo_curso})"