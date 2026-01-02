"""
Knowledge Base App
PyService Mini-ITSM Platform
IT solutions and FAQ articles
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    """Knowledge Base Category."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='bi-folder')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    def article_count(self):
        return self.articles.filter(is_published=True).count()


class Article(models.Model):
    """Knowledge Base Article."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles'
    )
    content = models.TextField()
    summary = models.TextField(max_length=500, blank=True)
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='kb_articles'
    )
    
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-updated_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
    
    def __str__(self):
        return self.title
    
    def increment_view(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def mark_helpful(self):
        self.helpful_count += 1
        self.save(update_fields=['helpful_count'])
