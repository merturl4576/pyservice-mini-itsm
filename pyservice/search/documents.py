"""
Elasticsearch Search Documents
PyService Mini-ITSM Platform

Elasticsearch document mappings for full-text search.
"""

from django.conf import settings

# Only import elasticsearch if enabled
if getattr(settings, 'ELASTICSEARCH_ENABLED', False):
    from django_elasticsearch_dsl import Document, fields
    from django_elasticsearch_dsl.registries import registry
    from incidents.models import Incident
    from service_requests.models import ServiceRequest
    from knowledge.models import Article
    from cmdb.models import Asset, User
    
    
    @registry.register_document
    class IncidentDocument(Document):
        """Elasticsearch document for Incident model."""
        
        caller = fields.ObjectField(properties={
            'id': fields.IntegerField(),
            'username': fields.TextField(),
            'full_name': fields.TextField(),
        })
        
        assigned_to = fields.ObjectField(properties={
            'id': fields.IntegerField(),
            'username': fields.TextField(),
            'full_name': fields.TextField(),
        })
        
        class Index:
            name = 'pyservice_incidents'
            settings = {
                'number_of_shards': 1,
                'number_of_replicas': 0,
            }
        
        class Django:
            model = Incident
            fields = [
                'id',
                'number',
                'title',
                'description',
                'state',
                'priority',
                'resolution_notes',
                'created_at',
                'resolved_at',
            ]
            related_models = [User]
        
        def get_queryset(self):
            return super().get_queryset().select_related('caller', 'assigned_to')
        
        def get_instances_from_related(self, related_instance):
            if isinstance(related_instance, User):
                return Incident.objects.filter(
                    caller=related_instance
                ) | Incident.objects.filter(
                    assigned_to=related_instance
                )
    
    
    @registry.register_document
    class AssetDocument(Document):
        """Elasticsearch document for Asset model."""
        
        assigned_to = fields.ObjectField(properties={
            'id': fields.IntegerField(),
            'username': fields.TextField(),
        })
        
        class Index:
            name = 'pyservice_assets'
            settings = {
                'number_of_shards': 1,
                'number_of_replicas': 0,
            }
        
        class Django:
            model = Asset
            fields = [
                'id',
                'name',
                'asset_type',
                'serial_number',
                'model_name',
                'manufacturer',
                'status',
                'location',
                'notes',
            ]
    
    
    @registry.register_document
    class ArticleDocument(Document):
        """Elasticsearch document for Knowledge Base Article."""
        
        category = fields.ObjectField(properties={
            'id': fields.IntegerField(),
            'name': fields.TextField(),
        })
        
        class Index:
            name = 'pyservice_articles'
            settings = {
                'number_of_shards': 1,
                'number_of_replicas': 0,
            }
        
        class Django:
            model = Article
            fields = [
                'id',
                'title',
                'content',
                'is_published',
                'view_count',
            ]

else:
    # Placeholder classes when Elasticsearch is disabled
    class IncidentDocument:
        pass
    
    class AssetDocument:
        pass
    
    class ArticleDocument:
        pass
