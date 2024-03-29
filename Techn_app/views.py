from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib import auth
from .models import *
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from rest_framework import generics, status, filters
from .serializers import *
from rest_framework.response import Response
from .dependencies import generate_book_code
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



# Create your views here.


class UserLogin(View):
    def get(self, request):
        return render(request, 'login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)    
        if user is not None and user.is_staff:
            print("user is ", user)
            login(request, user)
            return redirect('authors')
        else:
            messages.error(request,"Please enter valid credentials")
            return redirect('login')
        
        
        
def logout(request):
    auth.logout(request)
    return redirect('login')


class Authors(View):
    def get(self, request):
        if request.user.is_authenticated:
            search_query = request.GET.get('search', '')
            
            authors_list = Author.objects.filter(Q(name__icontains=search_query)).order_by('name')

            if not search_query:
                authors_list = Author.objects.all().order_by('name')

            paginator = Paginator(authors_list, 4)
            page = request.GET.get('page', 1)

            try:
                authors = paginator.page(page)
            except PageNotAnInteger:
                authors = paginator.page(1)
            except EmptyPage:
                authors = paginator.page(paginator.num_pages)
            
            authorss = Author.objects.all().order_by('name')
            author_count = len(authorss)
            books = Book.objects.all()
            book_count = len(books)

            return render(request, 'Authors.html', {'authors': authors, 'author_count': author_count, 'book_count': book_count, 'search_query': search_query})
        else:
            return redirect('login')

    def post(self, request):
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')

        if Author.objects.filter(name=name).exists():
            messages.error(request, 'Author with this name already exists.')
            return redirect('authors')

        if Author.objects.filter(username=username).exists():
            messages.error(request, 'Author with this username already exists.')
            return redirect('authors')

        if Author.objects.filter(email=email).exists():
            messages.error(request, 'Author with this email already exists.')
            return redirect('authors')

        author = Author.objects.create(name=name, username=username, email=email, is_active=True)
        author.save()

        messages.success(request, 'Author created successfully.')
        return redirect('authors')
    
def update_author_status(request):
    author_id = request.POST.get('author_id')
    is_active_str = request.POST.get('is_active')

    is_active = is_active_str.lower() == 'true'

    author = get_object_or_404(Author, pk=author_id)

    author.is_active = is_active
    author.save()

    return JsonResponse({'status': 'success', 'message': 'Author status updated successfully'})

class EditAuthor(View):
    def post(self, request, author_id):
        if request.user.is_authenticated:
            author = get_object_or_404(Author, pk=author_id)

            name = request.POST.get('name')
            username = request.POST.get('username')
            email = request.POST.get('email')
            is_active = request.POST.get('is_active') == 'True'

            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, 'Please enter a valid email address.')
                return redirect('authors')

            if Author.objects.filter(name=name).exclude(pk=author.id).exists():
                messages.error(request, 'Author with this name already exists.')
                return redirect('authors')

            if Author.objects.filter(username=username).exclude(pk=author.id).exists():
                messages.error(request, 'Author with this username already exists.')
                return redirect('authors')

            if Author.objects.filter(email=email).exclude(pk=author.id).exists():
                messages.error(request, 'Author with this email already exists.')
                return redirect('authors')

            author.name = name
            author.username = username
            author.email = email
            author.is_active = is_active
            author.save()

            messages.success(request, 'Author updated successfully.')
            return redirect('authors')
        else:
            return redirect('login')
    


class Books(View):
    def get(self, request):
        if request.user.is_authenticated:
            search_query = request.GET.get('search', '')
            books_list = Book.objects.filter(title__icontains=search_query).order_by('title')
            paginator = Paginator(books_list, 4)
            page = request.GET.get('page', 1)

            try:
                books = paginator.page(page)
            except PageNotAnInteger:
                books = paginator.page(1)
            except EmptyPage:
                books = paginator.page(paginator.num_pages)
                
            authors = Author.objects.all()
            author_count = len(authors)
            bookss = Book.objects.all().order_by('title')
            book_count = len(bookss)
            return render(request, 'Books.html', {'books': books, 'authors': authors, 'author_count': author_count, 'book_count': book_count})
        else:
            return redirect('login')

    def post(self, request):
        book_name = request.POST.get('book_name')
        author_id = request.POST.get('author')

        author = Author.objects.get(pk=author_id)
        
        if Book.objects.filter(title=book_name).exists():
            messages.error(request, 'Book with this name already exists.')
            return redirect('books')

        book = Book.objects.create(author=author, title=book_name,book_code=generate_book_code(self), is_active=True)
        book.save()

        return redirect('books')
    
