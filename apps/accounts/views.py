from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from .forms import RegistroForm, LoginForm, ProfesorProfileForm, EstudianteProfileForm, UnirseClaseForm
from .models import CustomUser, ProfesorProfile, EstudianteProfile
from .decorators import profesor_required, estudiante_required
from apps.games.models import UserProgress


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


@login_required
@profesor_required
def dashboard_profesor(request):
    profile = request.user.profesor_profile
    estudiantes = profile.estudiantes.select_related('user').all()
    context = {
        'profile': profile,
        'estudiantes': estudiantes,
        'total_estudiantes': estudiantes.count(),
    }
    return render(request, 'accounts/dashboard_profesor.html', context)


@login_required
@estudiante_required
def dashboard_estudiante(request):
    profile = request.user.estudiante_profile
    progreso = UserProgress.objects.filter(user=request.user).select_related('game')
    context = {
        'profile': profile,
        'progreso': progreso,
        'juegos_completados': progreso.filter(completed=True).count(),
    }
    return render(request, 'accounts/dashboard_estudiante.html', context)


@login_required
@estudiante_required
def unirse_clase(request):
    if request.method == 'POST':
        form = UnirseClaseForm(request.POST)
        if form.is_valid():
            codigo = form.cleaned_data['codigo_clase'].upper()
            try:
                prof_profile = ProfesorProfile.objects.get(codigo_clase=codigo)
                estudiante = request.user.estudiante_profile
                estudiante.profesor = prof_profile
                estudiante.save()
                messages.success(request, f'✅ ¡Te uniste a la clase del profesor {prof_profile.user.get_full_name()}!')
                return redirect('accounts:dashboard_estudiante')
            except ProfesorProfile.DoesNotExist:
                messages.error(request, '❌ Código inválido. Verifica con tu profesor.')
    else:
        form = UnirseClaseForm()
    return render(request, 'accounts/unirse_clase.html', {'form': form})


@login_required
def editar_perfil(request):
    if request.user.role == 'profesor':
        profile = request.user.profesor_profile
        FormClass = ProfesorProfileForm
    else:
        profile = request.user.estudiante_profile
        FormClass = EstudianteProfileForm

    if request.method == 'POST':
        form = FormClass(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Perfil actualizado correctamente.')
            return redirect('accounts:dashboard')
    else:
        form = FormClass(instance=profile)
    return render(request, 'accounts/editar_perfil.html', {'form': form})
