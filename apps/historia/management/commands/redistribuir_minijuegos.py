import random
from django.core.management.base import BaseCommand
from apps.historia.models import ActividadLeccion, Leccion

TIPOS = ['memoria', 'rellenar', 'ordenar_oracion', 'unir_pares', 'verdadero_falso', 'clasificar']

# Contenido por sección (1-10) y tipo de minijuego
# Cada entrada puede tener varias opciones; se elige una al azar por lección.
CONTENIDO = {
    1: {  # Colores
        'memoria': [
            {'pares': [
                {'es': 'rojo', 'en': 'red', 'emoji': '🔴'},
                {'es': 'azul', 'en': 'blue', 'emoji': '🔵'},
                {'es': 'verde', 'en': 'green', 'emoji': '🟢'},
                {'es': 'amarillo', 'en': 'yellow', 'emoji': '🟡'},
                {'es': 'naranja', 'en': 'orange', 'emoji': '🟠'},
                {'es': 'morado', 'en': 'purple', 'emoji': '🟣'},
            ]},
            {'pares': [
                {'es': 'blanco', 'en': 'white', 'emoji': '⬜'},
                {'es': 'negro', 'en': 'black', 'emoji': '⬛'},
                {'es': 'rosa', 'en': 'pink', 'emoji': '🩷'},
                {'es': 'café', 'en': 'brown', 'emoji': '🟫'},
                {'es': 'gris', 'en': 'gray', 'emoji': '🩶'},
                {'es': 'celeste', 'en': 'light blue', 'emoji': '🩵'},
            ]},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'The sky is ___', 'respuesta': 'blue', 'emoji': '🌤️'},
                {'texto': 'Apples are ___', 'respuesta': 'red', 'emoji': '🍎'},
                {'texto': 'Bananas are ___', 'respuesta': 'yellow', 'emoji': '🍌'},
            ]},
            {'oraciones': [
                {'texto': 'Grass is ___', 'respuesta': 'green', 'emoji': '🌿'},
                {'texto': 'The sun is ___', 'respuesta': 'yellow', 'emoji': '☀️'},
                {'texto': 'Snow is ___', 'respuesta': 'white', 'emoji': '❄️'},
            ]},
        ],
        'ordenar_oracion': [
            {'oracion': 'The apple is red', 'emoji': '🍎'},
            {'oracion': 'The sky is blue today', 'emoji': '🌤️'},
            {'oracion': 'I like the color green', 'emoji': '💚'},
        ],
        'unir_pares': [
            {'pares': [
                {'izq': '🔴 rojo', 'der': 'red'},
                {'izq': '🔵 azul', 'der': 'blue'},
                {'izq': '🟢 verde', 'der': 'green'},
                {'izq': '🟡 amarillo', 'der': 'yellow'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': 'The sky is red. ☁️', 'respuesta': False, 'explicacion': '¡El cielo es azul! 🔵'},
                {'afirmacion': 'Grass is green. 🌿', 'respuesta': True, 'explicacion': '¡Correcto! La hierba es verde. ✅'},
                {'afirmacion': 'Bananas are purple. 🍌', 'respuesta': False, 'explicacion': '¡Las bananas son amarillas! 🟡'},
                {'afirmacion': 'Roses are red. 🌹', 'respuesta': True, 'explicacion': '¡Muy bien! Las rosas son rojas. ✅'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Colores Calidos', 'emoji': '🔥', 'items': ['red', 'orange', 'yellow']},
                {'nombre': 'Colores Frios', 'emoji': '❄️', 'items': ['blue', 'green', 'purple']},
            ]},
        ],
    },
    2: {  # Familia
        'memoria': [
            {'pares': [
                {'es': 'mamá', 'en': 'mom', 'emoji': '👩'},
                {'es': 'papá', 'en': 'dad', 'emoji': '👨'},
                {'es': 'hermano', 'en': 'brother', 'emoji': '👦'},
                {'es': 'hermana', 'en': 'sister', 'emoji': '👧'},
                {'es': 'abuelo', 'en': 'grandpa', 'emoji': '👴'},
                {'es': 'abuela', 'en': 'grandma', 'emoji': '👵'},
            ]},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'My ___ cooks dinner.', 'respuesta': 'mom', 'emoji': '👩‍🍳'},
                {'texto': 'My ___ reads the news.', 'respuesta': 'dad', 'emoji': '📰'},
                {'texto': 'My ___ plays with me.', 'respuesta': 'brother', 'emoji': '👦'},
            ]},
        ],
        'ordenar_oracion': [
            {'oracion': 'My mom is very kind', 'emoji': '👩'},
            {'oracion': 'I love my family a lot', 'emoji': '👨‍👩‍👧‍👦'},
            {'oracion': 'My sister has long hair', 'emoji': '👧'},
        ],
        'unir_pares': [
            {'pares': [
                {'izq': '👩 mamá', 'der': 'mom'},
                {'izq': '👨 papá', 'der': 'dad'},
                {'izq': '👦 hermano', 'der': 'brother'},
                {'izq': '👵 abuela', 'der': 'grandma'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': '"Mom" means papá. 👨', 'respuesta': False, 'explicacion': '¡"Mom" significa mamá! 👩'},
                {'afirmacion': '"Sister" means hermana. 👧', 'respuesta': True, 'explicacion': '¡Correcto! ✅'},
                {'afirmacion': '"Grandpa" means abuela. 👵', 'respuesta': False, 'explicacion': '¡"Grandpa" significa abuelo! 👴'},
                {'afirmacion': '"Brother" means hermano. 👦', 'respuesta': True, 'explicacion': '¡Muy bien! ✅'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Padres', 'emoji': '👨‍👩', 'items': ['mom', 'dad']},
                {'nombre': 'Hijos', 'emoji': '🧒', 'items': ['sister', 'brother']},
                {'nombre': 'Abuelos', 'emoji': '🧓', 'items': ['grandpa', 'grandma']},
            ]},
        ],
    },
    3: {  # Números
        'memoria': [
            {'pares': [
                {'es': 'uno', 'en': 'one', 'emoji': '1️⃣'},
                {'es': 'dos', 'en': 'two', 'emoji': '2️⃣'},
                {'es': 'tres', 'en': 'three', 'emoji': '3️⃣'},
                {'es': 'cuatro', 'en': 'four', 'emoji': '4️⃣'},
                {'es': 'cinco', 'en': 'five', 'emoji': '5️⃣'},
                {'es': 'seis', 'en': 'six', 'emoji': '6️⃣'},
            ]},
            {'pares': [
                {'es': 'siete', 'en': 'seven', 'emoji': '7️⃣'},
                {'es': 'ocho', 'en': 'eight', 'emoji': '8️⃣'},
                {'es': 'nueve', 'en': 'nine', 'emoji': '9️⃣'},
                {'es': 'diez', 'en': 'ten', 'emoji': '🔟'},
                {'es': 'cero', 'en': 'zero', 'emoji': '0️⃣'},
                {'es': 'cien', 'en': 'one hundred', 'emoji': '💯'},
            ]},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'I have ___ hands.', 'respuesta': 'two', 'emoji': '🙌'},
                {'texto': 'A week has ___ days.', 'respuesta': 'seven', 'emoji': '📅'},
                {'texto': 'A cat has ___ legs.', 'respuesta': 'four', 'emoji': '🐈'},
            ]},
        ],
        'ordenar_oracion': [
            {'oracion': 'I have ten fingers', 'emoji': '🖐️'},
            {'oracion': 'There are seven days in a week', 'emoji': '📅'},
            {'oracion': 'Two plus three is five', 'emoji': '➕'},
        ],
        'unir_pares': [
            {'pares': [
                {'izq': '1️⃣ uno', 'der': 'one'},
                {'izq': '5️⃣ cinco', 'der': 'five'},
                {'izq': '🔟 diez', 'der': 'ten'},
                {'izq': '3️⃣ tres', 'der': 'three'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': '"Five" is the number 5. 5️⃣', 'respuesta': True, 'explicacion': '¡Correcto! "Five" = 5 ✅'},
                {'afirmacion': '"Ten" means nueve. 9️⃣', 'respuesta': False, 'explicacion': '¡"Ten" significa diez! 🔟'},
                {'afirmacion': 'Two plus two is four. ➕', 'respuesta': True, 'explicacion': '¡Muy bien! 2+2=4 ✅'},
                {'afirmacion': '"Eight" is the number 7. 7️⃣', 'respuesta': False, 'explicacion': '¡"Eight" es el 8, no el 7! 8️⃣'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Numeros pequenos (1-5)', 'emoji': '🤏', 'items': ['one', 'two', 'three', 'four', 'five']},
                {'nombre': 'Numeros grandes (6-10)', 'emoji': '💪', 'items': ['six', 'seven', 'eight', 'nine', 'ten']},
            ]},
        ],
    },
    4: {  # Animales
        'memoria': [
            {'pares': [
                {'es': 'perro', 'en': 'dog', 'emoji': '🐕'},
                {'es': 'gato', 'en': 'cat', 'emoji': '🐈'},
                {'es': 'pájaro', 'en': 'bird', 'emoji': '🐦'},
                {'es': 'pez', 'en': 'fish', 'emoji': '🐟'},
                {'es': 'caballo', 'en': 'horse', 'emoji': '🐴'},
                {'es': 'vaca', 'en': 'cow', 'emoji': '🐄'},
            ]},
            {'pares': [
                {'es': 'elefante', 'en': 'elephant', 'emoji': '🐘'},
                {'es': 'león', 'en': 'lion', 'emoji': '🦁'},
                {'es': 'mono', 'en': 'monkey', 'emoji': '🐒'},
                {'es': 'serpiente', 'en': 'snake', 'emoji': '🐍'},
                {'es': 'rana', 'en': 'frog', 'emoji': '🐸'},
                {'es': 'mariposa', 'en': 'butterfly', 'emoji': '🦋'},
            ]},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'The ___ barks. 🐕', 'respuesta': 'dog', 'emoji': '🔊'},
                {'texto': 'The ___ meows. 🐈', 'respuesta': 'cat', 'emoji': '🔊'},
                {'texto': 'The ___ swims. 🐟', 'respuesta': 'fish', 'emoji': '🌊'},
            ]},
        ],
        'ordenar_oracion': [
            {'oracion': 'The dog runs very fast', 'emoji': '🐕'},
            {'oracion': 'A bird can fly high', 'emoji': '🐦'},
            {'oracion': 'The cat drinks some milk', 'emoji': '🐈'},
        ],
        'unir_pares': [
            {'pares': [
                {'izq': '🐕 perro', 'der': 'dog'},
                {'izq': '🐈 gato', 'der': 'cat'},
                {'izq': '🦁 león', 'der': 'lion'},
                {'izq': '🐘 elefante', 'der': 'elephant'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': 'A "fish" lives in water. 🌊', 'respuesta': True, 'explicacion': '¡Correcto! Los peces viven en el agua. ✅'},
                {'afirmacion': 'A "bird" is a perro. 🐕', 'respuesta': False, 'explicacion': '¡"Bird" significa pajaro! 🐦'},
                {'afirmacion': 'A "lion" is a wild animal. 🦁', 'respuesta': True, 'explicacion': '¡Muy bien! El leon es un animal salvaje. ✅'},
                {'afirmacion': 'A "cow" can fly. ✈️', 'respuesta': False, 'explicacion': '¡Las vacas no pueden volar! 🐄'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Animales de Granja', 'emoji': '🌾', 'items': ['cow', 'horse', 'pig', 'chicken']},
                {'nombre': 'Animales Salvajes', 'emoji': '🌿', 'items': ['lion', 'elephant', 'monkey', 'snake']},
            ]},
        ],
    },
    5: {  # Cuerpo
        'memoria': [
            {'pares': [
                {'es': 'cabeza', 'en': 'head', 'emoji': '🗣️'},
                {'es': 'mano', 'en': 'hand', 'emoji': '✋'},
                {'es': 'pie', 'en': 'foot', 'emoji': '🦶'},
                {'es': 'ojo', 'en': 'eye', 'emoji': '👁️'},
                {'es': 'nariz', 'en': 'nose', 'emoji': '👃'},
                {'es': 'boca', 'en': 'mouth', 'emoji': '👄'},
            ]},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'I see with my ___', 'respuesta': 'eyes', 'emoji': '👁️'},
                {'texto': 'I smell with my ___', 'respuesta': 'nose', 'emoji': '👃'},
                {'texto': 'I eat with my ___', 'respuesta': 'mouth', 'emoji': '👄'},
            ]},
        ],
        'ordenar_oracion': [
            {'oracion': 'I have two hands', 'emoji': '🙌'},
            {'oracion': 'My nose is in the middle', 'emoji': '👃'},
            {'oracion': 'We use our eyes to see', 'emoji': '👁️'},
        ],
        'unir_pares': [
            {'pares': [
                {'izq': '👁️ ojo', 'der': 'eye'},
                {'izq': '👃 nariz', 'der': 'nose'},
                {'izq': '✋ mano', 'der': 'hand'},
                {'izq': '🦶 pie', 'der': 'foot'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': 'We use our "eyes" to see. 👁️', 'respuesta': True, 'explicacion': '¡Correcto! Los ojos son para ver. ✅'},
                {'afirmacion': '"Hand" means pie. 🦶', 'respuesta': False, 'explicacion': '¡"Hand" significa mano! ✋'},
                {'afirmacion': 'We have two ears. 👂', 'respuesta': True, 'explicacion': '¡Bien! Tenemos dos orejas. ✅'},
                {'afirmacion': '"Nose" means boca. 👄', 'respuesta': False, 'explicacion': '¡"Nose" significa nariz! 👃'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'La Cara', 'emoji': '😊', 'items': ['eye', 'nose', 'mouth', 'ear']},
                {'nombre': 'El Cuerpo', 'emoji': '🦾', 'items': ['hand', 'foot', 'arm', 'leg']},
            ]},
        ],
    },
    6: {  # Comida
        'memoria': [
            {'pares': [
                {'es': 'manzana', 'en': 'apple', 'emoji': '🍎'},
                {'es': 'naranja', 'en': 'orange', 'emoji': '🍊'},
                {'es': 'pan', 'en': 'bread', 'emoji': '🍞'},
                {'es': 'leche', 'en': 'milk', 'emoji': '🥛'},
                {'es': 'arroz', 'en': 'rice', 'emoji': '🍚'},
                {'es': 'huevo', 'en': 'egg', 'emoji': '🥚'},
            ]},
            {'pares': [
                {'es': 'pollo', 'en': 'chicken', 'emoji': '🍗'},
                {'es': 'sopa', 'en': 'soup', 'emoji': '🥣'},
                {'es': 'pizza', 'en': 'pizza', 'emoji': '🍕'},
                {'es': 'torta', 'en': 'cake', 'emoji': '🎂'},
                {'es': 'fresa', 'en': 'strawberry', 'emoji': '🍓'},
                {'es': 'zanahoria', 'en': 'carrot', 'emoji': '🥕'},
            ]},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'I eat ___ for breakfast.', 'respuesta': 'eggs', 'emoji': '🍳'},
                {'texto': 'I drink ___ every morning.', 'respuesta': 'milk', 'emoji': '🥛'},
                {'texto': 'Apples are a type of ___', 'respuesta': 'fruit', 'emoji': '🍎'},
            ]},
        ],
        'ordenar_oracion': [
            {'oracion': 'I eat an apple every day', 'emoji': '🍎'},
            {'oracion': 'Rice and chicken is delicious', 'emoji': '🍚'},
            {'oracion': 'She drinks milk for breakfast', 'emoji': '🥛'},
        ],
        'unir_pares': [
            {'pares': [
                {'izq': '🍎 manzana', 'der': 'apple'},
                {'izq': '🍞 pan', 'der': 'bread'},
                {'izq': '🥛 leche', 'der': 'milk'},
                {'izq': '🍕 pizza', 'der': 'pizza'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': '"Milk" is a drink. 🥛', 'respuesta': True, 'explicacion': '¡Correcto! La leche es una bebida. ✅'},
                {'afirmacion': '"Apple" means naranja. 🍊', 'respuesta': False, 'explicacion': '¡"Apple" significa manzana! 🍎'},
                {'afirmacion': 'Carrots are vegetables. 🥕', 'respuesta': True, 'explicacion': '¡Bien! Las zanahorias son verduras. ✅'},
                {'afirmacion': '"Bread" means torta. 🎂', 'respuesta': False, 'explicacion': '¡"Bread" significa pan! 🍞'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Frutas', 'emoji': '🍓', 'items': ['apple', 'orange', 'strawberry', 'banana']},
                {'nombre': 'Verduras', 'emoji': '🥦', 'items': ['carrot', 'tomato', 'corn', 'potato']},
            ]},
        ],
    },
    7: {  # Casa
        'memoria': [
            {'pares': [
                {'es': 'cama', 'en': 'bed', 'emoji': '🛏️'},
                {'es': 'mesa', 'en': 'table', 'emoji': '🪑'},
                {'es': 'silla', 'en': 'chair', 'emoji': '🪑'},
                {'es': 'puerta', 'en': 'door', 'emoji': '🚪'},
                {'es': 'ventana', 'en': 'window', 'emoji': '🪟'},
                {'es': 'cocina', 'en': 'kitchen', 'emoji': '🍳'},
            ]},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'I sleep in my ___', 'respuesta': 'bed', 'emoji': '🛏️'},
                {'texto': 'We eat at the ___', 'respuesta': 'table', 'emoji': '🍽️'},
                {'texto': 'I look through the ___', 'respuesta': 'window', 'emoji': '🪟'},
            ]},
        ],
        'ordenar_oracion': [
            {'oracion': 'My room has a big window', 'emoji': '🪟'},
            {'oracion': 'The table is in the kitchen', 'emoji': '🍳'},
            {'oracion': 'I sleep in my bed every night', 'emoji': '🛏️'},
        ],
        'unir_pares': [
            {'pares': [
                {'izq': '🛏️ cama', 'der': 'bed'},
                {'izq': '🚪 puerta', 'der': 'door'},
                {'izq': '🪟 ventana', 'der': 'window'},
                {'izq': '🍳 cocina', 'der': 'kitchen'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': '"Bed" means cama. 🛏️', 'respuesta': True, 'explicacion': '¡Correcto! ✅'},
                {'afirmacion': '"Door" means ventana. 🪟', 'respuesta': False, 'explicacion': '¡"Door" significa puerta! 🚪'},
                {'afirmacion': 'A kitchen is where we cook. 🍳', 'respuesta': True, 'explicacion': '¡Bien! En la cocina cocinamos. ✅'},
                {'afirmacion': '"Chair" means mesa. 🪑', 'respuesta': False, 'explicacion': '¡"Chair" significa silla! 🪑'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'El Cuarto', 'emoji': '🛏️', 'items': ['bed', 'pillow', 'lamp', 'closet']},
                {'nombre': 'La Cocina', 'emoji': '🍳', 'items': ['stove', 'fridge', 'pot', 'cup']},
            ]},
        ],
    },
    8: {  # Clima
        'memoria': [
            {'pares': [
                {'es': 'sol', 'en': 'sun', 'emoji': '☀️'},
                {'es': 'lluvia', 'en': 'rain', 'emoji': '🌧️'},
                {'es': 'nieve', 'en': 'snow', 'emoji': '❄️'},
                {'es': 'nube', 'en': 'cloud', 'emoji': '☁️'},
                {'es': 'viento', 'en': 'wind', 'emoji': '💨'},
                {'es': 'arco iris', 'en': 'rainbow', 'emoji': '🌈'},
            ]},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'The ___ shines every day.', 'respuesta': 'sun', 'emoji': '☀️'},
                {'texto': 'I use an umbrella in the ___', 'respuesta': 'rain', 'emoji': '☔'},
                {'texto': 'It is cold when there is ___', 'respuesta': 'snow', 'emoji': '❄️'},
            ]},
        ],
        'ordenar_oracion': [
            {'oracion': 'The sun is very bright today', 'emoji': '☀️'},
            {'oracion': 'I see a rainbow after the rain', 'emoji': '🌈'},
            {'oracion': 'The wind blows my hat away', 'emoji': '💨'},
        ],
        'unir_pares': [
            {'pares': [
                {'izq': '☀️ sol', 'der': 'sun'},
                {'izq': '🌧️ lluvia', 'der': 'rain'},
                {'izq': '❄️ nieve', 'der': 'snow'},
                {'izq': '🌈 arco iris', 'der': 'rainbow'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': '"Rain" means lluvia. 🌧️', 'respuesta': True, 'explicacion': '¡Correcto! ✅'},
                {'afirmacion': '"Snow" means sol. ☀️', 'respuesta': False, 'explicacion': '¡"Snow" significa nieve! ❄️'},
                {'afirmacion': 'A rainbow appears after rain. 🌈', 'respuesta': True, 'explicacion': '¡Bien! El arco iris aparece despues de la lluvia. ✅'},
                {'afirmacion': '"Cloud" means viento. 💨', 'respuesta': False, 'explicacion': '¡"Cloud" significa nube! ☁️'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Clima Caliente', 'emoji': '☀️', 'items': ['sun', 'hot', 'dry', 'summer']},
                {'nombre': 'Clima Frio', 'emoji': '❄️', 'items': ['snow', 'ice', 'cold', 'winter']},
            ]},
        ],
    },
    9: {  # Actividades
        'memoria': [
            {'pares': [
                {'es': 'correr', 'en': 'run', 'emoji': '🏃'},
                {'es': 'saltar', 'en': 'jump', 'emoji': '🤸'},
                {'es': 'nadar', 'en': 'swim', 'emoji': '🏊'},
                {'es': 'leer', 'en': 'read', 'emoji': '📖'},
                {'es': 'pintar', 'en': 'paint', 'emoji': '🎨'},
                {'es': 'bailar', 'en': 'dance', 'emoji': '💃'},
            ]},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'I like to ___ in the pool.', 'respuesta': 'swim', 'emoji': '🏊'},
                {'texto': 'She loves to ___ books.', 'respuesta': 'read', 'emoji': '📖'},
                {'texto': 'They ___ to the music.', 'respuesta': 'dance', 'emoji': '💃'},
            ]},
        ],
        'ordenar_oracion': [
            {'oracion': 'I love to play soccer', 'emoji': '⚽'},
            {'oracion': 'She can run very fast', 'emoji': '🏃'},
            {'oracion': 'We swim in the pool every day', 'emoji': '🏊'},
        ],
        'unir_pares': [
            {'pares': [
                {'izq': '🏃 correr', 'der': 'run'},
                {'izq': '🏊 nadar', 'der': 'swim'},
                {'izq': '📖 leer', 'der': 'read'},
                {'izq': '🎨 pintar', 'der': 'paint'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': '"Swim" means nadar. 🏊', 'respuesta': True, 'explicacion': '¡Correcto! ✅'},
                {'afirmacion': '"Run" means bailar. 💃', 'respuesta': False, 'explicacion': '¡"Run" significa correr! 🏃'},
                {'afirmacion': 'We use a ball to play soccer. ⚽', 'respuesta': True, 'explicacion': '¡Bien! Usamos pelota para jugar futbol. ✅'},
                {'afirmacion': '"Read" means pintar. 🎨', 'respuesta': False, 'explicacion': '¡"Read" significa leer! 📖'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Deportes', 'emoji': '🏅', 'items': ['run', 'swim', 'jump', 'kick']},
                {'nombre': 'Arte y Cultura', 'emoji': '🎨', 'items': ['paint', 'draw', 'dance', 'sing']},
            ]},
        ],
    },
    10: {  # Pueblo / Mundo
        'memoria': [
            {'pares': [
                {'es': 'escuela', 'en': 'school', 'emoji': '🏫'},
                {'es': 'hospital', 'en': 'hospital', 'emoji': '🏥'},
                {'es': 'parque', 'en': 'park', 'emoji': '🌳'},
                {'es': 'tienda', 'en': 'store', 'emoji': '🏪'},
                {'es': 'biblioteca', 'en': 'library', 'emoji': '📚'},
                {'es': 'iglesia', 'en': 'church', 'emoji': '⛪'},
            ]},
        ],
        'rellenar': [
            {'oraciones': [
                {'texto': 'I learn at ___', 'respuesta': 'school', 'emoji': '🏫'},
                {'texto': 'Sick people go to the ___', 'respuesta': 'hospital', 'emoji': '🏥'},
                {'texto': 'I borrow books from the ___', 'respuesta': 'library', 'emoji': '📚'},
            ]},
        ],
        'ordenar_oracion': [
            {'oracion': 'The school is near my house', 'emoji': '🏫'},
            {'oracion': 'I play in the park every Saturday', 'emoji': '🌳'},
            {'oracion': 'The library has many books', 'emoji': '📚'},
        ],
        'unir_pares': [
            {'pares': [
                {'izq': '🏫 escuela', 'der': 'school'},
                {'izq': '🏥 hospital', 'der': 'hospital'},
                {'izq': '🌳 parque', 'der': 'park'},
                {'izq': '📚 biblioteca', 'der': 'library'},
            ]},
        ],
        'verdadero_falso': [
            {'preguntas': [
                {'afirmacion': '"School" means escuela. 🏫', 'respuesta': True, 'explicacion': '¡Correcto! ✅'},
                {'afirmacion': '"Park" means hospital. 🏥', 'respuesta': False, 'explicacion': '¡"Park" significa parque! 🌳'},
                {'afirmacion': 'We buy things at a store. 🏪', 'respuesta': True, 'explicacion': '¡Bien! En la tienda compramos cosas. ✅'},
                {'afirmacion': '"Library" means tienda. 🏪', 'respuesta': False, 'explicacion': '¡"Library" significa biblioteca! 📚'},
            ]},
        ],
        'clasificar': [
            {'categorias': [
                {'nombre': 'Salud y Ayuda', 'emoji': '🏥', 'items': ['hospital', 'pharmacy', 'fire station', 'police']},
                {'nombre': 'Aprender y Divertirse', 'emoji': '📚', 'items': ['school', 'library', 'park', 'museum']},
            ]},
        ],
    },
}


