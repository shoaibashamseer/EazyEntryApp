document.addEventListener('DOMContentLoaded', () => {
    const scanEntryBtn = document.getElementById('scan-entry-btn');
    const scanExitBtn = document.getElementById('scan-exit-btn');
    const attendanceList = document.getElementById('attendance-list');

    async function updateAttendanceList() {
        const response = await fetch('/attendance/current-day'); // Replace with your endpoint
        const data = await response.json();

        // Clear and update the attendance list
        attendanceList.innerHTML = '';
        data.forEach((item) => {
            const div = document.createElement('div');
            div.textContent = `${item.seat_type} - Seat ${item.seat_number}`;
            attendanceList.appendChild(div);
        });
    }

    async function scanQRCode(type) {
        // Mock QR Code scanning
        const qrCode = prompt('Enter QR Code data:'); // Replace with actual scanner logic
        if (!qrCode) return;

        const response = await fetch(`/attendance/${type}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ qr_code: qrCode }),
        });

        const data = await response.json();
        alert(data.message);

        if (data.success) {
            updateAttendanceList();
        }
    }

    scanEntryBtn.addEventListener('click', () => scanQRCode('entry'));
    scanExitBtn.addEventListener('click', () => scanQRCode('exit'));

    // Initial load of attendance list
    updateAttendanceList();
});
