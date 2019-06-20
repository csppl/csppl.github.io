from django.urls import path
from . import views

# namespace 에러뜨면 이거 .. 안 한 거다! ㅋㅋ
app_name = 'boards'

urlpatterns = [
    path('', views.index),
    path('manage/', views.manage, name='manage'),
    path('service/', views.service, name='service'),
]