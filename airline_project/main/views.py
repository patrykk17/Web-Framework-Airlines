from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Flight, Booking, Invoice
from datetime import date
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Profile
from django.contrib.auth import get_user_model
from django import forms
from .models import Complaint

User = get_user_model()

# Home page view
def home(request):
    return render(request, 'home.html')

# View to list all flights
@login_required
def flight_list(request):
    flights = Flight.objects.all()
    return render(request, 'flight_list.html', {'flights': flights})

# Book a flight and create corresponding invoice
@login_required
def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    booking = Booking.objects.create(customer=request.user, flight=flight)
    Invoice.objects.create(booking=booking, total_amount=flight.price, status='Pending')
    return redirect('booking_list')

# List of bookings for the logged-in user
@login_required
def booking_list(request):
    bookings = Booking.objects.filter(customer=request.user)
    return render(request, 'booking_list.html', {'bookings': bookings})

# List of invoices for the logged-in user
@login_required
def invoice_list(request):
    invoices = Invoice.objects.filter(booking__customer=request.user)
    return render(request, 'invoice_list.html', {'invoices': invoices})

# Custom user registration form including profile fields
class CustomUserForm(UserCreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField()
    address = forms.CharField(widget=forms.Textarea)
    passport_number = forms.CharField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'address', 'passport_number', 'password1', 'password2']

# User registration view
def register(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            # Save extended profile data
            Profile.objects.create(
                user=user,
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                passport_number=form.cleaned_data['passport_number']
            )

            login(request, user)
            return redirect('home')
    else:
        form = CustomUserForm()
    return render(request, 'register.html', {'form': form})

# Complaint form using Django ModelForm
class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['booking', 'message']

# Submit a complaint (customers only)
@login_required
def submit_complaint(request):
    if request.user.role != 'customer':
        return HttpResponseForbidden("Only customers can file complaints.")

    form = ComplaintForm(request.POST or None)
    form.fields['booking'].queryset = Booking.objects.filter(customer=request.user)

    if request.method == 'POST' and form.is_valid():
        complaint = form.save(commit=False)
        complaint.user = request.user
        complaint.save()
        return redirect('booking_list') 

    return render(request, 'submit_complaint.html', {'form': form})

# View all complaints (service role only)
@login_required
def view_complaints(request):
    if request.user.role != 'service':
        return redirect('home')

    complaints = Complaint.objects.all().order_by('-created_at')

    if request.method == 'POST':
        complaint_id = request.POST.get('complaint_id')
        complaint = Complaint.objects.get(id=complaint_id)
        complaint.status = request.POST.get('status')
        complaint.response = request.POST.get('response')
        complaint.save()
        return redirect('view_complaints')

    return render(request, 'complaints_dashboard.html', {'complaints': complaints})

# View user’s own complaints
@login_required
def my_complaints(request):
    complaints = Complaint.objects.filter(user=request.user)
    return render(request, 'my_complaints.html', {'complaints': complaints})

# Dashboard for booking managers to manage bookings and invoices
@login_required
def booking_manager_dashboard(request):
    if request.user.role != 'manager':
        return redirect('home')

    bookings = Booking.objects.all()
    invoices = Invoice.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_booking':
            booking = get_object_or_404(Booking, id=request.POST.get('booking_id'))
            booking.status = request.POST.get('status')
            booking.save()
        elif action == 'delete_booking':
            Booking.objects.filter(id=request.POST.get('booking_id')).delete()
        elif action == 'update_invoice':
            invoice = get_object_or_404(Invoice, id=request.POST.get('invoice_id'))
            invoice.status = request.POST.get('status')
            invoice.save()
        elif action == 'delete_invoice':
            Invoice.objects.filter(id=request.POST.get('invoice_id')).delete()

        return redirect('booking_dashboard')

    return render(request, 'booking_dashboard.html', {
        'bookings': bookings,
        'invoices': invoices
    })
