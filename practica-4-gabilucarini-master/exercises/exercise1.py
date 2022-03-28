"""
Se desea tener un sistema de notas para los alumnos. Cada alumno se registra
con un DNI, un Nombre y un listado de notas. Las notas tienen el nombre de la
materia y el valor númerico de la nota.
Se desea además, tener una base de datos sencilla en formato JSON.
Restricciones:
- Utilizar 2 dataclasses
- No utilizar métodos de instancia
- No utilizar métodos de clase
"""

from typing import List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from contextlib import contextmanager


@dataclass
class Nota:
    materia: str
    nota: int


@dataclass
class Estudiante:
    dni: str
    nombre: str
    notas: List[Nota]


DATABASE_PARAMS = {
    "storage": JSONStorage,
    "indent": 4,
    "separators": (",", ": ")
}


@contextmanager
def database_connection():
    db = TinyDB(f"{Path(__file__).parent}/db.json", **DATABASE_PARAMS)
    db.default_table_name = "estudiantes"

    try:
        yield db
    finally:
        db.close()


def insert_estudiante(estudiante: Estudiante) -> Estudiante:
    estudiantes_dict = asdict(estudiante)

    with database_connection() as db:
        db.insert(estudiantes_dict)

    return Estudiante(**estudiantes_dict)


def get_all() -> List[Estudiante]:
    with database_connection() as db:
        todos = db.all()
    estudiantes = []
    for diccionario_estudiante in todos:
        dni = diccionario_estudiante["dni"]
        nombre = diccionario_estudiante["nombre"]
        notas = [Nota(**notas) for notas in diccionario_estudiante["notas"]]
        estudiantes.append(Estudiante(dni=dni, nombre=nombre, notas=notas))
    return estudiantes


def get_by_dni(dni: str) -> Optional[Estudiante]:
    Estudiante_ = Query()

    with database_connection() as db:
        estudiantes_ = db.search(Estudiante_.dni == dni)
        if not estudiantes_:
            return None

        for diccionario_estudiante in estudiantes_:
            dni = diccionario_estudiante["dni"]
            nombre = diccionario_estudiante["nombre"]
            notas = \
                [Nota(**notas) for notas in diccionario_estudiante["notas"]]
        return Estudiante(dni=dni, nombre=nombre, notas=notas)


def delete_by_id(dni: str) -> None:
    Estudiante_ = Query()

    with database_connection() as db:
        db.remove(Estudiante_.dni == dni)


def update(estudiante: Estudiante) -> Estudiante:

    with database_connection() as db:
        db.update(asdict(estudiante))
    return estudiante


# NO MODIFICAR - INICIO
juan_programacion_1 = Nota("Programación 1", 6)
maria_programacion_1 = Nota("Programación 1", 8)
maria_programacion_2 = Nota("Programación 2", 6)
pedro_base_de_datos = Nota("Base de datos", 5)

init_data = [
    Estudiante("47526381", "Juan", [juan_programacion_1]),
    Estudiante("46193480", "María", [maria_programacion_1, maria_programacion_2]),
    Estudiante("43796248", "Pedro", [pedro_base_de_datos])
]

db = TinyDB(f"{Path(__file__).parent}/db.json", **DATABASE_PARAMS)
db.default_table_name = "estudiantes"
db.truncate()


for estudiante in init_data:
    insert_estudiante(estudiante)

todos = get_all()
print(init_data)
assert todos == init_data

juan = get_by_dni(dni="47526381")

print(juan)
print(init_data[0])

assert juan == init_data[0]


delete_by_id(juan.dni)

todos = get_all()

assert todos == init_data[1:]

maria = todos[0]

maria.notas = maria.notas + [Nota("Base de datos", 8)]

update(maria)

maria_actualizada = get_all()[0]
assert maria_actualizada == maria
# NO MODIFICAR - FIN
