from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

from .forms import (RegistroForm, LoginForm,
                    ProfesorUserForm, ProfesorProfileForm,
                    EstudianteUserForm, EstudianteProfileForm,
                    GestionarEstudianteForm,
                    SalonForm, UnirseClaseForm)
from .models import CustomUser, ProfesorProfile, EstudianteProfile, Salon
from .decorators import profesor_required, estudiante_required
from apps.games.models import UserProgress, Score, pct_to_nota


# ── Auth ──────────────────────────────────────────────────────────────────────

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Si es estudiante, asignar el grado seleccionado al perfil recién creado
            if user.role == 'estudiante':
                grado = form.cleaned_data.get('grado', '')
                if grado:
                    EstudianteProfile.objects.filter(user=user).update(grado=grado)
            login(request, user)
            messages.success(request, f'¡Bienvenido/a a NestGrow, {user.first_name}! 🎉')
            return redirect('accounts:dashboard')
    else:
        form = RegistroForm()
    return render(request, 'accounts/registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Hola de nuevo, {user.first_name or user.username}! 👋')
            return redirect('accounts:dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, '¡Hasta pronto! Vuelve pronto a jugar. 👋')
    return redirect('core:home')


@login_required
def dashboard_view(request):
    if request.user.role == 'profesor':
        return redirect('accounts:dashboard_profesor')
    return redirect('accounts:dashboard_estudiante')


# ── Profesor Dashboard ────────────────────────────────────────────────────────

@login_required
@profesor_required
def dashboard_profesor(request):
    profile = request.user.profesor_profile
    salones = profile.salones.filter(is_active=True).prefetch_related('estudiantes__user')
    context = {
        'profile': profile,
        'salones': salones,
        'total_salones': salones.count(),
        'total_estudiantes': profile.get_total_estudiantes(),
    }
    return render(request, 'accounts/dashboard_profesor.html', context)


# ── Profesor — Editar Perfil ──────────────────────────────────────────────────

@login_required
@profesor_required
def editar_perfil_profesor(request):
    user_form = ProfesorUserForm(instance=request.user)
    profile_form = ProfesorProfileForm(instance=request.user.profesor_profile)

    if request.method == 'POST':
        user_form = ProfesorUserForm(request.POST, instance=request.user)
        profile_form = ProfesorProfileForm(request.POST, request.FILES, instance=request.user.profesor_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, '✅ Perfil actualizado correctamente.')
            return redirect('accounts:dashboard_profesor')

    return render(request, 'accounts/editar_perfil_profesor.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


# ── Profesor — Salones ────────────────────────────────────────────────────────

@login_required
@profesor_required
def crear_salon(request):
    if request.method == 'POST':
        form = SalonForm(request.POST)
        if form.is_valid():
            salon = form.save(commit=False)
            salon.profesor = request.user.profesor_profile
            salon.save()
            messages.success(request, f'✅ Salón "{salon.nombre}" creado. Código: {salon.codigo_clase}')
            return redirect('accounts:dashboard_profesor')
    else:
        form = SalonForm()
    return render(request, 'accounts/salon_form.html', {
        'form': form, 'titulo': 'Crear Nuevo Salón', 'accion': 'Crear salón'
    })


@login_required
@profesor_required
def editar_salon(request, pk):
    salon = get_object_or_404(Salon, pk=pk, profesor=request.user.profesor_profile)
    if request.method == 'POST':
        form = SalonForm(request.POST, instance=salon)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Salón "{salon.nombre}" actualizado.')
            return redirect('accounts:dashboard_profesor')
    else:
        form = SalonForm(instance=salon)
    return render(request, 'accounts/salon_form.html', {
        'form': form, 'titulo': f'Editar: {salon.nombre}', 'accion': 'Guardar cambios', 'salon': salon
    })


@login_required
@profesor_required
def eliminar_salon(request, pk):
    salon = get_object_or_404(Salon, pk=pk, profesor=request.user.profesor_profile)
    if request.method == 'POST':
        nombre = salon.nombre
        salon.delete()
        messages.success(request, f'🗑️ Salón "{nombre}" eliminado.')
        return redirect('accounts:dashboard_profesor')
    return render(request, 'accounts/confirmar_eliminar.html', {
        'objeto': salon, 'tipo': 'salón'
    })


@login_required
@profesor_required
def detalle_salon(request, pk):
    salon = get_object_or_404(Salon, pk=pk, profesor=request.user.profesor_profile)

    if request.method == 'POST':
        # Guardar cambios en bulk para todos los estudiantes del salón
        estudiantes_qs = salon.estudiantes.select_related('user').all()
        grados_validos = [v for v, _ in EstudianteProfile.GRADO_CHOICES]
        actualizados = 0
        for est in estudiantes_qs:
            pk_str = str(est.pk)
            grado = request.POST.get(f'grado_{pk_str}', '').strip()
            correo = request.POST.get(f'correo_padre_{pk_str}', '').strip()
            numero = request.POST.get(f'numero_lista_{pk_str}', '').strip()
            # Validación básica de grado
            if grado and grado not in grados_validos:
                grado = est.grado
            EstudianteProfile.objects.filter(pk=est.pk).update(
                grado=grado,
                correo_padre=correo,
                numero_lista=numero,
            )
            actualizados += 1
        messages.success(request, f'✅ Cambios guardados para {actualizados} estudiante(s).')
        return redirect('accounts:detalle_salon', pk=pk)

    # Ordenar por numero_lista numérico (vacíos al final)
    estudiantes_qs = salon.estudiantes.select_related('user').all()
    estudiantes = sorted(
        estudiantes_qs,
        key=lambda e: (int(e.numero_lista) if e.numero_lista and str(e.numero_lista).strip().isdigit() else 9999)
    )
    return render(request, 'accounts/detalle_salon.html', {
        'salon': salon,
        'estudiantes': estudiantes,
        'grado_choices': EstudianteProfile.GRADO_CHOICES,
    })


@login_required
@profesor_required
@require_POST
def actualizar_estudiante(request, pk):
    """El profesor edita grado, correo_padre y numero_lista de un estudiante."""
    estudiante = get_object_or_404(EstudianteProfile, pk=pk)
    # Verificar propiedad: el estudiante debe estar en un salon del profesor
    if not estudiante.salon or estudiante.salon.profesor != request.user.profesor_profile:
        messages.error(request, '⛔ No tienes permiso para editar este estudiante.')
        return redirect('accounts:dashboard_profesor')
    form = GestionarEstudianteForm(request.POST, instance=estudiante)
    if form.is_valid():
        form.save()
        messages.success(request, f'✅ Datos de {estudiante.user.get_full_name() or estudiante.user.username} actualizados.')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{error}')
    salon_pk = estudiante.salon.pk
    return redirect('accounts:detalle_salon', pk=salon_pk)


@login_required
@profesor_required
@require_POST
def subir_grado_salon(request, pk):
    """Sube el grado de todos los estudiantes del salón en un nivel."""
    salon = get_object_or_404(Salon, pk=pk, profesor=request.user.profesor_profile)
    grado_orden = ['1', '2', '3', '4', '5']
    idx_actual = grado_orden.index(salon.grado) if salon.grado in grado_orden else -1
    if idx_actual == -1 or idx_actual >= len(grado_orden) - 1:
        messages.warning(request, '⚠️ El salón ya está en el grado máximo (5° Primaria).')
        return redirect('accounts:detalle_salon', pk=pk)
    nuevo_grado = grado_orden[idx_actual + 1]
    salon.grado = nuevo_grado
    salon.save(update_fields=['grado'])
    # Actualizar el grado de todos los estudiantes del salón
    actualizados = salon.estudiantes.update(grado=nuevo_grado)
    grado_display = dict(EstudianteProfile.GRADO_CHOICES).get(nuevo_grado, nuevo_grado)
    messages.success(request, f'✅ Grado subido a {grado_display} para {actualizados} estudiante(s).')
    return redirect('accounts:detalle_salon', pk=pk)


# ── Profesor — Editar número de lista del estudiante ─────────────────────────

@login_required
@profesor_required
@require_POST
def set_numero_lista(request, pk):
    """El profesor asigna el número de lista de un estudiante."""
    estudiante = get_object_or_404(EstudianteProfile, pk=pk)
    if not estudiante.salon or estudiante.salon.profesor != request.user.profesor_profile:
        messages.error(request, '⛔ No tienes permiso para editar este estudiante.')
        return redirect('accounts:dashboard_profesor')
    numero = request.POST.get('numero_lista', '').strip()
    EstudianteProfile.objects.filter(pk=pk).update(numero_lista=numero)
    return redirect(request.POST.get('next', 'accounts:dashboard_profesor'))


# ── Profesor — Enviar informe PDF por correo ──────────────────────────────────

@login_required
@profesor_required
def enviar_informe(request, estudiante_pk):
    from .utils import generar_pdf_informe
    estudiante = get_object_or_404(EstudianteProfile, pk=estudiante_pk)

    # Security check: student must belong to this professor
    if not estudiante.salon or estudiante.salon.profesor != request.user.profesor_profile:
        messages.error(request, '⛔ No tienes permiso para enviar este informe.')
        return redirect('accounts:dashboard_profesor')

    if not estudiante.correo_padre:
        messages.error(request, f'❌ El estudiante {estudiante.user.get_full_name()} no tiene correo del padre registrado.')
        return redirect('accounts:detalle_salon', pk=estudiante.salon.pk)

    # Get student game progress (minijuegos)
    progreso = UserProgress.objects.filter(user=estudiante.user).select_related('game')

    # Get taller sessions with nota calculation (exclude párrafo libre)
    from apps.talleres.models import SesionTaller, BloquePregunta, RespuestaEstudiante
    sesiones_taller = (
        SesionTaller.objects
        .filter(estudiante=estudiante.user)
        .select_related('taller')
        .order_by('-created_at')
    )
    talleres_data = []
    for sesion in sesiones_taller:
        preguntas_cal = BloquePregunta.objects.filter(
            bloque__taller=sesion.taller,
            tipo_respuesta__in=['opcion_multiple', 'casillas'],
        )
        total_cal = preguntas_cal.count()
        nota_info = None
        if total_cal > 0:
            correctas = RespuestaEstudiante.objects.filter(
                estudiante=estudiante.user,
                pregunta__in=preguntas_cal,
                es_correcta=True,
            ).count()
            pct = (correctas / total_cal) * 100
            nota_info = {
                'nota': pct_to_nota(pct),
                'correctas': correctas,
                'total': total_cal,
                'pct': round(pct, 1),
            }
        talleres_data.append({'sesion': sesion, 'nota_info': nota_info})

    # Generate PDF
    pdf_bytes = generar_pdf_informe(estudiante, progreso, talleres_data)

    # Send email
    try:
        subject = f'Informe de actividades - {estudiante.user.get_full_name()} - NestGrow'
        body = render_to_string('accounts/email_informe.html', {
            'estudiante': estudiante,
            'profesor': request.user,
        })
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[estudiante.correo_padre],
        )
        email.content_subtype = 'html'
        email.attach(
            f'informe_{estudiante.user.username}.pdf',
            pdf_bytes,
            'application/pdf'
        )
        email.send()
        messages.success(request, f'✅ Informe enviado a {estudiante.correo_padre}')
    except Exception as e:
        messages.error(request, f'❌ Error al enviar el correo: {str(e)}')

    return redirect('accounts:detalle_salon', pk=estudiante.salon.pk)


# ── Estudiante Dashboard ──────────────────────────────────────────────────────

@login_required
@estudiante_required
def dashboard_estudiante(request):
    from apps.games.models import LogroUsuario
    profile = request.user.estudiante_profile
    progreso = UserProgress.objects.filter(user=request.user).select_related('game')
    logros_recientes = LogroUsuario.objects.filter(
        user=request.user).select_related('logro').order_by('-created_at')[:4]
    logros_pendientes = LogroUsuario.objects.filter(user=request.user, visto=False).count()

    # Historia: find the next incomplete accessible lesson for the continue button
    historia_primera_incompleta = None
    try:
        from apps.historia.models import SeccionHistoria, SeccionDesbloqueada, ProgresoLeccion

        def _sec_desbloqueada(sec):
            if sec.is_desbloqueada_por_defecto:
                return True
            if not profile.salon:
                return False
            return SeccionDesbloqueada.objects.filter(seccion=sec, salon=profile.salon).exists()

        completadas_ids = set(
            ProgresoLeccion.objects.filter(estudiante=request.user, completada=True)
            .values_list('leccion_id', flat=True)
        )
        for sec in SeccionHistoria.objects.prefetch_related('lecciones').order_by('orden'):
            if not _sec_desbloqueada(sec):
                continue
            prev_ok = True
            for lec in sec.lecciones.order_by('orden'):
                if lec.pk not in completadas_ids and prev_ok:
                    historia_primera_incompleta = {
                        'leccion_pk': lec.pk,
                        'seccion_titulo': sec.titulo,
                        'seccion_emoji': sec.icono_emoji,
                    }
                    break
                prev_ok = lec.pk in completadas_ids
            if historia_primera_incompleta:
                break
    except Exception:
        pass

    # Info del profesor para el mini panel
    profesor_profile = None
    if profile.salon:
        try:
            profesor_profile = profile.salon.profesor
        except Exception:
            pass

    context = {
        'profile': profile,
        'progreso': progreso,
        'juegos_completados': progreso.filter(completed=True).count(),
        'logros_recientes': logros_recientes,
        'logros_pendientes': logros_pendientes,
        'puntos_requeridos': profile.puntos_requeridos(),
        'historia_primera_incompleta': historia_primera_incompleta,
        'profesor_profile': profesor_profile,
    }
    return render(request, 'accounts/dashboard_estudiante.html', context)


@login_required
@estudiante_required
def guardar_avatar(request):
    """Guarda el avatar Emoji Kitchen del estudiante."""
    import json
    from django.http import JsonResponse
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    try:
        data = json.loads(request.body)
        profile = request.user.estudiante_profile
        profile.avatar_emoji1 = data.get('emoji1', '🐶')[:10]
        profile.avatar_emoji2 = data.get('emoji2', '🐱')[:10]
        profile.avatar_color = data.get('color', '#6C63FF')[:10]
        profile.avatar_kitchen_url = data.get('kitchen_url', '')[:500]
        profile.save(update_fields=['avatar_emoji1', 'avatar_emoji2', 'avatar_color', 'avatar_kitchen_url'])
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@login_required
@estudiante_required
def editar_perfil_estudiante(request):
    user_form = EstudianteUserForm(instance=request.user)
    profile_form = EstudianteProfileForm(instance=request.user.estudiante_profile)

    if request.method == 'POST':
        user_form = EstudianteUserForm(request.POST, instance=request.user)
        profile_form = EstudianteProfileForm(request.POST, instance=request.user.estudiante_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, '✅ Perfil actualizado correctamente.')
            return redirect('accounts:dashboard_estudiante')

    return render(request, 'accounts/editar_perfil_estudiante.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': request.user.estudiante_profile,
    })