def _get_datos(seccion_pk, tipo):
    opciones = CONTENIDO.get(seccion_pk, CONTENIDO[1]).get(tipo, [])
    if not opciones:
        opciones = CONTENIDO[1].get(tipo, [{}])
    datos = dict(random.choice(opciones))
    datos['tipo_minijuego'] = tipo
    if tipo == 'memoria':
        datos.setdefault('titulo', '¡Memoria!')
        datos.setdefault('instruccion', 'Encuentra los pares que coinciden.')
    elif tipo == 'rellenar':
        datos.setdefault('titulo', 'Rellena el espacio')
        datos.setdefault('instruccion', 'Escribe la palabra que falta en inglés.')
    elif tipo == 'ordenar_oracion':
        datos.setdefault('titulo', 'Arma la oración')
        datos.setdefault('instruccion', 'Toca las palabras en el orden correcto.')
    elif tipo == 'unir_pares':
        datos.setdefault('titulo', 'Une los pares')
        datos.setdefault('instruccion', 'Toca una palabra de cada columna para unir los pares.')
    elif tipo == 'verdadero_falso':
        datos.setdefault('titulo', '¿Verdadero o Falso?')
        datos.setdefault('instruccion', 'Lee la afirmación y elige Verdadero o Falso.')
    elif tipo == 'clasificar':
        datos.setdefault('titulo', 'Organiza en grupos')
        datos.setdefault('instruccion', 'Arrastra cada palabra al grupo correcto.')
    return datos


