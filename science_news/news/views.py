from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import RegisterForm, CommentForm, ArticleForm
from .models import Category, Article, Comment, ApprovedCategory

def home_view(request):
    categories = Category.objects.all()
    latest_news = Article.objects.order_by('-created_at')[:5]
    return render(request, 'news/home.html', {
        'categories': categories,
        'latest_news': latest_news
    })

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('science_news:home')
    else:
        form = RegisterForm()
    return render(request, 'news/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('science_news:home')
    else:
        form = AuthenticationForm()
    return render(request, 'news/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('science_news:home')

def category_list_view(request):
    categories = Category.objects.all()
    return render(request, 'news/category_list.html', {'categories': categories})

def article_list_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    articles = Article.objects.filter(category=category)
    return render(request, 'news/article_list.html', {
        'category': category,
        'articles': articles
    })

def article_detail_view(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    comments = article.comments.all()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('science_news:login')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.article = article
            comment.save()
            return redirect('science_news:article_detail', article_id=article_id)
    else:
        form = CommentForm()

    return render(request, 'news/article_detail.html', {
        'article': article,
        'comments': comments,
        'form': form,
    })

@login_required
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return HttpResponseForbidden("Ви не можете видалити цей коментар.")
    article_id = comment.article.id
    comment.delete()
    return redirect('science_news:article_detail', article_id=article_id)

@login_required
def create_article_view(request):
    approved_categories = Category.objects.filter(
        id__in=ApprovedCategory.objects.filter(user=request.user).values_list('category_id', flat=True)
    )

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.cleaned_data['category']
            if category not in approved_categories:
                return HttpResponseForbidden("Ви не маєте дозволу на створення статей у цій категорії.")
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('science_news:article_detail', article_id=article.id)
    else:
        form = ArticleForm()
        form.fields['category'].queryset = approved_categories

    return render(request, 'news/article_form.html', {'form': form})

@login_required
def update_article_view(request, article_id):
    article = get_object_or_404(Article, id=article_id, author=request.user)

    approved_categories = Category.objects.filter(
        id__in=ApprovedCategory.objects.filter(user=request.user).values_list('category_id', flat=True)
    )

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            category = form.cleaned_data['category']
            if category not in approved_categories:
                return HttpResponseForbidden("Ви не маєте дозволу на редагування у цій категорії.")
            form.save()
            return redirect('science_news:article_detail', article_id=article.id)
    else:
        form = ArticleForm(instance=article)
        form.fields['category'].queryset = approved_categories

    return render(request, 'news/article_form.html', {'form': form})

@login_required
def delete_article_view(request, article_id):
    article = get_object_or_404(Article, id=article_id, author=request.user)
    category_id = article.category.id
    article.delete()
    return redirect('science_news:article_list', category_id=category_id)
