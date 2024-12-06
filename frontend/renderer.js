document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed.");

    const fetchDrivesButton = document.getElementById('fetchDrives');
    const scanButton = document.getElementById('scanDrive');
    const driveSelect = document.getElementById('driveSelect');
    const output = document.getElementById('output');

    fetchDrivesButton.addEventListener('click', async () => {
        console.log("Fetch Drives button clicked.");

        try {
            const response = await fetch('http://127.0.0.1:8000/drives');
            const drives = await response.json();

            driveSelect.innerHTML = '<option value="">Select a drive</option>';
            drives.forEach(drive => {
                const option = document.createElement('option');
                option.value = drive;
                option.textContent = drive;
                driveSelect.appendChild(option);
            });

            console.log("Drives fetched successfully:", drives);
        } catch (error) {
            console.error("Fetch error:", error);
            output.textContent = `Error: ${error.message}`;
        }
    });

    scanButton.addEventListener('click', async () => {
        console.log("Scan Drive button clicked.");

        const drivePath = driveSelect.value;
        if (!drivePath) {
            output.textContent = "Please select a drive.";
            return;
        }

        console.log(`Drive path selected: ${drivePath}`);

        try {
            const response = await fetch(`http://127.0.0.1:8000/scan?drive=${encodeURIComponent(drivePath)}`);
            const result = await response.json();

            if (result.status === 'success') {
                console.log("Fetch successful:", result);
                output.textContent = JSON.stringify(result.data, null, 4);
            } else {
                console.error("Error from API:", result.message);
                output.textContent = `Error: ${result.message}`;
            }
        } catch (error) {
            console.error("Fetch error:", error);
            output.textContent = `Error: ${error.message}`;
        }
    });
});