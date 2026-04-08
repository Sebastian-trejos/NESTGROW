from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

from .forms import (RegistroForm, LoginForm,
                    ProfesorUserForm, ProfesorProfileForm,
                    EstudianteUserForm, EstudianteProfileForm,
                    SalonForm, UnirseClaseForm)
from .models import CustomUser, ProfesorProfile, EstudianteProfile, Salon
from .decorators import profesor_required, estudiante_required
from apps.games.models import UserProgress, Score


# ── Auth ──────────────────────────────────────────────────────────────────────

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
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
        profile_form = ProfesorProfileForm(request.POST, instance=request.user.profesor_profile)
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
    estudiantes = salon.estudiantes.select_related('user').all()
    return render(request, 'accounts/detalle_salon.html', {
        'salon': salon,
        'estudiantes': estudiantes,
    })


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

    # Get student progress
    progreso = UserProgress.objects.filter(user=estudiante.user).select_related('game')
    scores = Score.objects.filter(user=estudiante.user).select_related('game').order_by('-created_at')[:5]

    # Generate PDF
    pdf_bytes = generar_pdf_informe(estudiante, progreso, scores)

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
    context = {
        'profile': profile,
        'progreso': progreso,
        'juegos_completados': progreso.filter(completed=True).count(),
        'logros_recientes': logros_recientes,
        'logros_pendientes': logros_pendientes,
        'puntos_requeridos': profile.puntos_requeridos(),
    }
    return render(request, 'accounts/dashboard_estudiante.html', context)


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
