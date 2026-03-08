from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import json

from .models import Game, UserProgress, Score
from .forms import GameForm, CategoryForm, VocabularyItemForm
from apps.content.models import VocabularyItem, Category
from apps.accounts.decorators import profesor_required


@login_required
def game_list(request):
    games = Game.active.select_related('category').all()
    categories = Category.active.all()
    category_filter = request.GET.get('categoria')
    if category_filter:
        games = games.filter(category__id=category_filter)
    return render(request, 'games/game_list.html', {
        'games': games,
        'categories': categories,
        'selected_category': category_filter,
    })


@login_required
def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk, is_active=True)
    vocabulary = VocabularyItem.objects.filter(category=game.category, is_active=True)
    progress, _ = UserProgress.objects.get_or_create(user=request.user, game=game)
    top_scores = Score.objects.filter(game=game).select_related('user').order_by('-score')[:5]

    template_map = {
        'drag_and_drop': 'games/drag_and_drop.html',
        'word_search': 'games/word_search.html',
        'puzzle': 'games/puzzle.html',
        'audio_matching': 'games/audio_game.html',
    }
    template = template_map.get(game.game_type, 'games/game_detail.html')

    context = {
        'game': game,
        'vocabulary': vocabulary,
        'progress': progress,
        'top_scores': top_scores,
        'vocabulary_json': json.dumps([
            {
                'id': v.id,
                'word_en': v.word_en,
                'word_es': v.word_es,
                'image': v.image.url if v.image else None,
                'audio': v.audio.url if v.audio else None,
            }
            for v in vocabulary
        ]),
    }
    return render(request, template, context)


