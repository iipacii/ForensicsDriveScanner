function getColorAndMessages(value) {
    let color = null;
    let messages = [];

    if (value.hidden_status && value.hidden_status.is_hidden) {
        color = 'red';
        value.hidden_status.reasons.forEach(reason => 
            messages.push(`Hidden status: ${reason}`));
    }
    
    if (value.hashes?.virus_scan) {
        color = 'red';
        messages.push(`Virus scan: ${value.hashes.virus_scan.message || 'No message provided'}`);
    }
    
    if (value.file_type?.analysis?.is_suspicious) {
        color = 'red';
        value.file_type.analysis.reasons.forEach(reason => 
            messages.push(`Suspicious file type: ${reason}`));
    }

    return { color, messages };
}

function restructureData(data) {
    const result = {};

    for (const [path, value] of Object.entries(data)) {
        const parts = path.split('/').filter(Boolean);
        let current = result;
        
        // Build path structure
        for (let i = 0; i < parts.length; i++) {
            const part = parts[i];
            current[part] = current[part] || {};
            
            if (i === parts.length - 1) {
                // Process leaf node
                const { color, messages } = getColorAndMessages(value);
                if (color) {
                    current[part].color = color;
                    current[part].messages = messages;
                }
            }
            current = current[part];
        }
    }
    
    return result;
}

function flattenForSunburst(data, parent = '', result = []) {
    if (parent === '') {
        result.push({
            id: 'root',
            parent: '',
            label: 'root',
            color: 'lightgrey',
            customdata: ''
        });
    }

    for (const [key, value] of Object.entries(data)) {
        const newParent = parent === '' ? 'root' : parent;
        const currentId = `${newParent}/${key}`;
        
        // Handle leaf nodes and intermediate nodes
        const color = value.color || 'blue';
        const messages = value.messages || [];
        const messagesStr = messages.join('<br>');

        result.push({
            id: currentId,
            parent: newParent,
            label: key,
            color: color,
            customdata: messagesStr
        });

        // Recursively process children if they exist
        if (Object.keys(value).some(k => k !== 'color' && k !== 'messages')) {
            flattenForSunburst(value, currentId, result);
        }
    }

    return result;
}



document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed");

    const fetchDrivesButton = document.getElementById('fetchDrives');
    const scanButton = document.getElementById('scanDrive');
    const openVisualizationButton = document.getElementById('openVisualization');
    const driveSelect = document.getElementById('driveSelect');
    const output = document.getElementById('output');
    const visualizationContainer = document.getElementById('visualizationContainer');

    fetchDrivesButton.addEventListener('click', async () => {
        console.log("Fetch Drives button clicked");

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
        console.log("Scan Drive button clicked");
    
        const drivePath = driveSelect.value;
        if (!drivePath) {
            output.textContent = "Please select a drive.";
            return;
        }
    
        try {
            visualizationContainer.style.display = 'block'; // Show container
            const response = await fetch(`http://127.0.0.1:8000/scan?drive=${encodeURIComponent(drivePath)}`);
            const result = await response.json();

            console.log("Scan result:", result);
    
            if (result.status === 'success') {
                // Process the data
                const restructured = restructureData(result.data);
                const sunburstData = flattenForSunburst(restructured);
    
                // Prepare Plotly data
                const plotData = [{
                    ids: sunburstData.map(item => item.id),
                    labels: sunburstData.map(item => item.label),
                    parents: sunburstData.map(item => item.parent),
                    type: 'sunburst',
                    marker: { colors: sunburstData.map(item => item.color) },
                    customdata: sunburstData.map(item => item.customdata),
                    hovertemplate: '<b>%{label}</b><br>%{customdata}<extra></extra>'
                }];
                
                const layout = {
                    margin: { t: 0, l: 0, r: 0, b: 0 },
                    width: visualizationContainer.clientWidth,
                    height: visualizationContainer.clientHeight,
                    autosize: true
                };
                
                Plotly.newPlot('chart', plotData, layout);
                output.textContent = '';
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