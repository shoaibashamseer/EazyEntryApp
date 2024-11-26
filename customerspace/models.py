from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
import random


class Event(models.Model):

    name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class EventDay(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="days")
    day_number = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        unique_together = ("event", "day_number")

    def __str__(self):
        return f"Day {self.day_number} of {self.event.name} ({self.start_time} - {self.end_time})"

class SeatType(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="seat_types")
    type_name = models.CharField(max_length=50) 
    capacity = models.PositiveIntegerField()  

    def __str__(self):
        return f"{self.type_name} for {self.event.name} (Capacity: {self.capacity})"

class SeatAllocation(models.Model):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="seats")
    qr_code_data = models.CharField(max_length=8, unique=True, editable=False)  
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"QR {self.qr_code_data} for Event {self.event.name}"



class DailyAttendance(models.Model):
    
    event_day = models.ForeignKey(EventDay, on_delete=models.CASCADE, related_name="attendance")
    seat_allocation = models.ForeignKey(SeatAllocation, on_delete=models.CASCADE)
    is_inside = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("event_day", "seat_allocation")

    def __str__(self):
        return f"{self.seat_allocation} attended on {self.event_day}"
