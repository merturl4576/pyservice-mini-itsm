"""
Knowledge Base URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.article_list, name='kb_article_list'),
    path('categories/', views.category_list, name='kb_category_list'),
    path('article/<slug:slug>/', views.article_detail, name='kb_article_detail'),
    path('helpful/<int:article_id>/', views.mark_helpful, name='kb_mark_helpful'),
]
