from django.contrib import admin
from .models import User, Profile, Flight, Booking, Invoice, Payment

admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Flight)
admin.site.register(Booking)
admin.site.register(Invoice)
admin.site.register(Payment)
