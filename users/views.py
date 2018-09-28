from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from library.models import *


# Create your views here.

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('library:index'))


def register(request):
    if request.method != "POST":
        form = UserCreationForm()
    else:
        form = UserCreationForm(data=request.POST)

        if form.is_valid():
            new_user = form.save()
            authenticate_user = authenticate(username=new_user.username, password=request.POST['password1'])
            login(request, authenticate_user)
            # 同步Reader表
            user = User.objects.get(username=new_user.username)
            LibraryReader.objects.create(user_id=user.id)
            return HttpResponseRedirect(reverse('library:index'))

    context = {'form': form}
    return render(request, 'users/register.html', context)


def records(request, user_id):
    all_records = LibraryLoan.objects.filter(user_id=user_id)
    returned = all_records.filter(flag__lte=0).values('id', 'book', 'loan_time', 'loan_date')  # 完成借阅
    borrowing = all_records.filter(flag=1).values('id', 'book', 'loan_time', 'loan_date')  # 正在借阅
    reserving = all_records.filter(flag=2).values('id', 'book', 'loan_time', 'loan_date')  # 正在预约
    broken = returned.filter(flag__lt=0).values('id', 'book', 'loan_time', 'loan_date')  # 违约借阅记录
    personal_info = User.objects.get(id=user_id)
    notifications = LibraryNotification.objects.filter(user_id=user_id).filter(flag__lt=2).order_by('flag')

    for record in returned:
        book_isbn = LibraryBook.objects.get(id=record['book']).isbn
        book_name = LibraryStock.objects.get(isbn=book_isbn).name
        record['name'] = book_name
        record['isbn'] = book_isbn
    for record in broken:
        book_isbn = LibraryBook.objects.get(id=record['book']).isbn
        book_name = LibraryStock.objects.get(isbn=book_isbn).name
        record['name'] = book_name
        record['isbn'] = book_isbn
    for record in borrowing:
        book_isbn = LibraryBook.objects.get(id=record['book']).isbn
        book_name = LibraryStock.objects.get(isbn=book_isbn).name
        record['name'] = book_name
        record['isbn'] = book_isbn
    for record in reserving:
        book_isbn = LibraryBook.objects.get(id=record['book']).isbn
        book_name = LibraryStock.objects.get(isbn=book_isbn).name
        record['name'] = book_name
        record['isbn'] = book_isbn

    context = {'returned': returned, 'broken': broken, 'borrowing': borrowing,
               'reserving': reserving, 'personal_info': personal_info, 'notifications': notifications}
    return render(request, 'users/user_records.html', context)

