from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.contrib.auth.models import User
from django.contrib.auth import logout
import time

# Create your views here.

def post_list(request):
    post = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    posts = post.filter(author=request.user)
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
	post = get_object_or_404(Post, pk=pk)
	return render(request, 'blog/post_detail.html', {'post': post})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

def home(request):
    print "entra en home"
    context = {'request': request, 'user': request.user}
    # print User.objects.get(username = request.user)
    if request.user.is_anonymous():
        print "True"
        return render(request, 'blog/home.html',context)
    else:
        print"False"
        idn = User.objects.get(username = request.user)
        subject = "correo automatico de Django Web Blog"
        message = "Has iniciado sesion satisfactoriamente en Django Web Blog a las  "
        hora = time.strftime("%I:%M:%S")
        fecha = time.strftime("%d/%m/%y")
        message += str(hora) + "  " + str(fecha)
        idn.email_user(subject,message)
        return redirect('post_list')
