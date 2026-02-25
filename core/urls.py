from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('core/', views.CoreHome.as_view(), name='core'),
    path('core/about/', views.about, name='about'),
    path('core/addpost/', views.AddPost.as_view(), name='add_post'),
    path('contact/', views.contact, name='contact'),
    path('post/<slug:post_slug>/', views.ShowPost.as_view(), name='post'),
    path('core/category/<slug:cat_slug>/', views.PostCategory.as_view(), name='category'),
    path('tag/<slug:tag_slug>/', views.TagPostList.as_view(), name='tag'),
    path('edit/<slug:post_slug>/', views.UpdatePost.as_view(), name='editpage'),
    path('user/<str:username>/', views.UserPostList.as_view(), name='user_posts'),
    path('like-comment/', views.like_comment, name='like_comment'),
    path('delete-comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('core/notifications/', views.notifications_list, name='notifications'),
    path('core/notifications/go/<int:notification_id>/', views.go_to_notification, name='go_to_notification'),
    path('core/notifications/poll/', views.notifications_poll, name='notifications_poll'),
    path('post/<int:post_id>/pin/', views.toggle_pin_post, name='toggle_pin'),
]

