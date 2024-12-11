import json
import plotly.graph_objects as go

def generate_visualization(json_data):
    # Existing code but as a function
    def restructure_json(data):
        result = {}
        for key, value in data.items():
            parts = key.strip('/').split('/')
            current = result
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            file_or_folder = parts[-1]
            current.setdefault(file_or_folder, {})
            color, messages = get_color_based_on_conditions(file_or_folder, value)
            if color:
                current[file_or_folder]['color'] = color
                if messages:
                    current[file_or_folder]['messages'] = messages
        return result

    def get_color_based_on_conditions(key, value):
        color = None
        messages = []
        if isinstance(value, dict):
            if 'hidden_status' in value and value['hidden_status'] is not None and value['hidden_status'].get('is_hidden', True):
                color = 'red'
                reasons = value['hidden_status'].get('reasons', [])
                for reason in reasons:
                    messages.append(f"Hidden status: {reason}")
            if 'virus_scan' in value.get('hashes', {}) and value['hashes']['virus_scan'] is not None:
                color = 'red'
                message = value['hashes']['virus_scan'].get('message', 'No message provided')
                messages.append(f"Virus scan: {message}")
            if 'file_type' in value and value['file_type'] is not None and value['file_type']['analysis'].get('is_suspicious', True):
                color = 'red'
                reasons = value['file_type']['analysis'].get('reasons', [])
                for reason in reasons:
                    messages.append(f"Suspicious file type: {reason}")
        return color, messages

    def flatten_for_sunburst(data, parent='', sunburst_data=[]):
        if not parent:
            sunburst_data.append({
                'id': 'root',
                'parent': '',
                'label': 'root',
                'color': 'lightgrey',
                'customdata': []
            })
        if isinstance(data, dict):
            for key, value in data.items():
                new_parent = 'root' if parent == '' else parent
                color = None
                label = key
                messages = []
                if isinstance(value, dict):
                    color = value.get('color', None)
                    if 'messages' in value:
                        messages = value['messages']
                    messages_str = '<br>'.join(messages)
                    sunburst_data.append({
                        'id': new_parent + '/' + key,
                        'parent': new_parent,
                        'label': label,
                        'color': color if color else 'blue',
                        'customdata': messages_str
                    })
                    flatten_for_sunburst(value, new_parent + '/' + key, sunburst_data)
        return sunburst_data

    # Process the data
    restructured_data = restructure_json(json_data)
    sunburst_data = flatten_for_sunburst(restructured_data)

    # Create the visualization
    ids = [item['id'] for item in sunburst_data]
    labels = [item['label'] for item in sunburst_data]
    parents = [item['parent'] for item in sunburst_data]
    colors = [item['color'] for item in sunburst_data]
    customdata = [item['customdata'] for item in sunburst_data]

    fig = go.Figure(go.Sunburst(
        ids=ids,
        labels=labels,
        parents=parents,
        marker=dict(
            colors=colors
        ),
        customdata=customdata,
        hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>"
    ))

    fig.update_layout(
        title="Sunburst Visualization of Folder Structure",
        margin=dict(t=0, l=0, r=0, b=0),
        width=None,
        height=None,
        autosize=True
    )

    # Return the plot as HTML
    return fig.to_json()

if __name__ == "__main__":
    # Test with example data
    with open("exampleResponse.json", "r") as file:
        sample_data = json.load(file)
    generate_visualization(sample_data)