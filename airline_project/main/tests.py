from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Flight, Booking, Invoice, Complaint

User = get_user_model()

class SystemTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.customer = User.objects.create_user(username='cust', password='1234', role='customer')
        self.service = User.objects.create_user(username='service', password='1234', role='service')
        self.manager = User.objects.create_user(username='manager', password='1234', role='manager')

        self.flight = Flight.objects.create(
            flight_number='FL123',
            origin='London',
            destination='Paris',
            departure_date='2025-05-01',
            departure_time='10:00',
            seats_available=100,
            price=100.00
        )

        self.booking = Booking.objects.create(customer=self.customer, flight=self.flight)
        self.invoice = Invoice.objects.create(booking=self.booking, total_amount=100.00, status='Pending')
        self.complaint = Complaint.objects.create(booking=self.booking, user=self.customer, message="Issue", status="Open")

    # ✅ Customer-related tests
    def test_customer_can_login(self):
        response = self.client.post(reverse('login'), {'username': 'cust', 'password': '1234'})
        self.assertEqual(response.status_code, 302)  # Redirects if login successful

    def test_customer_can_view_flights(self):
        self.client.login(username='cust', password='1234')
        response = self.client.get(reverse('flight_list'))
        self.assertContains(response, 'FL123')

    def test_customer_can_book_flight(self):
        self.client.login(username='cust', password='1234')
        response = self.client.get(reverse('book_flight', args=[self.flight.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after booking
        self.assertEqual(Booking.objects.count(), 2)

    def test_customer_can_view_booking_and_invoice(self):
        self.client.login(username='cust', password='1234')
        booking_response = self.client.get(reverse('booking_list'))
        invoice_response = self.client.get(reverse('invoice_list'))
        self.assertEqual(booking_response.status_code, 200)
        self.assertEqual(invoice_response.status_code, 200)

    # ✅ Complaint tests
    def test_complaint_submission(self):
        self.client.login(username='cust', password='1234')
        response = self.client.post(reverse('submit_complaint'), {
            'booking': self.booking.id,
            'message': 'Another issue'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Complaint.objects.count(), 2)

    def test_complaint_view_and_update_by_service(self):
        self.client.login(username='service', password='1234')
        response = self.client.get(reverse('view_complaints'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Issue')

        # Update complaint
        post_response = self.client.post(reverse('view_complaints'), {
            'complaint_id': self.complaint.id,
            'status': 'Resolved',
            'response': 'Handled it'
        })
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, 'Resolved')
        self.assertEqual(self.complaint.response, 'Handled it')

    # ✅ Booking Manager tests
    def test_booking_view_by_manager(self):
        self.client.login(username='manager', password='1234')
        response = self.client.get(reverse('booking_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FL123')

    def test_booking_cancel_by_manager(self):
        self.client.login(username='manager', password='1234')
        self.client.post(reverse('booking_dashboard'), {
            'action': 'update_booking',
            'booking_id': self.booking.id,
            'status': 'Cancelled'
        })
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'Cancelled')

    def test_invoice_status_update_and_delete(self):
        self.client.login(username='manager', password='1234')
        # Update invoice
        self.client.post(reverse('booking_dashboard'), {
            'action': 'update_invoice',
            'invoice_id': self.invoice.id,
            'status': 'Paid'
        })
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, 'Paid')

        # Delete invoice
        self.client.post(reverse('booking_dashboard'), {
            'action': 'delete_invoice',
            'invoice_id': self.invoice.id,
        })
        self.assertFalse(Invoice.objects.filter(id=self.invoice.id).exists())

    def test_booking_delete_by_manager(self):
        self.client.login(username='manager', password='1234')
        self.client.post(reverse('booking_dashboard'), {
            'action': 'delete_booking',
            'booking_id': self.booking.id,
        })
        self.assertFalse(Booking.objects.filter(id=self.booking.id).exists())
