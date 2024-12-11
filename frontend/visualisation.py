import json
import plotly.graph_objects as go  #pip install plotly

# Read the JSON data from a file
with open("exampleResponse.json", "r") as file:
    sample_data = json.load(file)

# Function to restructure the JSON data into a nested format and add color based on conditions
def restructure_json(data):
    result = {}

    for key, value in data.items():
        # Split the key into folder structure
        parts = key.strip('/').split('/')
        
        # Navigate through the structure to organize the data
        current = result
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        
        # Add the file or subfolder to the parent folder
        file_or_folder = parts[-1]
        current.setdefault(file_or_folder, {})

        # Assign the color and messages based on conditions
        color, messages = get_color_based_on_conditions(file_or_folder, value)
        if color:
            # Set the color in the structure
            current[file_or_folder]['color'] = color
            # If messages exist, add them to the structure
            if messages:
                current[file_or_folder]['messages'] = messages

    return result

# Function to check conditions for files and folders and assign colors and messages
def get_color_based_on_conditions(key, value):
    color = None
    messages = []

    if isinstance(value, dict):
        # Check for hidden status
        if 'hidden_status' in value and value['hidden_status'] is not None and value['hidden_status'].get('is_hidden', True):
            color = 'red'
            reasons = value['hidden_status'].get('reasons', [])
            # Append all messages in the reasons list
            for reason in reasons:
                messages.append(f"Hidden status: {reason}")

        # Check for virus scan status
        if 'virus_scan' in value.get('hashes', {}) and value['hashes']['virus_scan'] is not None:
            color = 'red'
            message = value['hashes']['virus_scan'].get('message', 'No message provided')
            messages.append(f"Virus scan: {message}")

        # Check for file type
        if 'file_type' in value and value['file_type'] is not None and value['file_type']['analysis'].get('is_suspicious', True):
            color = 'red'
            reasons = value['file_type']['analysis'].get('reasons', [])
            # Append all messages in the reasons list
            for reason in reasons:
                messages.append(f"Suspicious file type: {reason}")

    return color, messages  # Return color and a list of messages


# Restructure the data and assign colors
restructured_data = restructure_json(sample_data)

# Function to flatten the dictionary into a format suitable for Sunburst chart
def flatten_for_sunburst(data, parent='', sunburst_data=[]):
    if not parent:  # If parent is empty, it means it's the root
        sunburst_data.append({
            'id': 'root',  # Add root as the central node
            'parent': '',
            'label': 'root',  # Label as "root"
            'color': 'lightgrey',  # Root is lightgrey
            'customdata': []  # No messages for the root
        })
    
    if isinstance(data, dict):  # Folder structure
        for key, value in data.items():
            new_parent = 'root' if parent == '' else parent  # Ensure root is the parent for top-level folders
            color = None  # Default color
            label = key  # Start with the key as the label
            messages = []  # Initialize messages list

            # Check if the value is a dictionary (folder)
            if isinstance(value, dict):
                color = value.get('color', None)  # Get the color if it exists
                
                # Append the messages to the messages list if they exist
                if 'messages' in value:
                    messages = value['messages']  # Get messages

                # Join messages with newline characters to format them line by line
                messages_str = '<br>'.join(messages)

                # Add the node to the sunburst data
                sunburst_data.append({
                    'id': new_parent + '/' + key,
                    'parent': new_parent,
                    'label': label,  # Include the label without the messages
                    'color': color if color else 'blue',  # Use 'blue' for folders without 'red'
                    'customdata': messages_str  # Attach the formatted messages
                })
                
                # Recursively flatten the data for nested structures
                flatten_for_sunburst(value, new_parent + '/' + key, sunburst_data)

    return sunburst_data

# Flatten the restructured data for Sunburst
sunburst_data = flatten_for_sunburst(restructured_data)

# Extract the IDs, labels, parents, colors, and messages (customdata)
ids = [item['id'] for item in sunburst_data]
labels = [item['label'] for item in sunburst_data]
parents = [item['parent'] for item in sunburst_data]
colors = [item['color'] for item in sunburst_data]
customdata = [item['customdata'] for item in sunburst_data]

# Create a Sunburst plot
fig = go.Figure(go.Sunburst(
    ids=ids,
    labels=labels,
    parents=parents,
    marker=dict(
        colors=colors  # Set colors for each node
    ),
    customdata=customdata,  # Add custom data (messages) for hover
    hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>"  # Display messages on hover
))

# Update layout and title
fig.update_layout(
    title="Sunburst Visualization of Folder Structure",
    margin=dict(t=0, l=0, r=0, b=0)
)

# Show the plot
fig.show()