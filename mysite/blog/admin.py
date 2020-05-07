from django.contrib import admin
from .models import Post

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # displayed column
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    # 1 filter field for
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
