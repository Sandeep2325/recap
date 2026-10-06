from django.urls import path
from . import views

urlpatterns = [
    path('members/', views.members, name='members'),
    path('members/add/', views.add_member, name='add_member'),
    path('members/update/<int:id>/', views.update_member, name='update_member'),
    path('members/delete/<int:id>/', views.delete_member, name='delete_member'),
]
