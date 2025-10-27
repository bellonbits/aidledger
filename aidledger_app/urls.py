from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    # User dashboard and actions
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('donate/', views.make_donation_view, name='make_donation'),
    path('distribute/', views.make_distribution_view, name='make_distribution'),
    
    # API endpoints
    path('api/donors/', views.DonorListCreateView.as_view(), name='donor-list'),
    path('api/ngos/', views.NGOListCreateView.as_view(), name='ngo-list'),
    path('api/recipients/', views.RecipientListCreateView.as_view(), name='recipient-list'),
    path('api/donations/', views.DonationListView.as_view(), name='donation-list'),
    path('api/distributions/', views.DistributionListView.as_view(), name='distribution-list'),
    path('api/donate/', views.create_donation, name='create-donation'),
    path('api/distribute/', views.create_distribution, name='create-distribution'),
    path('api/transactions/', views.get_transactions, name='get-transactions'),
    path('api/verify/<str:txn_hash>/', views.verify_transaction, name='verify-transaction'),
    path('api/stats/', views.get_stats, name='get-stats'),
    
    # Public dashboard
    path('', views.dashboard_view, name='home'),
]