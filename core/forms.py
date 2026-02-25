from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
from .models import Category, Post, Comment

class AddPostForm(forms.ModelForm):
    cat = forms.ModelChoiceField(queryset=Category.objects.all(),empty_label='Не выбрано', label='Категория')

    class Meta:
        model = Post
        fields = ['title', 'content','photo','file','is_published', 'cat',]
        widgets = {
            'content': forms.Textarea(attrs={'cols': 50, 'rows': 5}),
        }
        labels = {'slug': 'URL-slug'}



class UploadFileForm(forms.Form):
    file = forms.ImageField(label="Файл")



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Напишите комментарий...'
            }),'class': 'comment-class'
        }