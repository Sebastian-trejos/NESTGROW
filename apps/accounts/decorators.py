from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def profesor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role != 'profesor':
            messages.error(request, '⛔ Esta sección es solo para profesores.')
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def estudiante_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role != 'estudiante':
            messages.error(request, '⛔ Esta sección es solo para estudiantes.')
            return redirect('accounts:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
