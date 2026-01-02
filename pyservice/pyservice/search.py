"""
Global Search View
PyService Mini-ITSM Platform
Search across all modules
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from incidents.models import Incident
from service_requests.models import ServiceRequest
from cmdb.models import Asset
from knowledge.models import Article


@login_required
def global_search(request):
    """Search across all modules."""
    query = request.GET.get('q', '').strip()
    
    results = {
        'incidents': [],
        'requests': [],
        'assets': [],
        'articles': [],
    }
    
    if query and len(query) >= 2:
        # Search incidents
        results['incidents'] = Incident.objects.filter(
            Q(number__icontains=query) |
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )[:10]
        
        # Search service requests
        results['requests'] = ServiceRequest.objects.filter(
            Q(number__icontains=query) |
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )[:10]
        
        # Search assets
        results['assets'] = Asset.objects.filter(
            Q(name__icontains=query) |
            Q(serial_number__icontains=query) |
            Q(model_name__icontains=query)
        )[:10]
        
        # Search knowledge base
        results['articles'] = Article.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query),
            is_published=True
        )[:10]
    
    total_results = (
        len(results['incidents']) +
        len(results['requests']) +
        len(results['assets']) +
        len(results['articles'])
    )
    
    return render(request, 'search_results.html', {
        'query': query,
        'results': results,
        'total_results': total_results,
    })
