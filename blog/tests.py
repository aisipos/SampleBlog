"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".


"""

from django.test import TestCase
from django.test.client import Client
from model_mommy import mommy
from blog.models import User, Tag, Post, Comment, Category
from django.core.urlresolvers import reverse

class BlogTest(TestCase):
    """
    Test suite for Blog application
    """

    def setUp(self):
        self.user = User.objects.create_user(username='foo', password='bar')

    def test_logout_link(self):
        """
        Test that the logout link appears only when logged in
        """
        self.assertTrue(self.client.login(username='foo', password='bar'))
        #Test sign out appears after login
        response = self.client.get('/')
        self.assertContains(response, 'Sign Out')
        #Test sign out missing after logout
        self.client.logout()
        response = self.client.get('/')
        self.assertNotContains(response, 'Sign Out')

    def test_tags_on_post_creation(self):
        """
        Ensure tags on a post link to existing tags, and new ones get created
        """
        #Make some existing tags
        known_tags = [mommy.make(Tag, tag=x) for x in ('foo', 'bar', 'baz')]
        self.assertEqual(Tag.objects.count(), 3)

        #Create a post with some old and new tags
        self.assertTrue(self.client.login(username='foo', password='bar'))
        tags = ['foo', 'bar', 'baz', 'wibble', 'wobble']
        response = self.client.post(
            reverse('blog.views.new_post'),
            dict(
                title='Example Title',
                body='Lorem Ipsum',
                tags= ' '.join(tags),
                category='Test'
            ),
            follow=True
        )
        self.assertNotContains(response, 'Invalid')

        #Check that the new tags have been created
        all_tags = [x.tag for x in Tag.objects.all()]
        self.assertEqual(len(all_tags), 5)
        for t in tags:
            self.assertIn(t, all_tags)

        #Check that post has been created
        post = Post.objects.get(title='Example Title')
        saved_tags = list(post.tags.all())
        self.assertEqual(len(saved_tags), 5)
        self.assertEqual(set(x.tag for x in saved_tags) , set(tags))

    def test_comment_in_post_view(self):
        """
        Test that comment appears in post view
        """
        comment = mommy.make(Comment, body='Test Comment', user__username='TestUser')
        response = self.client.get(reverse('blog.views.view_post', args=[comment.post.id]))
        self.assertContains(response, 'Test Comment')
        self.assertContains(response, 'TestUser')

    def test_posting_a_comment(self):
        """
        Test that comment gets posted
        """
        self.assertTrue(self.client.login(username='foo', password='bar'))

        #Create a comment
        post = mommy.make(Post, user = self.user)

        #Post it to the comment's Post
        response = self.client.post(
            reverse('blog.views.post_comment', args=[post.id]),
            {'body': 'Test Comment'},
            follow=True
        )
        self.assertContains(response, 'Test Comment')
        self.assertContains(response, 'Comment Posted!')

    def test_category_page(self):
        """
        Test view category page
        """
        #Make a post and category
        post = mommy.make(
            Post,
            title='Test Post',
            category__name='TestCategory',
            user__username='TestUser'
        )
        response = self.client.get(
            reverse('blog.views.view_category', args=['TestCategory'])
        )
        self.assertContains(response, 'TestCategory')
        self.assertContains(response, 'Test Post')
        self.assertContains(response, 'TestUser')