class Command(BaseCommand):
    help = 'Redistribuye aleatoriamente los tipos de minijuego y añade segundos minijuegos en ~20 lecciones.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--segundos', type=int, default=20,
            help='Número de lecciones que recibirán un segundo minijuego (default: 20).'
        )
        parser.add_argument(
            '--seed', type=int, default=None,
            help='Semilla para reproducibilidad.'
        )

    def handle(self, *args, **options):
        if options['seed'] is not None:
            random.seed(options['seed'])

        actividades = list(
            ActividadLeccion.objects.filter(tipo='minijuego_embed')
            .select_related('leccion__seccion')
            .order_by('leccion__seccion__orden', 'leccion__orden', 'orden')
        )
        self.stdout.write(f'Actividades minijuego encontradas: {len(actividades)}')

        # Distribuir los 6 tipos de forma uniforme
        tipos_pool = (TIPOS * (len(actividades) // len(TIPOS) + 1))[:len(actividades)]
        random.shuffle(tipos_pool)

        for act, tipo in zip(actividades, tipos_pool):
            seccion_pk = act.leccion.seccion.pk
            act.datos = _get_datos(seccion_pk, tipo)
            act.save()

        self.stdout.write(self.style.SUCCESS(f'OK: {len(actividades)} minijuegos redistribuidos.'))

        # Añadir segundos minijuegos solo en lecciones que aún tienen 1
        from django.db.models import Count as _Count
        lecciones_con_uno = list(
            ActividadLeccion.objects.filter(tipo='minijuego_embed')
            .values('leccion').annotate(n=_Count('id')).filter(n=1)
            .values_list('leccion', flat=True)
        )
        num_segundos = min(options['segundos'], len(lecciones_con_uno))
        lecciones_elegidas = random.sample(lecciones_con_uno, num_segundos)

        creados = 0
        for lec_pk in lecciones_elegidas:
            try:
                leccion = Leccion.objects.select_related('seccion').get(pk=lec_pk)
            except Leccion.DoesNotExist:
                continue

            tipo_existente = ActividadLeccion.objects.filter(
                leccion=leccion, tipo='minijuego_embed'
            ).first()
            tipo_actual = (tipo_existente.datos or {}).get('tipo_minijuego', 'memoria') if tipo_existente else 'memoria'

            tipos_restantes = [t for t in TIPOS if t != tipo_actual]
            tipo_nuevo = random.choice(tipos_restantes)

            orden_max = ActividadLeccion.objects.filter(leccion=leccion).order_by('-orden').values_list('orden', flat=True).first() or 0

            ActividadLeccion.objects.create(
                leccion=leccion,
                orden=orden_max + 1,
                tipo='minijuego_embed',
                datos=_get_datos(leccion.seccion.pk, tipo_nuevo),
                puntos_actividad=2,
            )
            creados += 1

        self.stdout.write(self.style.SUCCESS(
            f'OK: {creados} segundos minijuegos anadidos en {num_segundos} lecciones.'
        ))
        self.stdout.write(self.style.SUCCESS('Listo! Redistribucion completa.'))
