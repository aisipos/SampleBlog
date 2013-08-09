from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    """
    One tag, represented as a single string
    """
    tag = models.CharField(max_length=50)


class Category(models.Model):
    """
    Categories for posts
    """
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300)


class Post(models.Model):
    """
    Represent a single blog post
    """
    title = models.CharField(max_length=300)
    body = models.TextField()
    date = models.DateTimeField()
    user = models.ForeignKey(User)
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag)


class Comment(models.Model):
    """
    Represent one comment on one blog post
    """
    body = models.CharField(max_length=256)
    date = models.DateTimeField()
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User)

