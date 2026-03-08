from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, VocabularyItem


@login_required
def category_list(request):
    categories = Category.active.all()
    return render(request, 'content/category_list.html', {'categories': categories})


@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk, is_active=True)
    vocabulary = category.vocabulary.filter(is_active=True)
    return render(request, 'content/vocabulary_detail.html', {
        'category': category,
        'vocabulary': vocabulary,
    })
