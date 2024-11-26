from django.contrib import admin
from .models import Event, SeatAllocation, DailyAttendance,EventDay,SeatType
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BulkQRCodeUploadForm
import zipfile
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

class EventDayInline(admin.TabularInline):
    model = EventDay
    extra = 1

class SeatTypeInline(admin.TabularInline):
    model = SeatType
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'number_of_days', 'created_at')
    inlines = [EventDayInline ,SeatTypeInline]

    def number_of_days(self, obj):
        return obj.days.count()
    number_of_days.short_description = "Number of Days"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('upload-qrcodes/', self.admin_site.admin_view(self.upload_qrcodes), name='upload_qrcodes'),
        ]
        return custom_urls + urls

    def upload_qrcodes(self, request):
        if request.method == "POST":
            form = BulkQRCodeUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['csv_file']
                zip_file = form.cleaned_data['zip_file']

                try:
                    # Process CSV file
                    qr_data_dict = {}
                    csv_content = csv_file.read().decode('utf-8').splitlines()
                    reader = csv.reader(csv_content)
                    for row in reader:
                        if len(row) != 2:
                            messages.error(request, "Invalid CSV format. Each row must contain QR code data and event name.")
                            return redirect('admin:upload_qrcodes')
                        qr_code_data, event_name = row
                        qr_data_dict[qr_code_data] = event_name

                    # Process ZIP file
                    if zip_file:
                        zip_content = zipfile.ZipFile(zip_file)
                        for file_name in zip_content.namelist():
                            qr_code_data = file_name.split('.')[0]  # Match filename to QR code data
                            if qr_code_data in qr_data_dict:
                                event = Event.objects.filter(name=qr_data_dict[qr_code_data]).first()
                                if event:
                                    qr_image = zip_content.open(file_name)

                                    # Create SeatAllocation object
                                    SeatAllocation.objects.create(
                                        event=event,
                                        qr_code_data=qr_code_data,
                                        qr_code_image=InMemoryUploadedFile(
                                            file=BytesIO(qr_image.read()),
                                            field_name="qr_code_image",
                                            name=file_name,
                                            content_type="image/png",
                                            size=qr_image.tell(),
                                            charset=None
                                        )
                                    )

                    messages.success(request, "QR codes uploaded successfully.")
                    return redirect('admin:upload_qrcodes')
                except Exception as e:
                    messages.error(request, f"An error occurred: {e}")
                    return redirect('admin:upload_qrcodes')

        else:
            form = BulkQRCodeUploadForm()
        return render(request, 'admin/upload_qrcodes.html', {'form': form, 'title': 'Upload QR Codes'})

@admin.register(SeatAllocation)
class SeatAllocationAdmin(admin.ModelAdmin):
    list_display = ('event', 'qr_code_data', 'is_occupied')
    list_filter = ('event',)


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = ('get_event_name', 'get_qr_code_data', 'is_inside', 'last_updated')
    list_filter = ('event_day__event', 'is_inside')  # Use related fields for filtering

    def get_event_name(self, obj):
        """Retrieve the event name from the related EventDay."""
        return obj.event_day.event.name
    get_event_name.short_description = 'Event Name'

    def get_qr_code_data(self, obj):
        """Retrieve QR code data from the related SeatAllocation."""
        return obj.seat_allocation.qr_code_data
    get_qr_code_data.short_description = 'QR Code Data'