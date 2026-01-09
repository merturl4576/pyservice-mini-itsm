import re
import os

file_path = r'c:\Users\MERT\Desktop\servicenow python project\pyservice\templates\remote_support\session_room.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# --- FIX 1: SESSION INFO TAGS ---

# Fix Status
# Pattern: <span ...>{{
#                             session.get_status_display }}</span>
content = re.sub(
    r'<span class="badge bg-\{\{ session\.get_status_color \}\}">\{\{\s+session\.get_status_display\s+\}\}',
    '<span class="badge bg-{{ session.get_status_color }}">{{ session.get_status_display }}',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# Fix Priority
# Pattern: <span ...>{{
#                             session.get_priority_display }}</span>
content = re.sub(
    r'<span class="badge bg-\{\{ session\.get_priority_color \}\}">\{\{\s+session\.get_priority_display\s+\}\}',
    '<span class="badge bg-{{ session.get_priority_color }}">{{ session.get_priority_display }}',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# Fix Technician (Session Info) - This one is tricky because of the if/else around it sometimes, or just the dd tag
# <dd class="col-7">{% if session.technician %}{{
#                         session.technician.get_full_name|default:session.technician.username }}{% else %}
content = re.sub(
    r'([ \t]*)\{% if session\.technician %\}\{\{\s+session\.technician\.get_full_name\|default:session\.technician\.username\s+\}\}',
    r'\1{% if session.technician %}{{ session.technician.get_full_name|default:session.technician.username }}',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# Also fix the requester if it's split
# <dd class="col-7">{{
#                             session.requester.get_full_name|default:session.requester.username }}</dd>
content = re.sub(
    r'<dd class="col-7">\{\{\s+session\.requester\.get_full_name\|default:session\.requester\.username\s+\}\}</dd>',
    '<dd class="col-7">{{ session.requester.get_full_name|default:session.requester.username }}</dd>',
    content,
    flags=re.MULTILINE | re.DOTALL
)


# --- FIX 2: CHAT MESSAGE TAGS ---

# Sender Name and Timestamp
# Pattern: <small ...>{{
#                                 msg.sender.get_full_name|default:msg.sender.username }} - {{ msg.created_at|time:"H:i"
#                                 }}</small>

# We'll do this in two steps or a robust regex.
# Let's target the inner content of the <small> tag.
content = re.sub(
    r'\}\}\{\{\s+msg\.sender\.get_full_name\|default:msg\.sender\.username\s+\}\}\s-\s\{\{\s+msg\.created_at\|time:"H:i"\s+\}\}</small>',
    '}}{{ msg.sender.get_full_name|default:msg.sender.username }} - {{ msg.created_at|time:"H:i" }}</small>',
    content,
    flags=re.MULTILINE | re.DOTALL
)
# The above regex assumes the class attribute part `...{% endif %}"` ends with `}}` which isn't right.
# The class attribute ends with `">`.
# <small class="...">{{ ... }} - {{ ... }}</small>

content = re.sub(
    r'(class="[^"]+">)\{\{\s+msg\.sender\.get_full_name\|default:msg\.sender\.username\s+\}\}\s-\s\{\{\s+msg\.created_at\|time:"H:i"\s+\}\}</small>',
    r'\1{{ msg.sender.get_full_name|default:msg.sender.username }} - {{ msg.created_at|time:"H:i" }}</small>',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# --- FIX 3: GENERIC CLEANUP ---
# Just in case specific regexes fail, let's look for `{{` at end of line and join it with next line
# ONLY if the next line starts with whitespace and then some content and `}}`.
# This is risky but effective if scoped.

def join_variable_tags(text):
    # Matches {{ at end of line, followed by whitespace, content, whitespace, }}
    pattern = r'\{\{\s*\n\s*(.*?)\s*\}\}'
    return re.sub(pattern, r'{{\1}}', text)

# Apply generic fix 
content = join_variable_tags(content)

# Apply generic fix for {% ... %} as well?
# pattern_block = r'\{%\s*\n\s*(.*?)\s*%\}'
# content = re.sub(pattern_block, r'{% \1 %}', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Applied comprehensive display fixes.")
