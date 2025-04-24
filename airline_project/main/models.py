from django.db import models
from django.contrib.auth.models import AbstractUser

# Extend default User model with role-based access
class User(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('service', 'Customer Service'),
        ('manager', 'Booking Manager'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

# Stores additional profile details for a user
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    passport_number = models.CharField(max_length=20)

# Flight details
class Flight(models.Model):
    flight_number = models.CharField(max_length=10)
    origin = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    departure_date = models.DateField()
    departure_time = models.TimeField()
    seats_available = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

# Booking record for a flight made by a customer
class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'customer'})
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    booking_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Confirmed')
    
    def __str__(self):
        return f"Booking ID: {self.id}"

# Invoice generated for a booking
class Invoice(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')

# Payment made toward an invoice
class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='Paid')

# Complaint submitted by a user regarding a booking
class Complaint(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint for Booking ID {self.booking.id} - Status: {self.status}"
