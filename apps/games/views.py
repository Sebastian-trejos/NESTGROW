from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import json

from .models import Game, UserProgress, Score, Logro, LogroUsuario, HuesoTransaccion, clasificar_puntaje, Artwork, PaintingWord
from .forms import GameForm, CategoryForm, VocabularyItemForm
from apps.content.models import VocabularyItem, Category
from apps.accounts.decorators import profesor_required


# ── Helpers ───────────────────────────────────────────────────────────────────

def verificar_logros(user):
    """Check and award any new badges. Returns list of newly unlocked badges."""
    nuevos = []
    juegos_completados = UserProgress.objects.filter(user=user, completed=True).count()
    puntaje_total = getattr(getattr(user, 'estudiante_profile', None), 'puntos_totales', 0)
    score_perfecto = Score.objects.filter(user=user).filter(score__gte=90).count()

    CONDICIONES = [
        # (condicion_slug, check_value)
        ('primera_victoria', juegos_completados >= 1),
        ('cinco_juegos', juegos_completados >= 5),
        ('diez_juegos', juegos_completados >= 10),
        ('50_puntos', puntaje_total >= 50),
        ('100_puntos', puntaje_total >= 100),
        ('perfeccionista', score_perfecto >= 1),
        ('tres_perfectos', score_perfecto >= 3),
    ]

    for slug, condicion_met in CONDICIONES:
        if condicion_met:
            try:
                logro = Logro.objects.get(nombre__icontains=slug.replace('_', ' '), is_active=True)
            except Logro.DoesNotExist:
                continue
            _, created = LogroUsuario.objects.get_or_create(user=user, logro=logro)
            if created:
                nuevos.append(logro)

    return nuevos


def otorgar_huesos(user, cantidad, descripcion):
    """Give Milo Bones to a user."""
    user.huesos += cantidad
    user.save(update_fields=['huesos'])
    HuesoTransaccion.objects.create(
        user=user, tipo='ganado', cantidad=cantidad, descripcion=descripcion
    )


# ── Student views ─────────────────────────────────────────────────────────────

