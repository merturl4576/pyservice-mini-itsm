import re
import os

file_path = r'c:\Users\MERT\Desktop\servicenow python project\pyservice\templates\remote_support\queue.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Priority display
# Pattern: <span ...>{{ session.get_priority_display
#                             }}</span>
# We want to join this.
content = re.sub(
    r'<span class="badge bg-\{\{ session\.get_priority_color \}\}">\{\{\s+session\.get_priority_display\s+\}\}',
    '<span class="badge bg-{{ session.get_priority_color }}">{{ session.get_priority_display }}',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# Fix 2: Requester Name
# Pattern: <i ...></i>{{
#                         session.requester.get_full_name|default:session.requester.username }}
content = re.sub(
    r'<i class="bi bi-person me-1"></i>\{\{\s+session\.requester\.get_full_name\|default:session\.requester\.username\s+\}\}',
    '<i class="bi bi-person me-1"></i>{{ session.requester.get_full_name|default:session.requester.username }}',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# Fix 3: Technician Name
# Pattern: <i ...></i>{{
#                         session.technician.get_full_name|default:session.technician.username }}
content = re.sub(
    r'<i class="bi bi-headset me-1"></i>\{\{\s+session\.technician\.get_full_name\|default:session\.technician\.username\s+\}\}',
    '<i class="bi bi-headset me-1"></i>{{ session.technician.get_full_name|default:session.technician.username }}',
    content,
    flags=re.MULTILINE | re.DOTALL
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully joined split tags in queue.html")
