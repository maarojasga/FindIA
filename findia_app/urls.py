from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.list_movements, name='list_movements'),
    path('crear/', views.create_movement, name='create_movement'),
    path('editar/<pk>/', views.edit_movement, name='edit_movement'),
    path('eliminar/<pk>/', views.delete_movement, name='delete_movement'),
    path('chat', views.chat, name="chat"),
    path('ask_question/', views.ask_question, name="ask_question"),
    path('calculate_credit/', views.calculate_credit, name='calculate_credit'),
]