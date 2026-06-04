"""Vocabulary unlock logic and milestone rewards for Fase 5."""
import random as _random
from django.db import transaction


HITOS_VOCAB = [
    (10, 2),
    (25, 5),
    (50, 10),
    (100, 20),
    (200, 40),
]

PALABRAS_POR_MINIJUEGO  = 4   # palabras de la categoría del minijuego al completarlo por primera vez
CATEGORIAS_POR_TALLER   = 5   # categorías aleatorias de las que se desbloquea vocab al completar un taller
PALABRAS_MIN_POR_CAT    = 1   # mínimo de palabras desbloqueadas por categoría en taller
PALABRAS_MAX_POR_CAT    = 3   # máximo de palabras desbloqueadas por categoría en taller


def desbloquear_palabras_iniciales(estudiante):
    """Desbloquea las palabras con is_unlocked_by_default=True para el estudiante.
    Se llama una sola vez al crear la cuenta del estudiante.
    """
    from .models import VocabularyItem, VocabularioDesbloqueado

    items_iniciales = VocabularyItem.objects.filter(
        is_unlocked_by_default=True, is_active=True
    )
    nuevos = []
    existentes = set(
        VocabularioDesbloqueado.objects.filter(
            estudiante=estudiante, item__in=items_iniciales
        ).values_list('item_id', flat=True)
    )
    for item in items_iniciales:
        if item.pk not in existentes:
            nuevos.append(
                VocabularioDesbloqueado(
                    estudiante=estudiante,
                    item=item,
                    fuente='inicial',
                )
            )
    if nuevos:
        VocabularioDesbloqueado.objects.bulk_create(nuevos, ignore_conflicts=True)


def desbloquear_vocabulario_taller(sesion):
    """Al completar un taller desbloquea palabras aleatorias de categorías aleatorias.

    Elige CATEGORIAS_POR_TALLER categorías al azar y de cada una desbloquea entre
    PALABRAS_MIN_POR_CAT y PALABRAS_MAX_POR_CAT palabras que el estudiante aún no tenga.
    No requiere configuración del profesor — funciona para cualquier taller.
    """
    from .models import VocabularyItem, VocabularioDesbloqueado, Category

    estudiante = sesion.estudiante

    ya_desbloqueados = set(
        VocabularioDesbloqueado.objects.filter(
            estudiante=estudiante
        ).values_list('item_id', flat=True)
    )

    # Elegir categorías activas al azar (excluir Pintura Libre que es especial)
    todas = list(Category.active.exclude(name='Pintura Libre'))
    elegidas = _random.sample(todas, min(CATEGORIAS_POR_TALLER, len(todas)))

    nuevos = []
    for cat in elegidas:
        candidatos = list(
            VocabularyItem.objects.filter(category=cat, is_active=True)
            .exclude(pk__in=ya_desbloqueados)
        )
        if not candidatos:
            continue
        cantidad = _random.randint(
            PALABRAS_MIN_POR_CAT, min(PALABRAS_MAX_POR_CAT, len(candidatos))
        )
        for item in _random.sample(candidatos, cantidad):
            nuevos.append(
                VocabularioDesbloqueado(estudiante=estudiante, item=item, fuente='taller')
            )
            ya_desbloqueados.add(item.pk)   # evitar duplicados entre categorías

    if nuevos:
        VocabularioDesbloqueado.objects.bulk_create(nuevos, ignore_conflicts=True)

    return nuevos


def desbloquear_vocabulario_minijuego(estudiante, game):
    """Al completar un minijuego por primera vez desbloquea palabras de su categoría.

    Desbloquea hasta PALABRAS_POR_MINIJUEGO palabras aleatorias de la categoría
    del minijuego que el estudiante aún no haya desbloqueado.
    """
    from .models import VocabularyItem, VocabularioDesbloqueado

    ya_desbloqueados = set(
        VocabularioDesbloqueado.objects.filter(
            estudiante=estudiante
        ).values_list('item_id', flat=True)
    )

    candidatos = list(
        VocabularyItem.objects.filter(category=game.category, is_active=True)
        .exclude(pk__in=ya_desbloqueados)
    )
    if not candidatos:
        return []

    elegidos = _random.sample(candidatos, min(PALABRAS_POR_MINIJUEGO, len(candidatos)))
    nuevos = [
        VocabularioDesbloqueado(estudiante=estudiante, item=item, fuente='minijuego')
        for item in elegidos
    ]
    if nuevos:
        VocabularioDesbloqueado.objects.bulk_create(nuevos, ignore_conflicts=True)

    return elegidos


@transaction.atomic
def verificar_hitos_vocabulario(estudiante):
    """Verifica si el estudiante alcanzó nuevos hitos de vocabulario y otorga huesos.

    Devuelve lista de (cantidad, huesos) para los hitos recién alcanzados.
    """
    from .models import VocabularioDesbloqueado, HitoVocabulario
    from apps.games.models import HuesoTransaccion

    total = VocabularioDesbloqueado.objects.filter(estudiante=estudiante).count()
    hitos_ya_entregados = set(
        HitoVocabulario.objects.filter(
            estudiante=estudiante
        ).values_list('palabras_cantidad', flat=True)
    )

    nuevos_hitos = []
    for cantidad, huesos in HITOS_VOCAB:
        if total >= cantidad and cantidad not in hitos_ya_entregados:
            HitoVocabulario.objects.create(
                estudiante=estudiante,
                palabras_cantidad=cantidad,
                huesos_ganados=huesos,
            )
            estudiante.huesos += huesos
            estudiante.save(update_fields=['huesos'])
            HuesoTransaccion.objects.create(
                user=estudiante,
                tipo='ganado',
                cantidad=huesos,
                descripcion=f'📚 ¡Hito de vocabulario! Desbloqueaste {cantidad} palabras',
            )
            nuevos_hitos.append((cantidad, huesos))

    return nuevos_hitos


def get_proximo_hito(total_desbloqueadas):
    """Devuelve (cantidad, huesos, progreso_pct) del próximo hito sin alcanzar."""
    prev = 0
    for cantidad, huesos in HITOS_VOCAB:
        if total_desbloqueadas < cantidad:
            rango = cantidad - prev
            progreso = total_desbloqueadas - prev
            pct = int((progreso / rango) * 100)
            return {'cantidad': cantidad, 'huesos': huesos, 'pct': pct, 'faltan': cantidad - total_desbloqueadas}
        prev = cantidad
    return None
