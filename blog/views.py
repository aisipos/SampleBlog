# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelForm, Form
from django.forms import widgets
from django import forms
from django.core.urlresolvers import reverse
from blog.models import Post, User, Tag, Comment, Category
from datetime import datetime


class UserForm(ModelForm):
    """
    Form for User entry
    """
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
    password = forms.CharField(widget=widgets.PasswordInput)


class PostForm(Form):
    """
    Form for Post entry
    """
    title = forms.CharField()
    category = forms.CharField()
    body = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField(label="Tags separated by spaces")


class CommentForm(Form):
    """
    Form for comment only
    """
    body = forms.CharField(label="Add a comment:")


def login_view(request):
    """
    Attempt to log a user in
    """
    if request.method != 'POST':
        return HttpResponseRedirect('/')

    #Send POST data as data kwarg.
    #See http://www.factory-h.com/blog/?p=196 for the reasons why
    form = AuthenticationForm(data=request.POST)
    if form.is_valid():
        login(request, form.get_user())
    else:
        messages.info(request, 'Invalid login information')
    return HttpResponseRedirect('/')


def logout_view(request):
    logout(request)
    messages.info(request, 'You are now logged out')
    return HttpResponseRedirect('/')


def index(request):
    """
    Home Page
    """
    latest_posts = Post.objects.order_by('-date')[:5]
    login_form = AuthenticationForm()
    context = {
        'latest_posts': latest_posts,
        'login_form' : login_form
    }
    return render(request, 'index.html', context)


def new_user(request):
    """
    Create new user page
    """
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(**form.cleaned_data)
            if new_user:
                #We must call authenticate() in order for login to succeed
                user = authenticate(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password']
                )
                #Login new users
                user = login(request, user)
                messages.info(request, 'Welcome {}'.format(new_user.username))
            else:
                messages.error(request, 'Unable to create user')
            return HttpResponseRedirect('/')
        else:
            return HttpResponseForbidden('Invalid User')
    else:
        form = UserForm()  # An unbound form

    return render(request, 'new_user.html', {
        'form': form,
    })


def new_post(request):
    """
    Create a new Post
    """
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            #Separate the tags we have seen before from those we haven't
            tags = form.cleaned_data['tags'].split(' ')
            known_tags = list(Tag.objects.filter(tag__in=tags))
            unknown_tag_names = set(tags) - set(x.tag for x in known_tags)
            #Create the unknown tags
            unknown_tags = [Tag(tag=x) for x in unknown_tag_names]
            #Tag.objects.bulk_create(unknown_tags)  # Sadly, this doesn't work.
            [t.save() for t in unknown_tags]

            #If category doesn't exist, create it
            try:
                category = Category.objects.get(name=form.cleaned_data['category'])
            except Category.DoesNotExist:
                category = Category(name=form.cleaned_data['category'], description='')
                category.save()

            #Create the Post object
            post = Post(
                user = request.user,
                category = category,
                title = form.cleaned_data['title'],
                body = form.cleaned_data['body'],
                date = datetime.now()
            )
            post.save()
            #You must create a primary key (by saving an object),
            #before you can use a many to many relationship
            post.tags.add(*(known_tags + unknown_tags))
            post.save()
            return HttpResponseRedirect('/')
        else:
            messages.error(request, 'Invalid post')
            return HttpResponseRedirect(reverse('new_post'))
    else:
        form = PostForm()

    return render(request, 'new_post.html', {
        'form': form,
    })


def view_user(request, username):
    """
    View a user
    """
    user = get_object_or_404(User, username=username)
    return render(request, 'view_user.html', {
        'user': user
    })


def view_post(request, post_id):
    """
    View a post, and make comments
    """
    post = get_object_or_404(Post, id=post_id)
    comment_form = CommentForm()
    return render(request, 'view_post.html', {
        'post': post,
        'comment_form' : comment_form
    })


def view_tag(request, tag_name):
    """
    View posts for a given tag
    """
    tag = get_object_or_404(Tag, tag=tag_name)
    return render(request, 'view_tag.html', {
        'tag': tag
    })


def view_category(request, category_name):
    """
    View posts for a given category
    """
    category = get_object_or_404(Category, name=category_name)
    return render(request, 'view_category.html', {
        'category': category
    })


def post_comment(request, post_id):
    """
    View posts for a given tag
    """
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = Comment(
                body = comment_form.cleaned_data['body'],
                date = datetime.now(),
                post = post,
                user = request.user
            )
            comment.save()
            messages.info(request, 'Comment Posted!')
        else:
            messages.error(request, 'Invalid comment')
    return HttpResponseRedirect(reverse('view_post', args=[post_id]))