@login_required
@estudiante_required
def unirse_clase(request):
    if request.method == 'POST':
        form = UnirseClaseForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo_clase'].upper()
            try:
                salon = Salon.objects.get(codigo_clase=codigo, is_active=True)
                estudiante = request.user.estudiante_profile
                # Verificar que el grado del estudiante coincide con el del salón
                if estudiante.grado and salon.grado and estudiante.grado != salon.grado:
                    grado_salon = salon.get_grado_display()
                    grado_est = dict(EstudianteProfile.GRADO_CHOICES).get(estudiante.grado, estudiante.grado)
                    messages.error(
                        request,
                        f'❌ Este salón es de {grado_salon}, pero tú estás registrado en {grado_est}. '
                        f'Pídele a tu profesor que verifique el código o ajuste tu grado.'
                    )
                else:
                    estudiante.salon = salon
                    estudiante.profesor = salon.profesor
                    estudiante.grado = salon.grado
                    estudiante.save()
                    messages.success(request, f'✅ ¡Te uniste al salón {salon.nombre} del profesor {salon.profesor.user.get_full_name()}!')
                    return redirect('accounts:dashboard_estudiante')
            except Salon.DoesNotExist:
                messages.error(request, '❌ Código inválido. Verifica con tu profesor.')
    else:
        form = UnirseClaseForm()
    return render(request, 'accounts/unirse_clase.html', {'form': form})


# ── Legacy redirect ───────────────────────────────────────────────────────────

@login_required
def editar_perfil(request):
    if request.user.role == 'profesor':
        return redirect('accounts:editar_perfil_profesor')
    return redirect('accounts:editar_perfil_estudiante')
