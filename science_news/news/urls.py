from django.urls import path
from . import views

app_name = 'science_news'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/<int:category_id>/', views.article_list_view, name='article_list'),
    path('article/<int:article_id>/', views.article_detail_view, name='article_detail'),
    path('comment/<int:comment_id>/delete/', views.delete_comment_view, name='delete_comment'),
    path('article/create/', views.create_article_view, name='create_article'),
    path('article/<int:article_id>/edit/', views.update_article_view, name='edit_article'),
    path('article/<int:article_id>/delete/', views.delete_article_view, name='delete_article'),
]
