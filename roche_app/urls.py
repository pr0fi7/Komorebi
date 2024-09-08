from django.urls import path
from . import views

urlpatterns = [
    path('challenges/', views.create_challenge, name='create_challenge'),
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('book_room/', views.book_room, name='book_room'),
    path('get_users_by_department/', views.get_users_by_department, name='get_users_by_department'),
    path('', views.home, name='home'),
    path('submit_idea/', views.submit_idea, name='submit_idea'),
    path('challenges_view/', views.challenges_view, name='challenges_view'),
    path('accept_challenge/<int:challenge_id>/', views.accept_challenge, name='accept_challenge'),
    path('leave_challenge/<int:challenge_id>/', views.leave_challenge, name='leave_challenge'),
    path('challenge_overview/<int:challenge_id>/', views.challenge_overview, name='challenge_overview'),
    path('dashboard', views.dashboard, name='dashboard'),
]
