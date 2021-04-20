from django.urls import path
from django.contrib.auth import views as auth_views
from . import views



urlpatterns = [
    # path('login/', views.user_login, name='login')
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.dashboard, name="dashboard"),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/,', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),
    path('create_tournaments/', views.create_tournaments, name='create_tournaments'),
    path('waiting_tournaments/', views.waiting_tournaments, name='waiting_tournaments'),
    path('ongoing_tournaments/', views.ongoing_tournaments, name='ongoing_tournaments'),
    path('completed_tournaments/', views.completed_tournaments, name='completed_tournaments'),
    path('<int:year>/<int:month>/<int:day>/<slug:tournament>/', views.tournament_detail, name='tournament_detail'),
    path('<int:year>/<int:month>/<int:day>/<slug:tournament>/start/', views.tournament_start, name='tournament_start'),
    path('<int:year>/<int:month>/<int:day>/<slug:tournament>/delete/', views.tournament_delete, name='tournament_delete'),
    path('<int:year>/<int:month>/<int:day>/<slug:tournament>/complete/', views.tournament_complete, name='tournament_complete'),
    path('<int:year>/<int:month>/<int:day>/<slug:tournament>/edit/', views.edit_tournaments, name='edit_tournaments'),
]
