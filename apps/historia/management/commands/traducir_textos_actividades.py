import re
from django.core.management.base import BaseCommand
from apps.historia.models import ActividadLeccion

PATRON_READING = re.compile(
    r"In English, we use many words for (.+?)\. "
    r"For example, '(.+?)' and '(.+?)' are very common words\. "
    r"We can also say '(.+?)' and '(.+?)'\. "
    r"Learning .+? vocabulary is fun and useful!?",
    re.IGNORECASE | re.DOTALL,
)

PATRON_REVIEW = re.compile(
    r"Let's review repaso: (.+?)! We learned many new words\. Do you remember them all\?",
    re.IGNORECASE,
)

INSTRUCCIONES_ES = {
    "Listen and select the correct word.": "Escucha el audio y elige la respuesta correcta.",
    "Listen and select the correct answer.": "Escucha el audio y elige la respuesta correcta.",
    "Listen carefully and choose the right option.": "Escucha con atencion y elige la opcion correcta.",
    "Read the text and answer the questions.": "Lee el texto y responde las preguntas.",
    "Read and answer the questions.": "Lee con atencion y responde las preguntas.",
    "Write the missing word in English.": "Escribe la palabra que falta en ingles.",
    "Write the words in English.": "Escribe las palabras en ingles.",
}


def _traducir_reading_texto(texto):
    m = PATRON_READING.search(texto)
    if m:
        tema, w1, w2, w3, w4 = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        return (
            f"En ingles, usamos muchas palabras para hablar de {tema}. "
            f"Por ejemplo, '{w1}' y '{w2}' son palabras muy comunes. "
            f"Tambien podemos decir '{w3}' y '{w4}'. "
            f"Aprender vocabulario de {tema} es muy divertido."
        )
    m2 = PATRON_REVIEW.search(texto)
    if m2:
        tema = m2.group(1)
        return f"Vamos a repasar: {tema}! Aprendimos muchas palabras nuevas. Las recuerdas todas?"
    return None


class Command(BaseCommand):
    help = "Traduce al espanol los textos de instruccion en ingles en las actividades de historia."

    def handle(self, *args, **options):
        actualizados = 0

        for act in ActividadLeccion.objects.filter(tipo="listening"):
            datos = act.datos or {}
            nueva = INSTRUCCIONES_ES.get(datos.get("instruccion", ""))
            if nueva:
                datos["instruccion"] = nueva
                act.datos = datos
                act.save(update_fields=["datos"])
                actualizados += 1

        for act in ActividadLeccion.objects.filter(tipo="reading"):
            datos = act.datos or {}
            cambio = False
            nueva_instr = INSTRUCCIONES_ES.get(datos.get("instruccion", ""))
            if nueva_instr:
                datos["instruccion"] = nueva_instr
                cambio = True
            nuevo_texto = _traducir_reading_texto(datos.get("texto", ""))
            if nuevo_texto:
                datos["texto"] = nuevo_texto
                cambio = True
            if cambio:
                act.datos = datos
                act.save(update_fields=["datos"])
                actualizados += 1

        for act in ActividadLeccion.objects.filter(tipo="writing"):
            datos = act.datos or {}
            nueva = INSTRUCCIONES_ES.get(datos.get("instruccion", ""))
            if nueva:
                datos["instruccion"] = nueva
                act.datos = datos
                act.save(update_fields=["datos"])
                actualizados += 1

        self.stdout.write(self.style.SUCCESS(
            f"Listo! {actualizados} actividades actualizadas."
        ))
