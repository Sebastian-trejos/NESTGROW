import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, VocabularyItem, VocabularioDesbloqueado
from .utils import desbloquear_palabras_iniciales, get_proximo_hito


@login_required
def category_list(request):
    # Los estudiantes van directamente a su vocabulario progresivo
    if request.user.role == 'estudiante':
        return redirect('content:mi_vocabulario')
    categories = Category.active.exclude(name='Pintura Libre')
    return render(request, 'content/category_list.html', {'categories': categories})


@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk, is_active=True)
    vocabulary = category.vocabulary.filter(is_active=True)
    return render(request, 'content/vocabulary_detail.html', {
        'category': category,
        'vocabulary': vocabulary,
    })


@login_required
def mi_vocabulario(request):
    """Vista de vocabulario progresivo para el estudiante."""
    user = request.user

    # Asegurar que tiene palabras iniciales (lazy init para cuentas antiguas)
    if not VocabularioDesbloqueado.objects.filter(estudiante=user).exists():
        desbloquear_palabras_iniciales(user)

    desbloqueados_ids = set(
        VocabularioDesbloqueado.objects.filter(
            estudiante=user
        ).values_list('item_id', flat=True)
    )

    categorias_data = []
    total_desbloqueadas = 0
    total_palabras = 0

    for cat in Category.active.all():
        items = list(cat.vocabulary.filter(is_active=True).order_by('orden', 'word_en'))
        if not items:
            continue

        desbloqueadas = [it for it in items if it.pk in desbloqueados_ids]
        bloqueadas = [it for it in items if it.pk not in desbloqueados_ids]

        total_desbloqueadas += len(desbloqueadas)
        total_palabras += len(items)

        pct = int(len(desbloqueadas) / len(items) * 100) if items else 0

        categorias_data.append({
            'categoria': cat,
            'desbloqueadas': desbloqueadas,
            'bloqueadas': bloqueadas,
            'total': len(items),
            'pct': pct,
        })

    # Palabra del día
    palabra_del_dia = None
    if desbloqueados_ids:
        candidatos = list(
            VocabularyItem.objects.filter(
                pk__in=desbloqueados_ids,
                is_active=True,
            ).exclude(descripcion_es='')
        )
        if candidatos:
            # Seed con la fecha para que sea la misma todo el día
            from django.utils import timezone
            seed = int(timezone.now().strftime('%Y%m%d')) + user.pk
            rng = random.Random(seed)
            palabra_del_dia = rng.choice(candidatos)

    proximo_hito = get_proximo_hito(total_desbloqueadas)

    pct_global = int(total_desbloqueadas / total_palabras * 100) if total_palabras else 0

    return render(request, 'content/mi_vocabulario.html', {
        'categorias_data': categorias_data,
        'total_desbloqueadas': total_desbloqueadas,
        'total_palabras': total_palabras,
        'pct_global': pct_global,
        'proximo_hito': proximo_hito,
        'palabra_del_dia': palabra_del_dia,
    })
