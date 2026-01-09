import re
import os

file_path = r'c:\Users\MERT\Desktop\servicenow python project\pyservice\templates\remote_support\queue.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Priority Badge in Active Sessions (has me-2 class)
# Pattern: <span class="badge bg-{{ session.get_priority_color }} me-2">{{ session.get_priority_display
#                         }}</span>
content = re.sub(
    r'<span class="badge bg-\{\{ session\.get_priority_color \}\} me-2">\{\{\s+session\.get_priority_display\s+\}\}',
    '<span class="badge bg-{{ session.get_priority_color }} me-2">{{ session.get_priority_display }}',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# Fix 2: AnyDesk ID in Active Sessions
# Pattern: <strong class="text-primary">{{ session.anydesk_id
#                         }}</strong>
content = re.sub(
    r'<strong class="text-primary">\{\{\s+session\.anydesk_id\s+\}\}',
    '<strong class="text-primary">{{ session.anydesk_id }}',
    content,
    flags=re.MULTILINE | re.DOTALL
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied active session display fixes to queue.html")
