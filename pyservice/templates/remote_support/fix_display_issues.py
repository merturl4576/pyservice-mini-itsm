import re
import os

file_path = r'c:\Users\MERT\Desktop\servicenow python project\pyservice\templates\remote_support\session_room.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: session.get_status_display
# Pattern: <span class="badge bg-{{ session.get_status_color }}">{{
#                             session.get_status_display }}</span>
# We want: ...color }}">{{ session.get_status_display }}</span>

content = re.sub(
    r'<span class="badge bg-\{\{ session\.get_status_color \}\}">\{\{\s+session\.get_status_display \}\}',
    '<span class="badge bg-{{ session.get_status_color }}">{{ session.get_status_display }}',
    content,
    flags=re.MULTILINE
)

# Fix 2: session.get_priority_display
# Pattern: <span class="badge bg-{{ session.get_priority_color }}">{{
#                             session.get_priority_display }}</span>

content = re.sub(
    r'<span class="badge bg-\{\{ session\.get_priority_color \}\}">\{\{\s+session\.get_priority_display \}\}',
    '<span class="badge bg-{{ session.get_priority_color }}">{{ session.get_priority_display }}',
    content,
    flags=re.MULTILINE
)

# Fix 3: Technician name
# Pattern: {% if session.technician %}{{
#                         session.technician.get_full_name|default:session.technician.username }}
# We want: ...{% if session.technician %}{{ session.technician.get_full_name|default:session.technician.username }}

content = re.sub(
    r'{% if session\.technician %}\{\{\s+session\.technician\.get_full_name\|default:session\.technician\.username \}\}',
    '{% if session.technician %}{{ session.technician.get_full_name|default:session.technician.username }}',
    content,
    flags=re.MULTILINE
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully joined split variable tags.")
