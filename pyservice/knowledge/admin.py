from django.contrib import admin
from .models import Category, Article


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'article_count', 'created_at']
    list_editable = ['order']
    search_fields = ['name', 'description']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'is_featured', 'view_count', 'updated_at']
    list_filter = ['is_published', 'is_featured', 'category']
    list_editable = ['is_published', 'is_featured']
    search_fields = ['title', 'content', 'summary']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['-updated_at']
