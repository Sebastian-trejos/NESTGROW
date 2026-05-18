from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib import messages
import json

from .models import Game, UserProgress, Score, Logro, LogroUsuario, HuesoTransaccion, clasificar_puntaje, Artwork, PaintingWord, PuzzleImage, TiendaItem, InventarioEstudiante
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
            'image': v.image.url if v.image else None,
            'audio': v.audio.url if v.audio else None,
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
        'quiz': 'games/quiz.html',
        'ordenar_letras': 'games/ordenar_letras.html',
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
        'quiz': 'games/quiz.html',
        'ordenar_letras': 'games/ordenar_letras.html',
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
        if request.user.role == 'estudiante':
            # Otorgar XP igual al puntaje obtenido en el juego
            perfil = request.user.estudiante_profile
            perfil.puntos_totales += score_val
            subio_nivel = perfil.actualizar_nivel()
            nuevo_nivel = perfil.nivel
            nuevos_logros = verificar_logros(request.user)

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
            messages.success(request, f'🎮 Juego "{juego.title}" creado correctamente.')
            return redirect('games:editar_juego', pk=juego.pk)
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
            messages.success(request, f'✅ Juego "{juego.title}" actualizado!')
            return redirect('games:gestionar_juegos')
    else:
        form = GameForm(instance=juego)
    puzzle_imagenes = (
        PuzzleImage.objects.filter(game=juego)
        if juego.game_type == 'puzzle' else []
    )
    return render(request, 'games/profesor/juego_form.html', {
        'form': form, 'titulo': f'Editar: {juego.title}', 'accion': 'Guardar',
        'juego': juego, 'painting_words': painting_words,
        'puzzle_imagenes': puzzle_imagenes,
        'juego_usa_imagenes': juego.game_type == 'puzzle'})


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
