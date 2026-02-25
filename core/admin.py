from django.contrib import admin, messages
from .models import Post, Category, Comment
from django.utils.safestring import mark_safe

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fields = ['title', 'slug', 'content', 'photo','post_photo', 'file','cat', 'is_published']
    prepopulated_fields = {"slug": ('title', )}
    list_display = ('title', 'time_create', 'post_photo', 'is_published', 'cat',)
    readonly_fields = ['post_photo']
    list_display_links = ('title',)
    ordering = ['time_create', 'title']
    list_editable = ('is_published',)
    list_per_page = 5
    actions = ['set_published', 'set_draft']
    search_fields = ['title__startswith', 'cat__name' ]
    list_filter = ['cat__name', 'is_published']
    save_on_top = True



    @admin.display(description='Изображение', ordering='content')
    def post_photo(self, post: Post):
        if post.photo:
            return mark_safe(f"<img src='{post.photo.url}' width=50>")
        return "Без фото"
    @admin.action(description='Опубликовать выбранные записи')
    def set_published(self, request, queryset):
        count = queryset.update(is_published=Post.Status.PUBLISHED)
        self.message_user(request, f'Изменено {count} записей')

    @admin.action(description='Снять с публикации выбранные записи')
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=Post.Status.DRAFT)
        self.message_user(request, f'{count} записей cнято с публикации.', messages.WARNING)



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'time_create', 'is_active')
    list_filter = ('is_active', 'time_create')