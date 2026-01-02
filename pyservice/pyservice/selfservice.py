"""
Self-Service Portal View
PyService Mini-ITSM Platform
FAQ and quick ticket creation for staff
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from knowledge.models import Article, Category


@login_required
def selfservice_portal(request):
    """Self-service portal with FAQ and quick actions."""
    
    # Get featured/popular articles
    featured_articles = Article.objects.filter(
        is_published=True,
        is_featured=True
    )[:6]
    
    # Get popular articles (most viewed)
    popular_articles = Article.objects.filter(
        is_published=True
    ).order_by('-view_count')[:6]
    
    # Get categories
    categories = Category.objects.all()
    
    # Quick links for common requests
    quick_links = [
        {
            'title': 'Request New Laptop',
            'icon': 'bi-laptop',
            'url': '/requests/create/?type=hardware&item=laptop',
            'color': 'primary',
        },
        {
            'title': 'Software Installation',
            'icon': 'bi-box',
            'url': '/requests/create/?type=software',
            'color': 'success',
        },
        {
            'title': 'Report an Issue',
            'icon': 'bi-exclamation-triangle',
            'url': '/incidents/create/',
            'color': 'danger',
        },
        {
            'title': 'Knowledge Base',
            'icon': 'bi-book',
            'url': '/knowledge/',
            'color': 'info',
        },
    ]
    
    # Search in portal
    query = request.GET.get('q', '')
    search_results = []
    if query:
        search_results = Article.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query),
            is_published=True
        )[:10]
    
    context = {
        'featured_articles': featured_articles,
        'popular_articles': popular_articles,
        'categories': categories,
        'quick_links': quick_links,
        'query': query,
        'search_results': search_results,
    }
    
    return render(request, 'selfservice/portal.html', context)
