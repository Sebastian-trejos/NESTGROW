"""Vocabulary unlock logic and milestone rewards for Fase 5."""
from django.db import transaction


HITOS_VOCAB = [
    (10, 2),
    (25, 5),
    (50, 10),
    (100, 20),
    (200, 40),
]

PALABRAS_POR_TALLER = 3  # palabras nuevas desbloqueadas al completar un taller


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


def desbloquear_vocabulario_taller(sesion, palabras_por_bloque=PALABRAS_POR_TALLER):
    """Desbloquea N palabras de las categorías asociadas al taller al completarlo.

    Selecciona las siguientes palabras ordenadas por `orden` que el estudiante
    aún no ha desbloqueado.
    """
    from .models import VocabularyItem, VocabularioDesbloqueado

    taller = sesion.taller
    categorias = taller.categorias_vocabulario.all()
    if not categorias.exists():
        return []

    estudiante = sesion.estudiante
    ya_desbloqueados = set(
        VocabularioDesbloqueado.objects.filter(
            estudiante=estudiante
        ).values_list('item_id', flat=True)
    )

    items_candidatos = (
        VocabularyItem.objects.filter(
            category__in=categorias, is_active=True
        )
        .exclude(pk__in=ya_desbloqueados)
        .order_by('category__order', 'orden')
    )[:palabras_por_bloque]

    nuevos = [
        VocabularioDesbloqueado(
            estudiante=estudiante,
            item=item,
            fuente='taller',
        )
        for item in items_candidatos
    ]
    if nuevos:
        VocabularioDesbloqueado.objects.bulk_create(nuevos, ignore_conflicts=True)

    return list(items_candidatos)


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
