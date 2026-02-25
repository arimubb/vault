import re
from django import template
from django.db.models import Count
from core.models import Category, TagPost
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe
register = template.Library()

@register.inclusion_tag('core/list_categories.html', takes_context=True)
def show_categories(context, cat_selected=0):
    request = context.get('request')
    show_all = request.GET.get('show_all') == '1' if request else False

    if show_all:
        cats = Category.objects.all()
    else:
        # Оставляем те, где есть посты + ту, которая выбрана (Q объекты для сложного фильтра)
        from django.db.models import Q, Count
        cats = Category.objects.annotate(posts_count=Count('posts')).filter(
            Q(posts_count__gt=0) | Q(pk=cat_selected)
        )

    return {'cats': cats, 'cat_selected': cat_selected}
@register.inclusion_tag('core/list_tags.html')
def show_all_tags():
    return {'tags': TagPost.objects.all()}

@register.filter(name='highlight_mention')
def highlight_mention(text):
    if not text:
        return ""

    def replace_with_link(match):
        mention = match.group(1)  # Это "@username"
        username = mention[1:]    # Отрезаем "@", получаем "username"
        
        try:
            # Генерируем ссылку на профиль (имя маршрута 'user_posts')
            url = reverse('user_posts', args=[username])
            return f'<a href="{url}" class="comment-mention">{mention}</a>'
        except NoReverseMatch:
            # Если такого пользователя или пути нет, просто оставляем текст синим
            return f'<span class="comment-mention">{mention}</span>'

    # Находит @username и вызывает функцию replace_with_link
    mentioned_text = re.sub(r'(@[a-zA-Z0-9_А-Яа-яёЁ-]+)', replace_with_link, str(text))
    
    return mark_safe(mentioned_text)