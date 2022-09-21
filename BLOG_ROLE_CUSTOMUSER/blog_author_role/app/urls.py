from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('blog_list/',BlogList.as_view()),
    path('blog_type_update/',UpdateBlogStatus.as_view()),
    path('blog_bookmark/', BookmarkBlogs.as_view()),
    path('blog_ratings/',GiveRatings.as_view()),
    path('blog_view_bookmarks/',ViewBookMark.as_view()),
    path('user_view_blog/',UserViewBlogs.as_view()),
    path('admin_blog_view/',AdminBlogView.as_view()),
]
