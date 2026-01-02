"""
Knowledge Base Views
PyService Mini-ITSM Platform
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Category, Article


@login_required
def article_list(request):
    """List all published articles."""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    
    articles = Article.objects.filter(is_published=True)
    
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query)
        )
    
    if category_id:
        articles = articles.filter(category_id=category_id)
    
    categories = Category.objects.all()
    featured = Article.objects.filter(is_published=True, is_featured=True)[:3]
    
    return render(request, 'knowledge/article_list.html', {
        'articles': articles,
        'categories': categories,
        'featured': featured,
        'query': query,
        'selected_category': category_id,
    })


@login_required
def article_detail(request, slug):
    """View single article."""
    article = get_object_or_404(Article, slug=slug, is_published=True)
    article.increment_view()
    
    related = Article.objects.filter(
        category=article.category,
        is_published=True
    ).exclude(id=article.id)[:5]
    
    return render(request, 'knowledge/article_detail.html', {
        'article': article,
        'related': related,
    })


@login_required
def category_list(request):
    """List all categories."""
    categories = Category.objects.all()
    return render(request, 'knowledge/category_list.html', {
        'categories': categories,
    })


@login_required
def mark_helpful(request, article_id):
    """Mark article as helpful (AJAX)."""
    if request.method == 'POST':
        article = get_object_or_404(Article, id=article_id)
        article.mark_helpful()
        return JsonResponse({'success': True, 'count': article.helpful_count})
    return JsonResponse({'success': False})
