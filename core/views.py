from django.http import Http404, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render , redirect 
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView
from django.core.paginator import Paginator
from .models import Notification
from .utils import DataMixin
from .forms import AddPostForm, UploadFileForm, CommentForm
from .models import Post, Category, TagPost, UploadFiles, Comment
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
User = get_user_model()

class CoreHome(DataMixin, ListView):
    model = Post
    template_name = 'core/core.html'
    context_object_name = 'posts'
    title_page = 'Главная страница'

    def get_queryset(self):
        query = self.request.GET.get('q')
        queryset = Post.published.all().select_related('cat').order_by('-is_pinned','-time_create')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(author__username__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаем query для инпута
        context['search_query'] = self.request.GET.get('q', '')
        # Явно передаем 0, чтобы сработал {% if cat_selected == 0 %}
        return self.get_mixin_context(context, cat_selected=0)


def index(request):
    return render(request, 'index/index.html', {'title': 'VΛULT'})

@login_required
def about(request):
    contact_list = Post.published.all().order_by('-time_create')
    paginator = Paginator(contact_list, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/about.html', {'title': 'About', 'page_obj': page_obj})


class ShowPost(DataMixin, DetailView):
    model = Post
    template_name = 'core/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        slug = self.kwargs[self.slug_url_kwarg]
        post = get_object_or_404(Post, slug=slug)

        if not post.is_published and post.author != self.request.user:
            raise Http404()

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = context['post']

        context['comments'] = post.comments.filter(
            is_active=True,
            parent__isnull=True
        ).prefetch_related('replies__author').order_by('-time_create')

        context['form'] = CommentForm()

        return self.get_mixin_context(context, title=post.title)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = CommentForm(request.POST)

        if form.is_valid() and request.user.is_authenticated:
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user

            # 🔥 получаем parent_id
            parent_id = request.POST.get("parent_id")

            if parent_id:
                parent_comment = Comment.objects.filter(
                    id=parent_id,
                    post=self.object
                ).first()

                if parent_comment:
                    comment.parent = parent_comment

            comment.save()
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            from django.template.loader import render_to_string

            channel_layer = get_channel_layer()
            html = render_to_string(
                'core/includes/comment.html',
                {'comment': comment, 'user': request.user, 'post': self.object},
                request=request
            )

            async_to_sync(channel_layer.group_send)(
                f'post_{self.object.slug}',
                {
                    'type': 'new_comment',
                    'html': html
                }
)

            if comment.parent and comment.parent.author != request.user:
                Notification.objects.create(
                    user=comment.parent.author,
                    sender=request.user,
                    comment=comment,
                    type='reply'
                )
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                html = render_to_string(
                    'core/includes/comment.html',
                    {
                        'comment': comment,
                        'user': request.user,
                        'post': self.object
                    },
                    request=request
                )

                return JsonResponse({
                    'html': html,
                    'parent_id': parent_id,
                })

            return redirect(request.path)

        return JsonResponse({'error': 'Ошибка'}, status=400)


class PostCategory(DataMixin, ListView):
    template_name = 'core/core.html'
    context_object_name = 'posts'
    allow_empty = True
    allow_empty = True

    def get_queryset(self):
        # Добавляем явную сортировку в конец
        return Post.published.filter(cat__slug=self.kwargs['cat_slug']).select_related('cat').order_by('-is_pinned','-time_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = context['posts']
        if posts:
            cat = posts[0].cat
            context = self.get_mixin_context(
                context,
                title='Категория - ' + cat.name,
                cat_selected=cat.pk
            )
        else:
            # Если постов нет, просто указываем пустую категорию или выводим заголовок
            cat_slug = self.kwargs['cat_slug']
            cat_obj = Category.objects.filter(slug=cat_slug).first()
            cat_name = cat_obj.name if cat_obj else 'Неизвестная категория'
            cat_pk = cat_obj.pk if cat_obj else 0
            context = self.get_mixin_context(
                context,
                title='Категория - ' + cat_name,
                cat_selected=cat_pk
            )
        return context


class AddPost(PermissionRequiredMixin, LoginRequiredMixin,DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'core/addpost.html'
    title_page = 'Добавление поста'
    permission_required = 'core.add_post'


    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class UpdatePost(PermissionRequiredMixin,UpdateView):
    model = Post
    fields = ['title', 'content', 'photo', 'is_published', 'cat']
    template_name = 'core/addpost.html'
    success_url = reverse_lazy('core')
    title_page = 'Редактирование поста'
    permission_required = 'core.change_post'

    slug_field = 'slug'           # поле в модели
    slug_url_kwarg = 'post_slug'  

def contact(request):
    return HttpResponse('Обратная связь')

def page_not_found(request, exception):
    return render(request, '404.html', status=404)


class TagPostList(DataMixin, ListView):
    template_name = 'core/core.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_context_data(self,*, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = TagPost.objects.get(slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title='Тег: '+ tag.tag)
    
    def get_queryset(self):
            # Добавляем фильтр, связь и обязательную сортировку
            return Post.published.filter(tags__slug=self.kwargs['tag_slug']).select_related('cat').order_by('-is_pinned','-time_create')
        

class UserPostList(DataMixin, ListView):
    model = Post
    template_name = 'core/core.html'
    context_object_name = 'posts'
    allow_empty = True
    
    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        # Добавляем сортировку здесь
        return Post.published.filter(author=self.author).select_related('cat').order_by('-is_pinned','-time_create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(
            context,
            title=f'Посты автора: {self.author.username}'
        )
    

@require_POST
@login_required
def like_comment(request):
    comment_id = request.POST.get('comment_id')
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
        # Создаём уведомление владельцу комментария, если это не сам автор
        if comment.author != request.user:
            Notification.objects.create(
                user=comment.author,
                sender=request.user,
                comment=comment,
                type='like'
            )
    


    return JsonResponse({
        'liked': liked,
        'total_likes': comment.total_likes(),
        'users': [u.username for u in comment.likes.all()]  # сразу передаем список пользователей
    })


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Разрешаем удалять: автор комментария, владелец поста или суперюзер
    if request.user == comment.author or request.user == comment.post.author or request.user.is_superuser:
        comment.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'comment_id': comment_id})

    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def refresh_comments(request, post_slug):
    post = get_object_or_404(Post, slug=post_slug)
    comments = post.comments.filter(is_active=True, parent__isnull=True).order_by('-is_pinned','-time_create')

    html = ""
    for comment in comments:
        html += render_to_string(
            'core/includes/comment.html',
            {'comment': comment, 'user': request.user, 'post': post},
            request=request
        )

    return HttpResponse(html)
@login_required
def notifications_list(request):
    # Берем только непрочитанные
    notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')
    unread_count = notifications.count()


    return render(request, 'core/profile_notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
        'title': 'Уведомления',
    })

@login_required
def go_to_notification(request, notification_id):
    notification = get_object_or_404(request.user.notifications, id=notification_id)

    if not notification.is_read:
        notification.is_read = True
        notification.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    return redirect(notification.comment.post.get_absolute_url())


@login_required
def notifications_poll(request):
    # Только непрочитанные уведомления
    notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')

    data = [
        {
            'id': n.id,
            'type': n.type,
            'sender': n.sender.username,
            'created_at': n.created_at.strftime("%H:%M:%S"),
            'url': n.comment.post.get_absolute_url() if hasattr(n, 'comment') else '#'
        }
        for n in notifications
    ]

    return JsonResponse({
        'notifications': data,
        'unread_count': notifications.count()
    })


def permission_denied(request, exception):
    return render(request, '403.html', status=403)

def server_error(request):
    return render(request, '500.html', status=500)

@staff_member_required
def toggle_pin_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.is_pinned = not post.is_pinned
    post.save()
    
    # Если это AJAX-запрос, возвращаем JSON, а не редирект
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'is_pinned': post.is_pinned})
    
    # Для обычных кликов оставляем редирект
    return redirect(request.META.get('HTTP_REFERER', 'core'))