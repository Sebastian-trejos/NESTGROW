from django.db import migrations


TIENDA_ITEMS = [
    {"pk": 1,  "nombre": "Mesa de Noche",          "descripcion": "Una mesita de madera con cajones para tus cosas.",          "categoria": "mueble",      "costo_huesos": 35, "icono": "🪵", "posicion_x": 15, "posicion_y": 30},
    {"pk": 2,  "nombre": "Librero de Madera",       "descripcion": "Un estante para tus libros favoritos.",                     "categoria": "mueble",      "costo_huesos": 40, "icono": "📚", "posicion_x": 75, "posicion_y": 30},
    {"pk": 3,  "nombre": "Lampara de Estrellas",    "descripcion": "Ilumina tu cuarto con estrellas azules.",                   "categoria": "electronico", "costo_huesos": 30, "icono": "⭐", "posicion_x": 60, "posicion_y": 70},
    {"pk": 4,  "nombre": "Cohete Espacial",         "descripcion": "Despega hacia las estrellas desde tu habitacion.",          "categoria": "decoracion",  "costo_huesos": 45, "icono": "🚀", "posicion_x": 50, "posicion_y": 60},
    {"pk": 5,  "nombre": "Cuadro Nube Feliz",       "descripcion": "Un cuadro con una nube sonriente para tu pared.",           "categoria": "decoracion",  "costo_huesos": 20, "icono": "☁️", "posicion_x": 20, "posicion_y": 80},
    {"pk": 6,  "nombre": "Cuadro de Cohete",        "descripcion": "Cuadro espacial con un cohete entre estrellas.",            "categoria": "decoracion",  "costo_huesos": 20, "icono": "🖼️", "posicion_x": 35, "posicion_y": 80},
    {"pk": 7,  "nombre": "Suculenta Dorada",        "descripcion": "Una pequena planta suculenta en maceta dorada.",            "categoria": "planta",      "costo_huesos": 15, "icono": "🌿", "posicion_x": 85, "posicion_y": 20},
    {"pk": 8,  "nombre": "Planta Grande",           "descripcion": "Una planta frondosa que llena de vida tu cuarto.",          "categoria": "planta",      "costo_huesos": 25, "icono": "🌱", "posicion_x": 10, "posicion_y": 20},
    {"pk": 9,  "nombre": "Suculenta Verde",         "descripcion": "Suculenta verde brillante en maceta esmeralda.",            "categoria": "planta",      "costo_huesos": 20, "icono": "🪴", "posicion_x": 90, "posicion_y": 20},
    {"pk": 10, "nombre": "Caballito de Madera",     "descripcion": "Un caballito balancin de madera para tu habitacion.",       "categoria": "mueble",      "costo_huesos": 55, "icono": "🐴", "posicion_x": 30, "posicion_y": 20},
    {"pk": 11, "nombre": "Carrito de Juguete",      "descripcion": "Un carrito verde de juguete listo para rodar.",             "categoria": "decoracion",  "costo_huesos": 30, "icono": "🚗", "posicion_x": 55, "posicion_y": 20},
    {"pk": 12, "nombre": "Dragon de Peluche",       "descripcion": "Un dragon verde de peluche, suave y amigable.",             "categoria": "decoracion",  "costo_huesos": 40, "icono": "🐲", "posicion_x": 70, "posicion_y": 20},
    {"pk": 13, "nombre": "Tambor de Juguete",       "descripcion": "Haz musica con tu propio tambor de colores.",               "categoria": "decoracion",  "costo_huesos": 35, "icono": "🥁", "posicion_x": 45, "posicion_y": 20},
    {"pk": 14, "nombre": "Xilofono de Colores",     "descripcion": "Toca melodias con este xilofono de arcoiris.",              "categoria": "decoracion",  "costo_huesos": 40, "icono": "🎵", "posicion_x": 25, "posicion_y": 20},
    {"pk": 15, "nombre": "Repisa de Madera",        "descripcion": "Repisa flotante de madera natural para tu pared.",          "categoria": "mueble",      "costo_huesos": 30, "icono": "🪵", "posicion_x": 65, "posicion_y": 80},
    {"pk": 16, "nombre": "Bloque de Letras",        "descripcion": "Bloque educativo con letras y figuras de colores.",         "categoria": "decoracion",  "costo_huesos": 20, "icono": "🔤", "posicion_x": 40, "posicion_y": 20},
    {"pk": 17, "nombre": "Cojin Estrella",          "descripcion": "Cojin con forma de estrella feliz para descansar.",         "categoria": "mueble",      "costo_huesos": 25, "icono": "⭐", "posicion_x": 50, "posicion_y": 10},
    {"pk": 18, "nombre": "Pelota de Playa",         "descripcion": "Pelota colorida para jugar dentro de casa.",                "categoria": "decoracion",  "costo_huesos": 20, "icono": "⚽", "posicion_x": 60, "posicion_y": 10},
    {"pk": 19, "nombre": "Guirnalda de Colores",    "descripcion": "Banderines de colores para decorar tu habitacion.",         "categoria": "decoracion",  "costo_huesos": 25, "icono": "🎏", "posicion_x": 50, "posicion_y": 90},
    {"pk": 20, "nombre": "Carpa de Juegos",         "descripcion": "Una pequena carpa tipi para tus aventuras en casa.",        "categoria": "mueble",      "costo_huesos": 65, "icono": "⛺", "posicion_x": 20, "posicion_y": 30},
    {"pk": 21, "nombre": "Tren de Juguete",         "descripcion": "Locomotora de madera lista para su viaje.",                 "categoria": "decoracion",  "costo_huesos": 50, "icono": "🚂", "posicion_x": 75, "posicion_y": 20},
    {"pk": 22, "nombre": "Pila de Libros",          "descripcion": "Una pila de libros coloridos para aprender mas.",           "categoria": "decoracion",  "costo_huesos": 30, "icono": "📖", "posicion_x": 80, "posicion_y": 20},
    {"pk": 23, "nombre": "Familia de Munequitos",   "descripcion": "Familia de munequitos de madera.",                          "categoria": "decoracion",  "costo_huesos": 35, "icono": "🪆", "posicion_x": 35, "posicion_y": 20},
    {"pk": 24, "nombre": "Caja de Bloques",         "descripcion": "Caja morada llena de bloques de construccion.",             "categoria": "decoracion",  "costo_huesos": 30, "icono": "🧱", "posicion_x": 45, "posicion_y": 10},
    {"pk": 25, "nombre": "Oso de Peluche",          "descripcion": "Un osito de peluche marron con mono rojo.",                 "categoria": "decoracion",  "costo_huesos": 35, "icono": "🧸", "posicion_x": 55, "posicion_y": 20},
    {"pk": 26, "nombre": "Escritorio de Estudio",   "descripcion": "Escritorio con libros y lapices para estudiar.",            "categoria": "mueble",      "costo_huesos": 70, "icono": "🖥️", "posicion_x": 65, "posicion_y": 40},
    {"pk": 27, "nombre": "Portalapices",            "descripcion": "Portalapices turquesa lleno de crayones de colores.",       "categoria": "decoracion",  "costo_huesos": 20, "icono": "✏️", "posicion_x": 30, "posicion_y": 60},
    {"pk": 28, "nombre": "Barco Puzzle",            "descripcion": "Un barco de juguete con piezas de puzzle para armar.",      "categoria": "decoracion",  "costo_huesos": 40, "icono": "⛵", "posicion_x": 70, "posicion_y": 10},
]


def populate_tienda(apps, schema_editor):
    TiendaItem = apps.get_model('games', 'TiendaItem')
    for data in TIENDA_ITEMS:
        TiendaItem.objects.get_or_create(
            pk=data['pk'],
            defaults={
                'nombre':       data['nombre'],
                'descripcion':  data['descripcion'],
                'categoria':    data['categoria'],
                'costo_huesos': data['costo_huesos'],
                'icono':        data['icono'],
                'posicion_x':   data['posicion_x'],
                'posicion_y':   data['posicion_y'],
                'juego_entretenimiento': 'ninguno',
                'is_active':    True,
                'order':        data['pk'],
            }
        )


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0016_remove_quiz_ordenar_letras'),
    ]

    operations = [
        migrations.RunPython(populate_tienda, migrations.RunPython.noop),
    ]