@login_required
@require_POST
def save_score(request):
    """AJAX endpoint to save game score."""
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        score_val = int(data.get('score', 0))
        time_spent = int(data.get('time_spent', 0))
        completed = data.get('completed', False)

        game = get_object_or_404(Game, pk=game_id)

        # Save individual attempt
        Score.objects.create(user=request.user, game=game, score=score_val, time_spent=time_spent)

        # Update progress
        progress, created = UserProgress.objects.get_or_create(user=request.user, game=game)
        progress.attempts += 1
        progress.time_spent += time_spent
        if score_val > progress.score:
            progress.score = score_val
        if completed:
            progress.completed = True
        progress.save()

        # Update student points
        if request.user.role == 'estudiante' and hasattr(request.user, 'estudiante_profile'):
            ep = request.user.estudiante_profile
            ep.puntos_totales += score_val
            ep.save()
            ep.actualizar_nivel()

        return JsonResponse({
            'status': 'ok',
            'new_score': score_val,
            'total_points': getattr(getattr(request.user, 'estudiante_profile', None), 'puntos_totales', 0),
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ============================================================
# PROFESOR — Gestión de Categorías
# ============================================================

@login_required
@profesor_required
def gestionar_categorias(request):
    categorias = Category.objects.all().order_by('order', 'name')
    return render(request, 'games/profesor/gestionar_categorias.html', {
        'categorias': categorias,
    })


@login_required
@profesor_required
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ ¡Categoría creada exitosamente!')
            return redirect('games:gestionar_categorias')
    else:
        form = CategoryForm()
    return render(request, 'games/profesor/categoria_form.html', {
        'form': form,
        'titulo': 'Nueva Categoría',
        'accion': 'Crear',
    })


@login_required
@profesor_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ ¡Categoría actualizada!')
            return redirect('games:gestionar_categorias')
    else:
        form = CategoryForm(instance=categoria)
    return render(request, 'games/profesor/categoria_form.html', {
        'form': form,
        'titulo': f'Editar: {categoria.name}',
        'accion': 'Guardar cambios',
        'categoria': categoria,
    })


@login_required
@profesor_required
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        nombre = categoria.name
        categoria.delete()
        messages.success(request, f'🗑️ Categoría "{nombre}" eliminada.')
        return redirect('games:gestionar_categorias')
    return render(request, 'games/profesor/confirmar_eliminar.html', {
        'objeto': categoria,
        'tipo': 'categoría',
        'volver': 'games:gestionar_categorias',
    })


# ============================================================
# PROFESOR — Gestión de Vocabulario
# ============================================================

@login_required
@profesor_required
def gestionar_vocabulario(request, categoria_pk):
    categoria = get_object_or_404(Category, pk=categoria_pk)
    vocabulario = categoria.vocabulary.all()
    return render(request, 'games/profesor/gestionar_vocabulario.html', {
        'categoria': categoria,
        'vocabulario': vocabulario,
    })


@login_required
@profesor_required
def crear_vocabulario(request, categoria_pk):
    categoria = get_object_or_404(Category, pk=categoria_pk)
    if request.method == 'POST':
        form = VocabularyItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.category = categoria
            item.save()
            messages.success(request, f'✅ Palabra "{item.word_en}" añadida!')
            return redirect('games:gestionar_vocabulario', categoria_pk=categoria.pk)
    else:
        form = VocabularyItemForm()
    return render(request, 'games/profesor/vocabulario_form.html', {
        'form': form,
        'categoria': categoria,
        'titulo': 'Añadir Palabra',
        'accion': 'Añadir',
    })


@login_required
@profesor_required
def editar_vocabulario(request, pk):
    item = get_object_or_404(VocabularyItem, pk=pk)
    if request.method == 'POST':
        form = VocabularyItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Palabra "{item.word_en}" actualizada!')
            return redirect('games:gestionar_vocabulario', categoria_pk=item.category.pk)
    else:
        form = VocabularyItemForm(instance=item)
    return render(request, 'games/profesor/vocabulario_form.html', {
        'form': form,
        'categoria': item.category,
        'titulo': f'Editar: {item.word_en}',
        'accion': 'Guardar cambios',
    })


@login_required
@profesor_required
def eliminar_vocabulario(request, pk):
    item = get_object_or_404(VocabularyItem, pk=pk)
    categoria_pk = item.category.pk
    if request.method == 'POST':
        nombre = item.word_en
        item.delete()
        messages.success(request, f'🗑️ Palabra "{nombre}" eliminada.')
        return redirect('games:gestionar_vocabulario', categoria_pk=categoria_pk)
    return render(request, 'games/profesor/confirmar_eliminar.html', {
        'objeto': item,
        'tipo': 'palabra',
        'volver_url': f'/juegos/vocabulario/{categoria_pk}/',
    })


# ============================================================
# PROFESOR — Gestión de Juegos
# ============================================================

@login_required
@profesor_required
def gestionar_juegos(request):
    juegos = Game.objects.select_related('category').order_by('order', 'title')
    categorias = Category.objects.all()
    return render(request, 'games/profesor/gestionar_juegos.html', {
        'juegos': juegos,
        'categorias': categorias,
    })


@login_required
@profesor_required
def crear_juego(request):
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES)
        if form.is_valid():
            juego = form.save()
            messages.success(request, f'🎮 ¡Juego "{juego.title}" creado exitosamente!')
            return redirect('games:gestionar_juegos')
    else:
        form = GameForm()
    return render(request, 'games/profesor/juego_form.html', {
        'form': form,
        'titulo': 'Crear Nuevo Juego',
        'accion': 'Crear juego',
    })


@login_required
@profesor_required
def editar_juego(request, pk):
    juego = get_object_or_404(Game, pk=pk)
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES, instance=juego)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ ¡Juego "{juego.title}" actualizado!')
            return redirect('games:gestionar_juegos')
    else:
        form = GameForm(instance=juego)
    return render(request, 'games/profesor/juego_form.html', {
        'form': form,
        'titulo': f'Editar: {juego.title}',
        'accion': 'Guardar cambios',
        'juego': juego,
    })


@login_required
@profesor_required
def eliminar_juego(request, pk):
    juego = get_object_or_404(Game, pk=pk)
    if request.method == 'POST':
        nombre = juego.title
        juego.delete()
        messages.success(request, f'🗑️ Juego "{nombre}" eliminado.')
        return redirect('games:gestionar_juegos')
    return render(request, 'games/profesor/confirmar_eliminar.html', {
        'objeto': juego,
        'tipo': 'juego',
        'volver': 'games:gestionar_juegos',
    })


@login_required
@profesor_required
def toggle_juego(request, pk):
    """Activar/desactivar juego con un click."""
    juego = get_object_or_404(Game, pk=pk)
    juego.is_active = not juego.is_active
    juego.save()
    estado = 'activado' if juego.is_active else 'desactivado'
    messages.success(request, f'✅ Juego "{juego.title}" {estado}.')
    return redirect('games:gestionar_juegos')
