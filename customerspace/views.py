from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils.timezone import now
from .models import Event, EventDay, SeatAllocation, DailyAttendance


def login_view(request):
    if request.method == "POST":
        name = request.POST.get("name")  # Fetch event name
        password = request.POST.get("password")  # Fetch event password

        # Check for valid event
        try:
            event = get_object_or_404(Event, name=name, password=password)
            request.session['event_id'] = event.id  # Store event ID in session
            return redirect('checkin')  # Redirect to checkin page
        except Event.DoesNotExist:
            messages.error(request, "Invalid credentials.")
            return redirect('login')  # Redirect back to login on failure

    return render(request, 'customerspace/login.html')


def checkin_view(request):
    event_id = request.session.get('event_id')
    if not event_id:
        return redirect('login')  # Redirect to login if no session exists

    # Get event and active day
    event = get_object_or_404(Event, id=event_id)
    current_time = now()
    event_day = event.days.filter(start_time__lte=current_time, end_time__gte=current_time).first()

    if not event_day:
        return render(request, 'customerspace/checkin.html', {"error": "No active event found.", "event": event})

    # Calculate seat counts
    attendance = DailyAttendance.objects.filter(event_day=event_day)
    seat_counts = {}
    for record in attendance:
        seat_type = record.seat_allocation.seat_type.type_name if record.seat_allocation.seat_type else "Unknown"
        seat_counts[seat_type] = seat_counts.get(seat_type, 0) + 1

    return render(request, 'customerspace/checkin.html', {"event": event, "seat_counts": seat_counts})


def scan_qr_code_view(request):
    if request.method == "POST":
        qr_code_data = request.POST.get("qr_code_data")
        event_id = request.session.get('event_id')

        # Ensure event is valid
        if not event_id:
            return JsonResponse({"error": "Invalid session. Please log in again."}, status=403)

        # Get active event day
        event_day = EventDay.objects.filter(event__id=event_id, start_time__lte=now(), end_time__gte=now()).first()
        if not event_day:
            return JsonResponse({"error": "No active event day at this time."}, status=400)

        # Find seat allocation by QR code
        try:
            seat = SeatAllocation.objects.get(event_id=event_id, qr_code_data=qr_code_data)
        except SeatAllocation.DoesNotExist:
            return JsonResponse({"error": "Invalid QR Code"}, status=400)

        # Handle attendance logic
        attendance, created = DailyAttendance.objects.get_or_create(event_day=event_day, seat_allocation=seat)
        if attendance.is_inside:
            # Already inside, confirm exit
            confirm_exit = request.POST.get("confirm_exit", "no")
            if confirm_exit == "yes":
                attendance.is_inside = False
                attendance.save()
                return JsonResponse({"message": "Seat marked as exited."})
            return JsonResponse({"message": "This seat is already inside. Confirm exit?", "requires_confirmation": True})
        else:
            # Mark as entered
            attendance.is_inside = True
            attendance.save()
            return JsonResponse({"message": "Seat marked as entered."})
