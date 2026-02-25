from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils.crypto import get_random_string
from django.apps import apps


# Create your models here.

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Post.Status.PUBLISHED)
    

class Post(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=120, verbose_name='Заголовок')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='Слаг')
    content = models.TextField(blank=True, verbose_name='Контент статьи')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    time_update = models.DateTimeField(auto_now=True,verbose_name='Время изменения')
    is_published = models.IntegerField(
    choices=Status.choices,
    default=Status.DRAFT,
    verbose_name='Статус поста')
    cat = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='posts', verbose_name='Категория')
    tags = models.ManyToManyField('TagPost', blank=True, related_name='tags',verbose_name='Тэг')
    is_pinned = models.BooleanField(default=False, verbose_name="Закреплено")
    objects = models.Manager()
    published = PublishedManager()
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/', default=None, blank=True, null=True, verbose_name='Фото')
    file = models.FileField(upload_to='files/%Y/%m/%d/', blank=True, null=True, verbose_name='Файл')

    author = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name='posts', null=True, default=None)


    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ['-is_pinned','-time_create']
        indexes = [
            models.Index(fields=['-time_create'])
        ]


    def get_absolute_url(self):
        return reverse('post', kwargs={'post_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            # Добавляем случайную строку, чтобы slug был уникальным
            self.slug = f"{base_slug}-{get_random_string(5)}"
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=100, db_index = True, verbose_name='Категория')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class TagPost(models.Model):
    tag = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.tag
    
    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})


class UploadFiles(models.Model):
    file = models.FileField(upload_to='uploads_model')

class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    content = models.TextField()
    time_create = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # 🔥 ВЛОЖЕННЫЕ ОТВЕТЫ
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_comments',
        blank=True
    )

    class Meta:
        ordering = ['-time_create']

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return f'{self.author} → {self.post}'
    
class Notification(models.Model):
    TYPE_CHOICES = (
        ('reply', 'Reply'),
        ('like', 'Like'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_notifications"
    )
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='reply')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.user} ({self.type})"
