from django.urls import path
from .views import *

urlpatterns = [
    path('', UserLogin.as_view(), name='login'),
    path('logout/', logout, name='logout'),
    path('authors/', Authors.as_view(), name='authors'),
    path('edit-author/<int:author_id>/', EditAuthor.as_view(), name='edit-author'),
    path('update_author_status/', update_author_status, name='update_author_status'),
    path('edit-book/<int:book_id>/', EditBooks.as_view(), name='edit-book'),
    path('update_book_status/', update_book_status, name='update_book_status'),

    path('books/', Books.as_view(), name='books'),
    path('view_books/<int:author_id>/', ViewBooks.as_view(), name='view_books'),
    
    path('list-all-author/', ListAllAuthor.as_view(), name='list-all-author'),
    path('list-all-author-status-on/', ListAllAuthorStatusOn.as_view(), name='list-all-author-status-on'),
    path('author/<int:pk>/', AuthorView.as_view(), name='author'),
    
    path('list-all-book/', ListAllBook.as_view(), name='list-all-book'),
    path('list-all-book-status-on/', ListAllBookStatusOn.as_view(), name='list-all-book-status-on'),
    path('book/<int:pk>/', BookView.as_view(), name='book'),


]
