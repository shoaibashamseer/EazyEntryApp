document.getElementById('scanEnter').addEventListener('click', function () {
    scanQRCode('entry');
});

document.getElementById('scanExit').addEventListener('click', function () {
    scanQRCode('exit');
});

function scanQRCode(action) {
    const qrCodeData = prompt("Please scan or enter the QR code data:");

    if (!qrCodeData) {
        alert("No QR code data entered.");
        return;
    }

    const confirmExit = action === 'exit' ? confirm("Are you sure you want to mark this seat as exited?") : null;

    fetch("{% url 'scan_qr_code_view' %}", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}' // CSRF Token for security
        },
        body: JSON.stringify({
            qr_code_data: qrCodeData,
            confirm_exit: action === 'exit' ? (confirmExit ? 'yes' : 'no') : null
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(`Error: ${data.error}`);
        } else if (data.requires_confirmation) {
            alert(data.message); // Handle confirmation separately if required
        } else {
            alert(data.message); // Show success message
            window.location.reload(); // Reload page to update seat counts
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Something went wrong. Please try again.");
    });
}