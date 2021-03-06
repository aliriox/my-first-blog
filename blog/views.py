from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.contrib.auth.models import User
from django.contrib.auth import logout
import time
from smtplib import SMTPRecipientsRefused

# Create your views here.

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

scopes = ['https://www.googleapis.com/auth/calendar']

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'my-first-blog/blog/calendar.json',
    # entorno local 
    #'blog/calendar.json',
    scopes)

def calendar(request):
    service_calendar = build('calendar', 'v3', credentials=credentials)
    listevents = service_calendar.events().list(calendarId = 'primary').execute()
    context = listevents['items']
    return render(request, 'blog/calendar.html',context)

def post_list(request):
    post = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    posts = post.filter(author=request.user)
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_list_all(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list_all.html', {'posts': posts})

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
    context = {'request': request, 'user': request.user}
    # print User.objects.get(username = request.user)
    if request.user.is_anonymous():
        return render(request, 'blog/home.html',context)
    else:
        idn = User.objects.get(username = request.user)
        subject = "correo automatico de Django Web Blog"
        message = "Has iniciado sesion satisfactoriamente en Django Web Blog a las  "
        hora = time.strftime("%I:%M:%S")
        fecha = time.strftime("%d/%m/%y")
        message += str(hora) + "  " + str(fecha)
        try:
            idn.email_user(subject,message)
        except SMTPRecipientsRefused:
            print "conexion fail"
        return redirect('post_list')
