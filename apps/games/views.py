from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages
import json

from .models import Game, UserProgress, Score, Logro, LogroUsuario, HuesoTransaccion, clasificar_puntaje, Artwork, PaintingWord, PuzzleImage, TiendaItem, InventarioEstudiante, WordSearchWord, MemoriaCard
from .forms import GameForm, CategoryForm, VocabularyItemForm
from apps.content.models import VocabularyItem, Category
from apps.accounts.decorators import profesor_required, estudiante_required


# ── Vocabulario (JSON cliente) ───────────────────────────────────────────────

def vocabulary_payload_for_game(game, vocabulary):
    """Lista de objetos coherentes para minijuegos, tomados del vocabulario de la categoría."""
    return [
        {
            'id': v.id,
            'word_en': v.word_en,
            'word_es': v.word_es,
            'image': v.display_image_url,
            'audio': v.audio.url if v.audio else None,
            'emoji': v.emoji or '',
            'orden': getattr(v, 'orden', 0),
            'item_difficulty': v.difficulty,
        }
        for v in vocabulary.order_by('orden', 'word_en')
    ]


def vocabulary_json_for_game(game, vocabulary):
    return json.dumps(vocabulary_payload_for_game(game, vocabulary))


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

        # Ocultar minijuegos del período activo que ya fueron completados y revisados
        try:
            from apps.talleres.models import RegistroMinijuegoPeriodo
            from django.utils import timezone as tz
            perfil = request.user.estudiante_profile
            if perfil.salon_id:
                hoy = tz.now().date()
                juegos_revisados_ids = RegistroMinijuegoPeriodo.objects.filter(
                    estudiante=request.user,
                    revisado=True,
                    periodo__salon_id=perfil.salon_id,
                    periodo__is_activo=True,
                    periodo__cerrado=False,
                    periodo__fecha_fin__gte=hoy,
                ).values_list('asignacion__game_id', flat=True)
                games = games.exclude(pk__in=juegos_revisados_ids)
        except Exception:
            pass

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
        'memoria': 'games/memoria.html',
        'ahorcado': 'games/ahorcado.html',
        'globos': 'games/globos.html',
        'comparacion': 'games/comparacion.html',
    }
    template = template_map.get(game.game_type, 'games/game_detail.html')

    # Get painting words if painting game
    painting_words = []
    if game.game_type == 'painting':
        painting_words = list(game.painting_words.values_list('word', flat=True))

    # Get puzzle images if puzzle game
    puzzle_images_json = '[]'
    if game.game_type == 'puzzle':
        puzzle_images_json = json.dumps([
            {'image': pi.image.url, 'word_en': pi.title}
            for pi in game.puzzle_images.all()
        ])

    # Get word search custom words if word_search game
    word_search_words_json = '[]'
    if game.game_type == 'word_search':
        ws_words = list(game.word_search_words.values_list('word', flat=True))
        if ws_words:
            word_search_words_json = json.dumps(ws_words)

    # Get memoria custom cards if memoria game
    memoria_cards_json = '[]'
    if game.game_type == 'memoria':
        cards = game.memoria_cards.all()
        if cards.exists():
            memoria_cards_json = json.dumps([
                {
                    'id': c.pk,
                    'label_es': c.label_es,
                    'label_en': c.label_en or c.label_es,
                    'image': c.image.url if c.image else '',
                }
                for c in cards
            ])

    vocabulary_json = vocabulary_json_for_game(game, vocabulary)

    logros_nuevos = []
    if request.user.role == 'estudiante':
        logros_nuevos = LogroUsuario.objects.filter(
            user=request.user, visto=False).select_related('logro')
    context = {
        'game': game,
        'logros_nuevos': logros_nuevos,
        'vocabulary': vocabulary,
        'progress': progress,
        'top_scores': top_scores,
        'painting_words_json': json.dumps(painting_words),
        'words_json': json.dumps(painting_words),
        'vocabulary_json': vocabulary_json,
        'puzzle_images_json': puzzle_images_json,
        'word_search_words_json': word_search_words_json,
        'memoria_cards_json': memoria_cards_json,
    }
    return render(request, template, context)