@login_required
def game_list(request):
    games = Game.active.select_related('category').all()
    categories = Category.active.all()
    category_filter = request.GET.get('categoria')
    if category_filter:
        games = games.filter(category__id=category_filter)

    # Get unread badge notifications
    logros_nuevos = []
    if request.user.role == 'estudiante':
        logros_nuevos = LogroUsuario.objects.filter(
            user=request.user, visto=False
        ).select_related('logro')

    return render(request, 'games/game_list.html', {
        'games': games,
        'categories': categories,
        'selected_category': category_filter,
        'logros_nuevos': logros_nuevos,
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
        'painting': 'games/painting.html',
    }
    template = template_map.get(game.game_type, 'games/game_detail.html')

    # Get painting words if painting game
    painting_words = []
    if game.game_type == 'painting':
        painting_words = list(game.painting_words.values_list('word', flat=True))

    context = {
        'game': game,
        'vocabulary': vocabulary,
        'progress': progress,
        'top_scores': top_scores,
        'painting_words_json': json.dumps(painting_words),
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
def ranking_salon(request):
    """Classroom ranking view."""
    if request.user.role != 'estudiante':
        return redirect('accounts:dashboard')

    estudiante = request.user.estudiante_profile
    salon = estudiante.salon
    if not salon:
        messages.info(request, 'Únete a un salón para ver el ranking.')
        return redirect('accounts:dashboard_estudiante')

    compañeros = salon.estudiantes.select_related('user').order_by('-puntos_totales')
    return render(request, 'games/ranking_salon.html', {
        'salon': salon,
        'compañeros': compañeros,
        'mi_perfil': estudiante,
    })


@login_required
def mis_logros(request):
    """View all unlocked badges."""
    logros_obtenidos = LogroUsuario.objects.filter(
        user=request.user
    ).select_related('logro').order_by('-created_at')
    todos_logros = Logro.objects.filter(is_active=True)
    ids_obtenidos = set(lu.logro_id for lu in logros_obtenidos)

    # Mark as seen
    LogroUsuario.objects.filter(user=request.user, visto=False).update(visto=True)

    return render(request, 'games/mis_logros.html', {
        'logros_obtenidos': logros_obtenidos,
        'todos_logros': todos_logros,
        'ids_obtenidos': ids_obtenidos,
    })


@login_required
@require_POST
def marcar_logro_visto(request):
    """AJAX: mark badge notification as seen."""
    LogroUsuario.objects.filter(user=request.user, visto=False).update(visto=True)
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def save_score(request):
    """AJAX endpoint to save game score."""
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        score_val = int(data.get('score', 0))
        max_score_val = int(data.get('max_score', score_val))
        time_spent = int(data.get('time_spent', 0))
        completed = data.get('completed', False)

        game = get_object_or_404(Game, pk=game_id)

        # Percentage and classification
        pct = int((score_val / max_score_val) * 100) if max_score_val > 0 else 0
        clasificacion = clasificar_puntaje(pct)

        # Save score record
        Score.objects.create(
            user=request.user, game=game,
            score=score_val, max_score=max_score_val, time_spent=time_spent
        )

        # Update progress
        progress, _ = UserProgress.objects.get_or_create(user=request.user, game=game)
        progress.attempts += 1
        progress.time_spent += time_spent
        progress.max_score = max_score_val
        if score_val > progress.score:
            progress.score = score_val
        if completed:
            progress.completed = True
        progress.save()

        # Update student points + huesos
        nuevos_logros = []
        huesos_ganados = 0
        subio_nivel = False
        nuevo_nivel = 0
        if request.user.role == 'estudiante' and hasattr(request.user, 'estudiante_profile'):
            ep = request.user.estudiante_profile
            ep.puntos_totales += score_val
            # Don't call ep.save() here - actualizar_nivel() handles the save
            subio_nivel = ep.actualizar_nivel()
            nuevo_nivel = ep.nivel
            request.user.refresh_from_db()

            # Award Huesos based on classification
            huesos_map = {'perfecto': 5, 'alto': 3, 'basico': 2, 'bajo': 1}
            huesos_ganados = huesos_map.get(clasificacion[0], 1)
            otorgar_huesos(request.user, huesos_ganados,
                           f'Juego: {game.title} ({clasificacion[1]})')

            # Check badges
            nuevos_logros = verificar_logros(request.user)

        return JsonResponse({
            'status': 'ok',
            'score': score_val,
            'max_score': max_score_val,
            'percentage': pct,
            'clasificacion_key': clasificacion[0],
            'clasificacion_label': clasificacion[1],
            'clasificacion_color': clasificacion[2],
            'huesos_ganados': huesos_ganados,
            'total_huesos': request.user.huesos,
            'subio_nivel': subio_nivel,
            'nuevo_nivel': nuevo_nivel,
            'nuevos_logros': [
                {'nombre': l.nombre, 'icono': l.icono, 'descripcion': l.descripcion}
                for l in nuevos_logros
            ],
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ── Professor management views (unchanged) ───────────────────────────────────

@login_required
@profesor_required
def gestionar_categorias(request):
    categorias = Category.objects.all().order_by('order', 'name')
    return render(request, 'games/profesor/gestionar_categorias.html', {'categorias': categorias})


@login_required
@profesor_required
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ ¡Categoría creada!')
            return redirect('games:gestionar_categorias')
    else:
        form = CategoryForm()
    return render(request, 'games/profesor/categoria_form.html', {
        'form': form, 'titulo': 'Nueva Categoría', 'accion': 'Crear'})


@login_required
@profesor_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Categoría actualizada.')
            return redirect('games:gestionar_categorias')
    else:
        form = CategoryForm(instance=categoria)
    return render(request, 'games/profesor/categoria_form.html', {
        'form': form, 'titulo': f'Editar: {categoria.name}', 'accion': 'Guardar'})


@login_required
@profesor_required
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, '🗑️ Categoría eliminada.')
        return redirect('games:gestionar_categorias')
    return render(request, 'games/profesor/confirmar_eliminar.html', {
        'objeto': categoria, 'tipo': 'categoría', 'volver': 'games:gestionar_categorias'})


@login_required
@profesor_required
def gestionar_vocabulario(request, categoria_pk):
    categoria = get_object_or_404(Category, pk=categoria_pk)
    vocabulario = categoria.vocabulary.all()
    return render(request, 'games/profesor/gestionar_vocabulario.html', {
        'categoria': categoria, 'vocabulario': vocabulario})


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
        'form': form, 'categoria': categoria, 'titulo': 'Añadir Palabra', 'accion': 'Añadir'})


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
        'form': form, 'categoria': item.category,
        'titulo': f'Editar: {item.word_en}', 'accion': 'Guardar'})


@login_required
@profesor_required
def eliminar_vocabulario(request, pk):
    item = get_object_or_404(VocabularyItem, pk=pk)
    categoria_pk = item.category.pk
    if request.method == 'POST':
        item.delete()
        messages.success(request, '🗑️ Palabra eliminada.')
        return redirect('games:gestionar_vocabulario', categoria_pk=categoria_pk)
    return render(request, 'games/profesor/confirmar_eliminar.html', {
        'objeto': item, 'tipo': 'palabra',
        'volver_url': f'/juegos/vocabulario/{categoria_pk}/'})


