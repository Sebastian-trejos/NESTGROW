from django.shortcuts import render, redirect
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def dispatch(self, request, *args, **kwargs):
        # Usuarios ya autenticados no deben ver la landing page
        if request.user.is_authenticated:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)


class AboutView(TemplateView):
    template_name = 'core/about.html'


def page_not_found(request, exception):
    return render(request, '404.html', status=404)