@xframe_options_exempt
@login_required
def game_embed(request, pk):
    """Render a game without navbar/footer, for embedding inside talleres."""
    game = get_object_or_404(Game, pk=pk)
    vocabulary = VocabularyItem.objects.filter(category=game.category, is_active=True)
    progress, _ = UserProgress.objects.get_or_create(user=request.user, game=game)
    top_scores = Score.objects.filter(game=game).select_related('user').order_by('-score')[:5]

    template_map = {
        'drag_and_drop': 'games/drag_and_drop.html',
        'word_search': 'games/word_search.html',
        'puzzle': 'games/puzzle.html',
        'audio_matching': 'games/audio_game.html',
        'painting': 'games/painting.html',
        'memoria': 'games/memoria.html',
        'ahorcado': 'games/ahorcado.html',
        'globos': 'games/globos.html',
        'comparacion': 'games/comparacion.html',
    }
    template = template_map.get(game.game_type, 'games/game_detail.html')

    painting_words = []
    if game.game_type == 'painting':
        painting_words = list(game.painting_words.values_list('word', flat=True))

    puzzle_images_json = '[]'
    if game.game_type == 'puzzle':
        puzzle_images_json = json.dumps([
            {'image': pi.image.url, 'word_en': pi.title}
            for pi in game.puzzle_images.all()
        ])

    word_search_words_json = '[]'
    if game.game_type == 'word_search':
        ws_words = list(game.word_search_words.values_list('word', flat=True))
        if ws_words:
            word_search_words_json = json.dumps(ws_words)

    memoria_cards_json = '[]'
    if game.game_type == 'memoria':
        cards = game.memoria_cards.all()
        if cards.exists():
            memoria_cards_json = json.dumps([
                {
                    'id': c.pk,
                    'label_es': c.label_es,
                    'label_en': c.label_en or c.label_es,
                    'image': c.image.url if c.image else '',
                }
                for c in cards
            ])

    vocabulary_json = vocabulary_json_for_game(game, vocabulary)

    taller_mode = request.GET.get('taller') == '1'
    return render(request, template, {
        'game': game,
        'vocabulary': vocabulary,
        'progress': progress,
        'top_scores': top_scores,
        'painting_words_json': json.dumps(painting_words),
        'words_json': json.dumps(painting_words),
        'vocabulary_json': vocabulary_json,
        'puzzle_images_json': puzzle_images_json,
        'word_search_words_json': word_search_words_json,
        'memoria_cards_json': memoria_cards_json,
        'embedded': True,
        'taller_mode': taller_mode,
    })


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

    ranking = sorted(
        salon.estudiantes.select_related('user').all(),
        key=lambda p: p.puntos_acumulados,
        reverse=True,
    )

    logros_nuevos = []
    if request.user.role == 'estudiante':
        logros_nuevos = LogroUsuario.objects.filter(
            user=request.user, visto=False).select_related('logro')
    return render(request, 'games/ranking_salon.html', {
        'logros_nuevos': logros_nuevos,
        'salon': salon,
        'ranking': ranking,
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
        'logros_nuevos': [],
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
        primera_vez_completado = completed and not progress.completed   # True solo en la 1ª completion
        progress.attempts += 1
        progress.time_spent += time_spent
        progress.max_score = max_score_val
        if score_val > progress.score:
            progress.score = score_val
        if completed:
            progress.completed = True
        progress.save()

        nuevos_logros = []
        huesos_ganados = 0
        subio_nivel = False
        nuevo_nivel = 0
        registro_pk = None
        vocab_nuevas = 0
        if request.user.role == 'estudiante':
            # Otorgar XP igual al puntaje obtenido en el juego
            perfil = request.user.estudiante_profile
            perfil.puntos_totales += score_val
            subio_nivel = perfil.actualizar_nivel()
            nuevo_nivel = perfil.nivel
            nuevos_logros = verificar_logros(request.user)

            # Desbloquear vocabulario en la primera completion del minijuego
            if primera_vez_completado:
                try:
                    from apps.content.utils import desbloquear_vocabulario_minijuego, verificar_hitos_vocabulario
                    nuevas = desbloquear_vocabulario_minijuego(request.user, game)
                    vocab_nuevas = len(nuevas)
                    if vocab_nuevas:
                        verificar_hitos_vocabulario(request.user)
                except Exception:
                    pass   # nunca interrumpir el flujo del juego

            # Registrar completado en período activo (si existe asignación)
            registro_pk = None
            try:
                from apps.talleres.models import AsignacionMinijuego, RegistroMinijuegoPeriodo
                from django.utils import timezone as tz
                perfil = request.user.estudiante_profile
                if perfil.salon_id:
                    hoy = tz.now().date()
                    asignacion = AsignacionMinijuego.objects.filter(
                        game_id=game_id,
                        periodo__salon_id=perfil.salon_id,
                        periodo__is_activo=True,
                        periodo__cerrado=False,
                        periodo__fecha_fin__gte=hoy,
                    ).select_related('periodo').first()
                    if asignacion:
                        registro, _ = RegistroMinijuegoPeriodo.objects.update_or_create(
                            asignacion=asignacion,
                            estudiante=request.user,
                            defaults={
                                'periodo': asignacion.periodo,
                                'score': score_val,
                                'max_score': max_score_val,
                                'completado': True,
                            },
                        )
                        registro_pk = registro.pk
            except Exception:
                registro_pk = None  # No interrumpir el flujo del juego por errores de período

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
            'registro_pk': registro_pk,  # pk del RegistroMinijuegoPeriodo, o null si no hay periodo
            'vocab_nuevas': vocab_nuevas,  # palabras desbloqueadas en esta partida (0 si no es 1ª vez)
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
            # Save painting words if painting game
            if juego.game_type == 'painting':
                raw = request.POST.get('painting_words', '[]')
                try:
                    words = json.loads(raw)
                except Exception:
                    words = []
                PaintingWord.objects.filter(game=juego).delete()
                for i, w in enumerate(words):
                    if w.strip():
                        PaintingWord.objects.create(game=juego, word=w.strip(), order=i)
            if juego.game_type == 'puzzle':
                total = int(request.POST.get('img_total_rows', 0))
                for i in range(total):
                    title = request.POST.get(f'puzzle_title_{i}', '').strip()
                    img_file = request.FILES.get(f'puzzle_file_{i}')
                    if title and img_file:
                        PuzzleImage.objects.create(
                            game=juego,
                            title=title,
                            image=img_file,
                            order=i,
                        )
            # Save word search words if word_search game
            if juego.game_type == 'word_search':
                raw = request.POST.get('word_search_words', '[]')
                try:
                    ws_words = json.loads(raw)
                except Exception:
                    ws_words = []
                WordSearchWord.objects.filter(game=juego).delete()
                for i, w in enumerate(ws_words):
                    if w.strip():
                        WordSearchWord.objects.create(game=juego, word=w.strip().upper(), order=i)
            messages.success(request, f'🎮 Juego "{juego.title}" creado correctamente.')
            return redirect('talleres:lista_periodos')
    else:
        form = GameForm()
    return render(request, 'games/profesor/juego_form.html', {
        'form': form, 'titulo': 'Crear Nuevo Juego', 'accion': 'Crear juego'})


@login_required
@profesor_required
def editar_juego(request, pk):
    juego = get_object_or_404(Game, pk=pk)
    painting_words = PaintingWord.objects.filter(game=juego)
    if request.method == 'POST':
        form = GameForm(request.POST, request.FILES, instance=juego)
        if form.is_valid():
            form.save()
            # Save painting words if painting game
            if juego.game_type == 'painting':
                raw = request.POST.get('painting_words', '[]')
                try:
                    words = json.loads(raw)
                except Exception:
                    words = []
                PaintingWord.objects.filter(game=juego).delete()
                for i, w in enumerate(words):
                    if w.strip():
                        PaintingWord.objects.create(game=juego, word=w.strip(), order=i)
            # Save word search words if word_search game
            if juego.game_type == 'word_search':
                raw = request.POST.get('word_search_words', '[]')
                try:
                    ws_words = json.loads(raw)
                except Exception:
                    ws_words = []
                WordSearchWord.objects.filter(game=juego).delete()
                for i, w in enumerate(ws_words):
                    if w.strip():
                        WordSearchWord.objects.create(game=juego, word=w.strip().upper(), order=i)
            messages.success(request, f'✅ Juego "{juego.title}" actualizado!')
            return redirect('talleres:lista_periodos')
    else:
        form = GameForm(instance=juego)
    puzzle_imagenes = (
        PuzzleImage.objects.filter(game=juego)
        if juego.game_type == 'puzzle' else []
    )
    word_search_words = WordSearchWord.objects.filter(game=juego) if juego.game_type == 'word_search' else []
    memoria_cards = MemoriaCard.objects.filter(game=juego) if juego.game_type == 'memoria' else []
    return render(request, 'games/profesor/juego_form.html', {
        'form': form, 'titulo': f'Editar: {juego.title}', 'accion': 'Guardar',
        'juego': juego, 'painting_words': painting_words,
        'word_search_words': word_search_words,
        'puzzle_imagenes': puzzle_imagenes,
        'juego_usa_imagenes': juego.game_type == 'puzzle',
        'memoria_cards': memoria_cards,
        'juego_usa_memoria': juego.game_type == 'memoria'})


@login_required
@profesor_required
def eliminar_juego(request, pk):
    juego = get_object_or_404(Game, pk=pk)
    next_url = request.GET.get('next') or request.POST.get('next', '')
    if request.method == 'POST':
        juego.delete()
        messages.success(request, '🗑️ Minijuego eliminado.')
        return redirect(next_url or 'games:gestionar_juegos')
    return render(request, 'games/profesor/confirmar_eliminar.html', {
        'objeto': juego, 'tipo': 'minijuego',
        'volver_url': next_url or None, 'volver': None if next_url else 'games:gestionar_juegos',
        'next_url': next_url})


@login_required
@profesor_required
def toggle_juego(request, pk):
    juego = get_object_or_404(Game, pk=pk)
    juego.is_active = not juego.is_active
    juego.save()
    estado = 'activado' if juego.is_active else 'desactivado'
    messages.success(request, f'✅ Juego "{juego.title}" {estado}.')
    return redirect('games:gestionar_juegos')


# ── Imágenes del Rompecabezas (PuzzleImage) ───────────────────────────────────

@login_required
@profesor_required
@require_POST
def api_imagen_agregar(request, game_pk):
    """Añade una PuzzleImage al rompecabezas (máximo 5)."""
    game = get_object_or_404(Game, pk=game_pk)
    if PuzzleImage.objects.filter(game=game).count() >= 5:
        return JsonResponse({'ok': False, 'error': 'Máximo 5 imágenes por rompecabezas.'})
    title = request.POST.get('title', '').strip()
    if not title:
        return JsonResponse({'ok': False, 'error': 'El nombre del rompecabezas es requerido.'})
    if 'image' not in request.FILES:
        return JsonResponse({'ok': False, 'error': 'La imagen es requerida.'})
    order = PuzzleImage.objects.filter(game=game).count()
    item = PuzzleImage.objects.create(
        game=game,
        title=title,
        image=request.FILES['image'],
        order=order,
    )
    return JsonResponse({'ok': True, 'item': {
        'pk': item.pk,
        'title': item.title,
        'image_url': item.image.url,
    }})


@login_required
@profesor_required
@require_POST
def api_imagen_eliminar(request, item_pk):
    """Elimina una PuzzleImage."""
    item = get_object_or_404(PuzzleImage, pk=item_pk)
    item.delete()
    return JsonResponse({'ok': True})


# ── MemoriaCard API ───────────────────────────────────────────────────────────

@login_required
@profesor_required
@require_POST
def api_memoria_card_agregar(request, game_pk):
    """Añade una MemoriaCard al memorama (máximo 12)."""
    game = get_object_or_404(Game, pk=game_pk)
    if MemoriaCard.objects.filter(game=game).count() >= 12:
        return JsonResponse({'ok': False, 'error': 'Máximo 12 tarjetas por memorama.'})
    label_es = request.POST.get('label_es', '').strip()
    label_en = request.POST.get('label_en', '').strip()
    if not label_es:
        return JsonResponse({'ok': False, 'error': 'El texto en español es requerido.'})
    order = MemoriaCard.objects.filter(game=game).count()
    card = MemoriaCard.objects.create(
        game=game,
        label_es=label_es,
        label_en=label_en,
        image=request.FILES.get('image'),
        order=order,
    )
    return JsonResponse({'ok': True, 'card': {
        'pk': card.pk,
        'label_es': card.label_es,
        'label_en': card.label_en,
        'image_url': card.image.url if card.image else '',
    }})


@login_required
@profesor_required
@require_POST
def api_memoria_card_eliminar(request, card_pk):
    """Elimina una MemoriaCard."""
    card = get_object_or_404(MemoriaCard, pk=card_pk)
    card.delete()
    return JsonResponse({'ok': True})


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

        # Los juegos en solitario no otorgan XP ni Huesos (solo los Talleres lo hacen)

        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@estudiante_required
def pintar_libre(request):
    """Canvas libre para el estudiante — crea una obra sin que el profe la haya asignado."""
    # Busca o crea un Game especial "Pintura Libre" para que Artwork.game no sea null
    from apps.content.models import Category
    categoria, _ = Category.objects.get_or_create(
        name='Pintura Libre',
        defaults={
            'name_en': 'Free Painting',
            'description': 'Obras creadas libremente por los estudiantes desde el museo.',
            'icon': '🖌️',
            'color': '#6C63FF',
        }
    )
    game, _ = Game.objects.get_or_create(
        title='Pintura Libre',
        game_type='painting',
        defaults={
            'title_en': 'Free Painting',
            'description': 'Canvas libre desde el museo virtual.',
            'category': categoria,
            'difficulty': 1,
        }
    )
    return render(request, 'games/painting_libre.html', {'game': game})


@require_POST
@login_required
@estudiante_required
def guardar_obra_libre(request):
    """Guarda una obra de pintura libre (sin palabra asignada)."""
    try:
        data = json.loads(request.body)
        canvas_data = data.get('canvas_data', '')
        title = (data.get('title') or '').strip() or 'Sin título'

        from apps.content.models import Category
        categoria, _ = Category.objects.get_or_create(
            name='Pintura Libre',
            defaults={
                'name_en': 'Free Painting',
                'description': 'Obras creadas libremente por los estudiantes desde el museo.',
                'icon': '🖌️',
                'color': '#6C63FF',
            }
        )
        game, _ = Game.objects.get_or_create(
            title='Pintura Libre',
            game_type='painting',
            defaults={
                'title_en': 'Free Painting',
                'description': 'Canvas libre desde el museo virtual.',
                'category': categoria,
                'difficulty': 1,
            }
        )

        Artwork.objects.create(
            user=request.user,
            game=game,
            vocabulary_item=None,
            canvas_data=canvas_data,
            title=title,
        )
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
@estudiante_required
def museo_global(request):
    """Foro visual: obras de todos los estudiantes del mismo salón, agrupadas por autor."""
    profile = request.user.estudiante_profile
    if not profile.salon:
        messages.warning(request, 'Únete a un salón para ver el museo global.')
        return redirect('games:museo_virtual')

    artworks_qs = (
        Artwork.objects
        .filter(user__estudiante_profile__salon=profile.salon)
        .select_related('user', 'vocabulary_item')
        .order_by('user__first_name', 'user__last_name', '-created_at')
    )

    # Agrupar por autor
    autores = {}
    for obra in artworks_qs:
        uid = obra.user_id
        if uid not in autores:
            autores[uid] = {'user': obra.user, 'obras': []}
        autores[uid]['obras'].append(obra)

    return render(request, 'games/museo_global.html', {
        'autores': list(autores.values()),
        'salon': profile.salon,
        'total_obras': artworks_qs.count(),
    })


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


# ── Tienda de Huesos de Milo ──────────────────────────────────────────────────

@login_required
def tienda(request):
    """Milo's shop - buy items with bones."""
    items = TiendaItem.objects.filter(is_active=True).order_by('order', 'costo_huesos')
    inventario_ids = set()
    if request.user.role == 'estudiante':
        inventario_ids = set(
            InventarioEstudiante.objects.filter(user=request.user)
            .values_list('item_id', flat=True)
        )
    logros_nuevos = []
    if request.user.role == 'estudiante':
        logros_nuevos = LogroUsuario.objects.filter(
            user=request.user, visto=False).select_related('logro')
    return render(request, 'games/tienda.html', {
        'items': items,
        'inventario_ids': inventario_ids,
        'huesos': request.user.huesos,
        'logros_nuevos': logros_nuevos,
    })


@login_required
@require_POST
def comprar_item(request):
    """Purchase a shop item with bones."""
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        item = get_object_or_404(TiendaItem, pk=item_id, is_active=True)

        if request.user.role != 'estudiante':
            return JsonResponse({'status': 'error', 'message': 'Solo los estudiantes pueden comprar.'}, status=403)

        # Check already owned
        if InventarioEstudiante.objects.filter(user=request.user, item=item).exists():
            return JsonResponse({'status': 'error', 'message': '¡Ya tienes este objeto!'}, status=400)

        # Check bones
        if request.user.huesos < item.costo_huesos:
            return JsonResponse({
                'status': 'error',
                'message': f'No tienes suficientes huesos. Necesitas {item.costo_huesos} 🦴'
            }, status=400)

        # Deduct bones
        request.user.huesos -= item.costo_huesos
        request.user.save(update_fields=['huesos'])

        HuesoTransaccion.objects.create(
            user=request.user, tipo='gastado',
            cantidad=item.costo_huesos,
            descripcion=f'Compra: {item.nombre}'
        )

        # Add to inventory
        InventarioEstudiante.objects.create(user=request.user, item=item)

        return JsonResponse({
            'status': 'ok',
            'message': f'¡{item.icono} {item.nombre} añadido a tu habitación!',
            'huesos_restantes': request.user.huesos,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# ── Habitación de Milo ────────────────────────────────────────────────────────

@require_POST
@login_required
def guardar_posicion_item(request):
    """Guarda pos_x (left%), pos_y (top%) y escala de un item en el inventario del estudiante."""
    try:
        data   = json.loads(request.body)
        inv_id = int(data['inv_id'])
        pos_x  = float(data['pos_x'])
        pos_y  = float(data['pos_y'])
        escala = float(data['escala'])
    except (KeyError, ValueError, TypeError):
        return JsonResponse({'status': 'error', 'msg': 'Datos inválidos'}, status=400)

    inv = get_object_or_404(InventarioEstudiante, pk=inv_id, user=request.user)
    inv.pos_x  = max(0.0, min(100.0, pos_x))
    inv.pos_y  = max(0.0, min(100.0, pos_y))
    inv.escala = max(0.3, min(3.0, escala))
    inv.save(update_fields=['pos_x', 'pos_y', 'escala'])
    return JsonResponse({'status': 'ok'})


@login_required
def habitacion_milo(request):
    """Student's Milo room with purchased items."""
    if request.user.role != 'estudiante':
        return redirect('accounts:dashboard_profesor')

    inventario = InventarioEstudiante.objects.filter(
        user=request.user
    ).select_related('item')

    logros_nuevos = LogroUsuario.objects.filter(
        user=request.user, visto=False).select_related('logro')

    return render(request, 'games/habitacion_milo.html', {
        'inventario': inventario,
        'huesos': request.user.huesos,
        'logros_nuevos': logros_nuevos,
    })