@login_required
@profesor_required
def gestionar_juegos(request):
    juegos = Game.objects.select_related('category').order_by('order', 'title')
    categorias = Category.objects.all()
    return render(request, 'games/profesor/gestionar_juegos.html', {
        'juegos': juegos, 'categorias': categorias})


@login_required
@profesor_required
def crear_juego(request):
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES)
        if form.is_valid():
            juego = form.save()
            messages.success(request, f'🎮 Juego "{juego.title}" creado!')
            return redirect('games:gestionar_juegos')
    else:
        form = GameForm()
    return render(request, 'games/profesor/juego_form.html', {
        'form': form, 'titulo': 'Crear Nuevo Juego', 'accion': 'Crear juego'})


@login_required
@profesor_required
def editar_juego(request, pk):
    juego = get_object_or_404(Game, pk=pk)
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES, instance=juego)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Juego "{juego.title}" actualizado!')
            return redirect('games:gestionar_juegos')
    else:
        form = GameForm(instance=juego)
    return render(request, 'games/profesor/juego_form.html', {
        'form': form, 'titulo': f'Editar: {juego.title}', 'accion': 'Guardar', 'juego': juego})


@login_required
@profesor_required
def eliminar_juego(request, pk):
    juego = get_object_or_404(Game, pk=pk)
    if request.method == 'POST':
        juego.delete()
        messages.success(request, f'🗑️ Juego eliminado.')
        return redirect('games:gestionar_juegos')
    return render(request, 'games/profesor/confirmar_eliminar.html', {
        'objeto': juego, 'tipo': 'juego', 'volver': 'games:gestionar_juegos'})


@login_required
@profesor_required
def toggle_juego(request, pk):
    juego = get_object_or_404(Game, pk=pk)
    juego.is_active = not juego.is_active
    juego.save()
    estado = 'activado' if juego.is_active else 'desactivado'
    messages.success(request, f'✅ Juego "{juego.title}" {estado}.')
    return redirect('games:gestionar_juegos')


# ── Museo Virtual ─────────────────────────────────────────────────────────────

@login_required
def guardar_obra(request):
    """Guarda la obra de arte del estudiante."""
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        canvas_data = data.get('canvas_data')
        vocabulary_id = data.get('vocabulary_id')
        title = data.get('title', 'Sin título')

        game = get_object_or_404(Game, pk=game_id)
        vocab_item = None
        if vocabulary_id:
            from apps.content.models import VocabularyItem
            try:
                vocab_item = VocabularyItem.objects.get(pk=vocabulary_id)
            except VocabularyItem.DoesNotExist:
                pass

        Artwork.objects.create(
            user=request.user, game=game,
            vocabulary_item=vocab_item,
            canvas_data=canvas_data, title=title,
        )

        # Award points
        if request.user.role == 'estudiante' and hasattr(request.user, 'estudiante_profile'):
            ep = request.user.estudiante_profile
            ep.puntos_totales += game.points_reward
            ep.actualizar_nivel()
            otorgar_huesos(request.user, 2, f'Juego de pintar: {game.title}')

        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def museo_virtual(request):
    """Museo virtual: estudiante ve sus obras, profesor ve las de sus estudiantes."""
    if request.user.role == 'profesor':
        profile = request.user.profesor_profile
        estudiantes = profile.estudiantes.select_related('user').all()
        artworks = Artwork.objects.filter(
            user__estudiante_profile__profesor=profile
        ).select_related('user', 'vocabulary_item').order_by('-created_at')
        estudiante_filtro = request.GET.get('estudiante')
        if estudiante_filtro:
            artworks = artworks.filter(user__pk=estudiante_filtro)
        return render(request, 'games/museo_virtual.html', {
            'artworks': artworks,
            'estudiantes': estudiantes,
            'estudiante_filtro': estudiante_filtro,
        })
    else:
        artworks = Artwork.objects.filter(
            user=request.user
        ).select_related('vocabulary_item').order_by('-created_at')
        return render(request, 'games/museo_virtual.html', {'artworks': artworks})


@login_required
def museo_estudiante(request, user_pk):
    """Profesor ve las obras de un estudiante específico."""
    from apps.accounts.models import EstudianteProfile
    from django.contrib.auth import get_user_model
    User = get_user_model()
    estudiante_user = get_object_or_404(User, pk=user_pk)
    if request.user.role == 'profesor':
        profile = request.user.profesor_profile
        if not EstudianteProfile.objects.filter(user=estudiante_user, profesor=profile).exists():
            messages.error(request, 'Este estudiante no pertenece a tu clase.')
            return redirect('accounts:dashboard_profesor')
    artworks = Artwork.objects.filter(
        user=estudiante_user
    ).select_related('vocabulary_item').order_by('-created_at')
    return render(request, 'games/museo_virtual.html', {
        'artworks': artworks,
        'estudiante_visto': estudiante_user,
    })
