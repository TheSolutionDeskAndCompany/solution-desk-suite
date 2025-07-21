from flask import Blueprint, render_template, request, jsonify
import json

flowmatic_bp = Blueprint('flowmatic', __name__, template_folder='templates')

import re

def parse_step_with_metrics(step_text):
    """
    Parse step text to extract name, duration, and automation status.
    Supports formats like:
    - "Customer places order (2h, manual)"
    - "Payment processed (30m)"
    - "Review & approval (2h, manual)"
    """
    step_data = {
        'name': step_text.strip(),
        'duration_minutes': 0,
        'is_manual': False,
        'has_metrics': False
    }
    
    # Look for duration and tags in parentheses
    match = re.search(r'\((.*?)\)', step_text)
    if match:
        annotations = match.group(1).lower()
        step_data['name'] = step_text[:match.start()].strip()
        step_data['has_metrics'] = True
        
        # Parse duration
        duration_match = re.search(r'(\d+(?:\.\d+)?)\s*(h|hr|hour|hours|m|min|minute|minutes)', annotations)
        if duration_match:
            value = float(duration_match.group(1))
            unit = duration_match.group(2)
            if unit in ['h', 'hr', 'hour', 'hours']:
                step_data['duration_minutes'] = int(value * 60)
            else:
                step_data['duration_minutes'] = int(value)
        
        # Check if manual
        if 'manual' in annotations:
            step_data['is_manual'] = True
    
    # Fallback: check for manual keywords in step name
    manual_keywords = ['manual', 'manually', 'hand', 'paper', 'spreadsheet']
    if any(keyword in step_data['name'].lower() for keyword in manual_keywords):
        step_data['is_manual'] = True
    
    return step_data

def analyze_process(parsed_steps):
    """
    Analyze parsed process steps and provide improvement suggestions.
    """
    hints = []
    total_duration = sum(step['duration_minutes'] for step in parsed_steps)
    
    # Duration-based analysis
    if total_duration > 0:
        longest_step = max(parsed_steps, key=lambda s: s['duration_minutes'])
        if longest_step['duration_minutes'] > 60:
            hints.append(f"⏱️ '{longest_step['name']}' takes over an hour—consider splitting it or automating part of it.")
        
        hints.append(f"📊 Total cycle time: {total_duration // 60}h {total_duration % 60}m")
    
    # Manual step analysis
    manual_steps = [step for step in parsed_steps if step['is_manual']]
    if manual_steps:
        for step in manual_steps:
            hints.append(f"🛠️ '{step['name']}' is manual—could we streamline or script this?")
    
    # Process complexity
    if len(parsed_steps) > 6:
        hints.append("Your process has many steps—consider breaking it into smaller sub-processes for better clarity.")
    elif len(parsed_steps) < 2:
        hints.append("Try adding more detail to see a complete process flow visualization.")
    
    # Approval bottlenecks
    approval_keywords = ['approve', 'review', 'check', 'verify', 'confirm']
    approval_steps = [step for step in parsed_steps if any(keyword in step['name'].lower() for keyword in approval_keywords)]
    if len(approval_steps) > 2:
        hints.append("Multiple approval steps detected—streamline decision points to reduce delays.")
    
    # Communication analysis
    comm_keywords = ['email', 'notify', 'send', 'call', 'message', 'inform']
    comm_steps = [step for step in parsed_steps if any(keyword in step['name'].lower() for keyword in comm_keywords)]
    if len(comm_steps) > 1:
        hints.append("Consider batching notifications or using automated status updates.")
    
    if not hints:
        hints.append("Your process looks streamlined! Consider documenting decision points and success metrics.")
    
    return hints

@flowmatic_bp.route('/', methods=['GET', 'POST'])
def index():
    steps = []
    hints = []
    process_description = ''
    
    if request.method == 'POST':
        process_description = request.form.get('process', '').strip()
        
        if process_description:
            # Parse steps with metrics
            raw_steps = process_description.split('→')
            parsed_steps = []
            
            for i, step_text in enumerate(raw_steps):
                step_text = step_text.strip()
                if step_text and len(step_text) > 3:
                    step_data = parse_step_with_metrics(step_text)
                    step_data['id'] = i + 1
                    step_data['type'] = 'process'
                    parsed_steps.append(step_data)
                    
                    # For template compatibility
                    steps.append({
                        'id': i + 1,
                        'text': step_data['name'],
                        'type': 'process',
                        'duration_minutes': step_data['duration_minutes'],
                        'is_manual': step_data['is_manual'],
                        'has_metrics': step_data['has_metrics']
                    })
            
            # Generate improvement hints based on parsed data
            hints = analyze_process(parsed_steps)
    
    return render_template('flowmatic.html', 
                         steps=steps, 
                         hints=hints,
                         process_description=process_description)

@flowmatic_bp.route('/generate', methods=['POST'])
def generate_process():
    """Generate a process visualization from user input via AJAX"""
    data = request.get_json()
    process_description = data.get('description', '')
    
    # Simple process generation logic (can be enhanced with AI later)
    steps = []
    if process_description:
        # Basic parsing - split by common indicators
        raw_steps = process_description.replace('.', '|').replace(',', '|').split('|')
        for i, step in enumerate(raw_steps):
            step = step.strip()
            if step and len(step) > 3:
                steps.append({
                    'id': i + 1,
                    'text': step,
                    'type': 'process'
                })
    
    return jsonify({
        'steps': steps,
        'connections': [{'from': i, 'to': i + 1} for i in range(1, len(steps))]
    })