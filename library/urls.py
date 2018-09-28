from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.index, name='index'),
    path('books', views.books, name='books'),
    path('bookinfo/<int:stock_id>/', views.book_info, name='bookinfo'),

    path('borrow_gd/<int:stock_id>', views.borrow_guidance, name="borrow_gd"),
    path('borrow/<int:stock_id>/', views.borrow_book, name='borrow'),

    path('renew_confirmation/<int:book_id>', views.renew_confirmation, name='renew_confirmation'),
    path('renew/<int:book_id>', views.renew_book, name='renew'),

    path('return/<int:book_id>', views.return_book, name='return'),

    path('reserve_confirmation/<int:stock_id>', views.reserve_confirmation, name='reserve_confirmation'),
    path('reserve/<int:book_id>', views.reserve_book, name='reserve'),
    path('reserve_hd/<int:book_id>/<int:sign>', views.reserve_handle, name='reserve_handle'),

    path('suggest', views.suggest_book, name='suggest'),

    path('new_review/<int:stock_id>', views.new_review, name='new_review'),
    path('edit_review/<int:review_id>', views.edit_review, name='edit_review'),

    path('errormsg/<str:msg>', views.error_msg, name="errormsg"),
    path('message/<str:msg>', views.message, name='message'),

    path('add_book', views.add_book, name='add_book'),
]
