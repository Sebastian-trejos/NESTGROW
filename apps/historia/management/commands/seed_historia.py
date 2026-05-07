from django.core.management.base import BaseCommand
from apps.historia.models import SeccionHistoria, Leccion, ActividadLeccion


SECCIONES = [
    {
        'titulo': 'Capítulo 1: Saludos y Presentaciones',
        'descripcion': 'Aprende a saludar y presentarte en inglés con Milo.',
        'orden': 1,
        'icono_emoji': '👋',
        'color_hex': '#6C63FF',
        'is_desbloqueada_por_defecto': True,
        'lecciones': [
            {
                'titulo': 'Hello! ¿Cómo te llamas?',
                'descripcion_corta': 'Saludos básicos y presentación personal',
                'orden': 1,
                'icono_emoji': '😊',
                'puntos_xp': 15,
                'huesos_recompensa': 3,
                'tiempo_estimado_minutos': 10,
                'actividades': [
                    {
                        'orden': 1,
                        'tipo': 'introduccion',
                        'puntos_actividad': 0,
                        'datos': {
                            'titulo': 'Bienvenido al inglés con Milo 🐺',
                            'texto': 'Milo te enseñará a saludar en inglés. ¡Es muy fácil! Primero aprende estas palabras clave.',
                            'palabras_clave': [
                                {'es': 'Hola', 'en': 'Hello / Hi'},
                                {'es': 'Me llamo', 'en': 'My name is'},
                                {'es': 'Mucho gusto', 'en': 'Nice to meet you'},
                                {'es': 'Adiós', 'en': 'Goodbye / Bye'},
                            ],
                        },
                    },
                    {
                        'orden': 2,
                        'tipo': 'vocabulario',
                        'puntos_actividad': 1,
                        'datos': {
                            'titulo': 'Palabras de saludo',
                            'tarjetas': [
                                {'es': 'Hola',        'en': 'Hello',        'emoji': '👋'},
                                {'es': 'Buenos días', 'en': 'Good morning', 'emoji': '🌅'},
                                {'es': 'Buenas tardes','en': 'Good afternoon','emoji': '☀️'},
                                {'es': 'Buenas noches','en': 'Good evening', 'emoji': '🌙'},
                                {'es': 'Adiós',       'en': 'Goodbye',      'emoji': '👋'},
                                {'es': 'Hasta luego', 'en': 'See you later', 'emoji': '😊'},
                            ],
                        },
                    },
                    {
                        'orden': 3,
                        'tipo': 'dialogo',
                        'puntos_actividad': 0,
                        'datos': {
                            'titulo': 'Milo se presenta',
                            'lineas': [
                                {'personaje': 'Milo',    'avatar': '🐺', 'texto': 'Hello! My name is Milo. What is your name?'},
                                {'personaje': 'Tú',      'avatar': '🎒', 'texto': 'Hi Milo! My name is Carlos. Nice to meet you!'},
                                {'personaje': 'Milo',    'avatar': '🐺', 'texto': 'Nice to meet you too, Carlos! How are you?'},
                                {'personaje': 'Tú',      'avatar': '🎒', 'texto': 'I am fine, thank you! And you?'},
                                {'personaje': 'Milo',    'avatar': '🐺', 'texto': 'I am great! Let\'s learn English together!'},
                            ],
                        },
                    },
                    {
                        'orden': 4,
                        'tipo': 'listening',
                        'puntos_actividad': 2,
                        'datos': {
                            'titulo': '¿Qué escuchas?',
                            'instruccion': 'Presiona el botón 🔊 y selecciona lo que escuchas en español.',
                            'preguntas': [
                                {
                                    'audio_texto': 'Hello',
                                    'opciones': ['Hola', 'Adiós', 'Gracias', 'Por favor'],
                                    'respuesta_correcta': 'Hola',
                                },
                                {
                                    'audio_texto': 'Good morning',
                                    'opciones': ['Buenas noches', 'Buenas tardes', 'Buenos días', 'Hasta luego'],
                                    'respuesta_correcta': 'Buenos días',
                                },
                                {
                                    'audio_texto': 'Goodbye',
                                    'opciones': ['Hola', 'Adiós', 'Por favor', 'Gracias'],
                                    'respuesta_correcta': 'Adiós',
                                },
                            ],
                        },
                    },
                    {
                        'orden': 5,
                        'tipo': 'pronunciacion',
                        'puntos_actividad': 1,
                        'datos': {
                            'titulo': 'Practica la pronunciación',
                            'palabras': [
                                {'en': 'Hello',     'es': 'Hola'},
                                {'en': 'Goodbye',   'es': 'Adiós'},
                                {'en': 'My name is','es': 'Me llamo'},
                                {'en': 'Thank you', 'es': 'Gracias'},
                            ],
                        },
                    },
                ],
            },
            {
                'titulo': 'How are you? Los sentimientos',
                'descripcion_corta': 'Aprende a expresar cómo te sientes',
                'orden': 2,
                'icono_emoji': '🎭',
                'puntos_xp': 20,
                'huesos_recompensa': 4,
                'tiempo_estimado_minutos': 12,
                'actividades': [
                    {
                        'orden': 1,
                        'tipo': 'introduccion',
                        'puntos_actividad': 0,
                        'datos': {
                            'titulo': '¿Cómo te sientes hoy?',
                            'texto': 'En inglés puedes expresar tus sentimientos de muchas formas. Milo te enseña las más importantes.',
                            'palabras_clave': [
                                {'es': 'Feliz',     'en': 'Happy'},
                                {'es': 'Triste',    'en': 'Sad'},
                                {'es': 'Cansado',   'en': 'Tired'},
                                {'es': 'Bien',      'en': 'Fine / Good'},
                                {'es': 'Excelente', 'en': 'Great / Excellent'},
                            ],
                        },
                    },
                    {
                        'orden': 2,
                        'tipo': 'vocabulario',
                        'puntos_actividad': 1,
                        'datos': {
                            'titulo': 'Sentimientos y emociones',
                            'tarjetas': [
                                {'es': 'Feliz',      'en': 'Happy',     'emoji': '😄'},
                                {'es': 'Triste',     'en': 'Sad',       'emoji': '😢'},
                                {'es': 'Enojado',    'en': 'Angry',     'emoji': '😠'},
                                {'es': 'Sorprendido','en': 'Surprised', 'emoji': '😲'},
                                {'es': 'Cansado',    'en': 'Tired',     'emoji': '😴'},
                                {'es': 'Asustado',   'en': 'Scared',    'emoji': '😨'},
                            ],
                        },
                    },
                    {
                        'orden': 3,
                        'tipo': 'listening',
                        'puntos_actividad': 2,
                        'datos': {
                            'titulo': 'Escucha y responde',
                            'instruccion': 'Presiona 🔊 y elige la traducción correcta.',
                            'preguntas': [
                                {
                                    'audio_texto': 'I am happy',
                                    'opciones': ['Estoy triste', 'Estoy feliz', 'Estoy cansado', 'Estoy enojado'],
                                    'respuesta_correcta': 'Estoy feliz',
                                },
                                {
                                    'audio_texto': 'I am tired',
                                    'opciones': ['Estoy feliz', 'Estoy asustado', 'Estoy cansado', 'Estoy sorprendido'],
                                    'respuesta_correcta': 'Estoy cansado',
                                },
                            ],
                        },
                    },
                ],
            },
        ],
    },
    {
        'titulo': 'Capítulo 2: Los Colores y Números',
        'descripcion': 'Aprende los colores y números del 1 al 20 en inglés.',
        'orden': 2,
        'icono_emoji': '🎨',
        'color_hex': '#4ECDC4',
        'is_desbloqueada_por_defecto': False,
        'lecciones': [
            {
                'titulo': 'The Colors — Los colores',
                'descripcion_corta': 'Aprende los colores básicos en inglés',
                'orden': 1,
                'icono_emoji': '🌈',
                'puntos_xp': 20,
                'huesos_recompensa': 4,
                'tiempo_estimado_minutos': 10,
                'actividades': [
                    {
                        'orden': 1,
                        'tipo': 'introduccion',
                        'puntos_actividad': 0,
                        'datos': {
                            'titulo': 'Los colores del arco iris',
                            'texto': 'Los colores en inglés son fáciles de aprender. ¡Milo te los enseña todos!',
                            'palabras_clave': [
                                {'es': 'Rojo',    'en': 'Red'},
                                {'es': 'Azul',    'en': 'Blue'},
                                {'es': 'Verde',   'en': 'Green'},
                                {'es': 'Amarillo','en': 'Yellow'},
                                {'es': 'Naranja', 'en': 'Orange'},
                            ],
                        },
                    },
                    {
                        'orden': 2,
                        'tipo': 'vocabulario',
                        'puntos_actividad': 1,
                        'datos': {
                            'titulo': 'Colores en inglés',
                            'tarjetas': [
                                {'es': 'Rojo',     'en': 'Red',    'emoji': '🔴'},
                                {'es': 'Azul',     'en': 'Blue',   'emoji': '🔵'},
                                {'es': 'Verde',    'en': 'Green',  'emoji': '🟢'},
                                {'es': 'Amarillo', 'en': 'Yellow', 'emoji': '🟡'},
                                {'es': 'Naranja',  'en': 'Orange', 'emoji': '🟠'},
                                {'es': 'Morado',   'en': 'Purple', 'emoji': '🟣'},
                                {'es': 'Negro',    'en': 'Black',  'emoji': '⚫'},
                                {'es': 'Blanco',   'en': 'White',  'emoji': '⚪'},
                            ],
                        },
                    },
                    {
                        'orden': 3,
                        'tipo': 'listening',
                        'puntos_actividad': 2,
                        'datos': {
                            'titulo': '¿Qué color es?',
                            'instruccion': 'Escucha el color en inglés y selecciona su traducción.',
                            'preguntas': [
                                {
                                    'audio_texto': 'Red',
                                    'opciones': ['Azul', 'Verde', 'Rojo', 'Amarillo'],
                                    'respuesta_correcta': 'Rojo',
                                },
                                {
                                    'audio_texto': 'Blue',
                                    'opciones': ['Rojo', 'Azul', 'Verde', 'Morado'],
                                    'respuesta_correcta': 'Azul',
                                },
                                {
                                    'audio_texto': 'Yellow',
                                    'opciones': ['Naranja', 'Blanco', 'Negro', 'Amarillo'],
                                    'respuesta_correcta': 'Amarillo',
                                },
                            ],
                        },
                    },
                    {
                        'orden': 4,
                        'tipo': 'pronunciacion',
                        'puntos_actividad': 1,
                        'datos': {
                            'titulo': 'Pronuncia los colores',
                            'palabras': [
                                {'en': 'Red',    'es': 'Rojo'},
                                {'en': 'Blue',   'es': 'Azul'},
                                {'en': 'Green',  'es': 'Verde'},
                                {'en': 'Yellow', 'es': 'Amarillo'},
                                {'en': 'Orange', 'es': 'Naranja'},
                            ],
                        },
                    },
                ],
            },
            {
                'titulo': 'Numbers 1-20 — Los números',
                'descripcion_corta': 'Cuenta del 1 al 20 en inglés',
                'orden': 2,
                'icono_emoji': '🔢',
                'puntos_xp': 25,
                'huesos_recompensa': 5,
                'tiempo_estimado_minutos': 15,
                'actividades': [
                    {
                        'orden': 1,
                        'tipo': 'vocabulario',
                        'puntos_actividad': 1,
                        'datos': {
                            'titulo': 'Números del 1 al 10',
                            'tarjetas': [
                                {'es': 'Uno',   'en': 'One',   'emoji': '1️⃣'},
                                {'es': 'Dos',   'en': 'Two',   'emoji': '2️⃣'},
                                {'es': 'Tres',  'en': 'Three', 'emoji': '3️⃣'},
                                {'es': 'Cuatro','en': 'Four',  'emoji': '4️⃣'},
                                {'es': 'Cinco', 'en': 'Five',  'emoji': '5️⃣'},
                                {'es': 'Seis',  'en': 'Six',   'emoji': '6️⃣'},
                                {'es': 'Siete', 'en': 'Seven', 'emoji': '7️⃣'},
                                {'es': 'Ocho',  'en': 'Eight', 'emoji': '8️⃣'},
                                {'es': 'Nueve', 'en': 'Nine',  'emoji': '9️⃣'},
                                {'es': 'Diez',  'en': 'Ten',   'emoji': '🔟'},
                            ],
                        },
                    },
                    {
                        'orden': 2,
                        'tipo': 'listening',
                        'puntos_actividad': 2,
                        'datos': {
                            'titulo': '¿Qué número escuchas?',
                            'instruccion': 'Escucha el número en inglés y selecciona el correcto.',
                            'preguntas': [
                                {
                                    'audio_texto': 'Three',
                                    'opciones': ['Uno', 'Cinco', 'Tres', 'Siete'],
                                    'respuesta_correcta': 'Tres',
                                },
                                {
                                    'audio_texto': 'Seven',
                                    'opciones': ['Dos', 'Siete', 'Cuatro', 'Diez'],
                                    'respuesta_correcta': 'Siete',
                                },
                                {
                                    'audio_texto': 'Ten',
                                    'opciones': ['Seis', 'Ocho', 'Nueve', 'Diez'],
                                    'respuesta_correcta': 'Diez',
                                },
                            ],
                        },
                    },
                ],
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Crea el contenido inicial del Modo Historia (2 capítulos, 5 lecciones).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Borra todo el contenido de historia antes de sembrar.',
        )

    def handle(self, *args, **options):
        if options['reset']:
            SeccionHistoria.objects.all().delete()
            self.stdout.write(self.style.WARNING('Contenido de historia borrado.'))

        creadas = 0
        for sec_data in SECCIONES:
            lecciones_data = sec_data.pop('lecciones')
            sec, created = SeccionHistoria.objects.get_or_create(
                orden=sec_data['orden'],
                defaults=sec_data,
            )
            if created:
                creadas += 1
                self.stdout.write(f'  Seccion creada: orden={sec.orden} "{sec.titulo}"')
            else:
                self.stdout.write(f'  Seccion ya existe: orden={sec.orden} "{sec.titulo}"')

            for lec_data in lecciones_data:
                actividades_data = lec_data.pop('actividades')
                lec, _ = Leccion.objects.get_or_create(
                    seccion=sec,
                    orden=lec_data['orden'],
                    defaults=lec_data,
                )
                for act_data in actividades_data:
                    ActividadLeccion.objects.get_or_create(
                        leccion=lec,
                        orden=act_data['orden'],
                        defaults=act_data,
                    )

        self.stdout.write(self.style.SUCCESS(
            f'\nListo. {creadas} secciones nuevas creadas. '
            'Corre con --reset para borrar y recrear desde cero.'
        ))
