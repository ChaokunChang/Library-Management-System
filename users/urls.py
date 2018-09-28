from django.conf.urls import url
from django.urls import path
from django.contrib.auth.views import login
from . import views

app_name = 'users'

urlpatterns = [
    url(r'^login/$', login, {'template_name': 'users/login.html'}, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^register/$', views.register, name='register'),
    path('records/<int:user_id>', views.records, name='records')
]
