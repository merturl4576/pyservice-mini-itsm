"""
Search API Views
PyService Mini-ITSM Platform

Full-text search endpoints using Elasticsearch or Django ORM fallback.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


class GlobalSearchView(APIView):
    """
    Global search across multiple models.
    Uses Elasticsearch if enabled, falls back to Django ORM.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        search_type = request.query_params.get('type', 'all')
        limit = int(request.query_params.get('limit', 10))
        
        if not query:
            return Response({
                'error': 'Query parameter "q" is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(query) < 2:
            return Response({
                'error': 'Query must be at least 2 characters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        results = {
            'query': query,
            'results': {}
        }
        
        if getattr(settings, 'ELASTICSEARCH_ENABLED', False):
            # Use Elasticsearch
            results['results'] = self._elasticsearch_search(query, search_type, limit)
            results['engine'] = 'elasticsearch'
        else:
            # Fall back to Django ORM
            results['results'] = self._orm_search(query, search_type, limit)
            results['engine'] = 'django_orm'
        
        return Response(results)
    
    def _elasticsearch_search(self, query, search_type, limit):
        """Search using Elasticsearch."""
        from .documents import IncidentDocument, AssetDocument, ArticleDocument
        
        results = {}
        
        if search_type in ['all', 'incidents']:
            incidents = IncidentDocument.search().query(
                'multi_match',
                query=query,
                fields=['number', 'title', 'description', 'resolution_notes']
            )[:limit]
            
            results['incidents'] = [
                {
                    'id': hit.id,
                    'number': hit.number,
                    'title': hit.title,
                    'state': hit.state,
                    'priority': hit.priority,
                    'score': hit.meta.score,
                }
                for hit in incidents
            ]
        
        if search_type in ['all', 'assets']:
            assets = AssetDocument.search().query(
                'multi_match',
                query=query,
                fields=['name', 'serial_number', 'model_name', 'manufacturer']
            )[:limit]
            
            results['assets'] = [
                {
                    'id': hit.id,
                    'name': hit.name,
                    'serial_number': hit.serial_number,
                    'status': hit.status,
                    'score': hit.meta.score,
                }
                for hit in assets
            ]
        
        if search_type in ['all', 'articles']:
            articles = ArticleDocument.search().query(
                'multi_match',
                query=query,
                fields=['title', 'content']
            ).filter('term', is_published=True)[:limit]
            
            results['articles'] = [
                {
                    'id': hit.id,
                    'title': hit.title,
                    'score': hit.meta.score,
                }
                for hit in articles
            ]
        
        return results
    
    def _orm_search(self, query, search_type, limit):
        """Search using Django ORM (fallback)."""
        from incidents.models import Incident
        from service_requests.models import ServiceRequest
        from cmdb.models import Asset
        from knowledge.models import Article
        
        results = {}
        
        if search_type in ['all', 'incidents']:
            incidents = Incident.objects.filter(
                Q(number__icontains=query) |
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )[:limit]
            
            results['incidents'] = [
                {
                    'id': inc.pk,
                    'number': inc.number,
                    'title': inc.title,
                    'state': inc.state,
                    'priority': inc.priority,
                }
                for inc in incidents
            ]
        
        if search_type in ['all', 'requests']:
            requests = ServiceRequest.objects.filter(
                Q(number__icontains=query) |
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )[:limit]
            
            results['requests'] = [
                {
                    'id': req.pk,
                    'number': req.number,
                    'title': req.title,
                    'state': req.state,
                }
                for req in requests
            ]
        
        if search_type in ['all', 'assets']:
            assets = Asset.objects.filter(
                Q(name__icontains=query) |
                Q(serial_number__icontains=query) |
                Q(model_name__icontains=query) |
                Q(manufacturer__icontains=query)
            )[:limit]
            
            results['assets'] = [
                {
                    'id': asset.pk,
                    'name': asset.name,
                    'serial_number': asset.serial_number,
                    'status': asset.status,
                }
                for asset in assets
            ]
        
        if search_type in ['all', 'articles']:
            articles = Article.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query),
                is_published=True
            )[:limit]
            
            results['articles'] = [
                {
                    'id': article.pk,
                    'title': article.title,
                }
                for article in articles
            ]
        
        return results


class SearchSuggestionsView(APIView):
    """
    Autocomplete search suggestions.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if len(query) < 2:
            return Response({'suggestions': []})
        
        suggestions = []
        
        # Get incident number suggestions
        from incidents.models import Incident
        incidents = Incident.objects.filter(
            Q(number__istartswith=query) |
            Q(title__icontains=query)
        ).values_list('number', 'title')[:5]
        
        for number, title in incidents:
            suggestions.append({
                'type': 'incident',
                'value': number,
                'label': f'{number}: {title[:40]}...' if len(title) > 40 else f'{number}: {title}'
            })
        
        # Get asset suggestions
        from cmdb.models import Asset
        assets = Asset.objects.filter(
            Q(name__icontains=query) |
            Q(serial_number__istartswith=query)
        ).values_list('name', 'serial_number')[:5]
        
        for name, serial in assets:
            suggestions.append({
                'type': 'asset',
                'value': serial or name,
                'label': f'{name} ({serial})' if serial else name
            })
        
        return Response({'suggestions': suggestions[:10]})