class EditBooks(View):
    def post(self, request, book_id):
        if request.user.is_authenticated:
            book = get_object_or_404(Book, pk=book_id)
            
            book_title = request.POST.get('book_title')
            author_id = request.POST.get('author')
            
            author_id = int(author_id)
            
            author = Author.objects.get(pk=author_id)
            
            book.title = book_title
            book.author = author
            
            if Book.objects.filter(title=book_title).exclude(pk=book_id).exists():
                messages.error(request, 'Book with this name already exists.')
                return redirect('books')
            book.save()
            return redirect('books')
        else:
            return redirect('login')
    
def update_book_status(request):
    book_id = request.POST.get('book_id')
    is_active_str = request.POST.get('is_active')

    is_active = is_active_str.lower() == 'true'

    book = Book.objects.get(pk=book_id)
    book.is_active = is_active
    book.save()

    return JsonResponse({'status': 'success'}) 
    
class ViewBooks(View):

    def get(self, request, author_id):
        if request.user.is_authenticated:
            search_query = request.GET.get('search', '')
            author = get_object_or_404(Author, pk=author_id)

            if search_query:
                books = Book.objects.filter(author=author, title__icontains=search_query)
            else:
                books = Book.objects.filter(author=author)

            page = request.GET.get('page', 1)
            paginator = Paginator(books, 4)

            try:
                books = paginator.page(page)
            except PageNotAnInteger:
                books = paginator.page(1)
            except EmptyPage:
                books = paginator.page(paginator.num_pages)

            return render(request, 'AuthorBooks.html', {'author': author, 'books': books})
        
        else:
            return redirect('login')

    def post(self, request, author_id):
        author = get_object_or_404(Author, pk=author_id)

        book_name = request.POST.get('book_name')
        new_book = Book.objects.create(author=author, title=book_name,book_code =generate_book_code(self) , is_active=True)
        new_book.save()

        return redirect('view_books', author_id=author_id)
    
    
#REST API


class ListAllAuthor(generics.ListAPIView): #LISTING ALL AUTHORS INCLUDING STATUS OFF
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'username', 'email']  
    queryset = Author.objects.all()
        
    
class ListAllAuthorStatusOn(generics.ListAPIView): #LISTING ALL AUTHOR WITH STATUS ON IN PROPER API RESPONSE
    queryset = Author.objects.filter(is_active=True)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'username', 'email']  

    def get_queryset(self):
        return Author.objects.filter(is_active=True)

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = AuthorSerializer(queryset, many=True)
        return Response({
            'status': "success",
            'message': "Listed all authors with status on successfully",
            'response_code': status.HTTP_200_OK,
            'data': serializer.data
        })
        
        
class AuthorView(generics.ListAPIView): # LISTS SPECIFIC AUTHORS
    serializer_class = AuthorSerializer
        
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Author.objects.filter(pk=pk)
    
    
    
class ListAllBook(generics.ListAPIView):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']  
        
    
    
class ListAllBookStatusOn(generics.ListAPIView): #LISTING ALL BOOKS WITH STATUS ON IN PROPER API RESPONSE
    serializer_class = BookSerializer
    queryset = Book.objects.filter(is_active=True)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']  
    
    def get_queryset(self):
        return Book.objects.filter(is_active=True)

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = BookSerializer(queryset, many=True)
        return Response({
            'status': "success",
            'message': "Listed all Books with status on successfully",
            'response_code': status.HTTP_200_OK,
            'data': serializer.data
        })


class BookView(generics.ListAPIView): # LISTS SPECIFIC BOOK
    serializer_class = BookSerializer
    
    
    def get_queryset(self):
        pk = self.kwargs['pk']
        return Book.objects.filter(pk=pk)
    
