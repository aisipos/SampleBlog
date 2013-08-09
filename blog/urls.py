from django.conf.urls import patterns, url
from blog import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'new_user.html', views.new_user, name='new_user'),
    url(r'login', views.login_view, name='login_view'),
    url(r'logout', views.logout_view, name='logout_view'),
    url(r'new_post', views.new_post, name='new_post'),
    url(r'user/(\w+)', views.view_user, name='view_user'),
    url(r'post/(\d+)', views.view_post, name='view_post'),
    url(r'tag/(\w+)', views.view_tag, name='view_tag'),
    url(r'category/(\w+)', views.view_category, name='view_category'),
    url(r'post_comment/(\d+)', views.post_comment, name='post_comment')
)
