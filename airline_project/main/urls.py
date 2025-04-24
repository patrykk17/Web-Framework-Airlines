from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('flights/', views.flight_list, name='flight_list'),
    path('book/<int:flight_id>/', views.book_flight, name='book_flight'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('register/', views.register, name='register'),
    path('complaints/submit/', views.submit_complaint, name='submit_complaint'),
    path('complaints/manage/', views.view_complaints, name='view_complaints'),
    path('complaints/mine/', views.my_complaints, name='my_complaints'),
    path('dashboard/booking-manager/', views.booking_manager_dashboard, name='booking_dashboard'),







]
