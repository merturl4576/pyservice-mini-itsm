import re
import os

file_path = r'c:\Users\MERT\Desktop\servicenow python project\pyservice\templates\remote_support\session_room.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern:
# <small class="...">{{
#                                 msg.sender.get_full_name|default:msg.sender.username }} - {{ msg.created_at|time:"H:i"
#                                 }}</small>

# We want to match the interior of <small> and flatten it.
# The class attribute varies (text-muted vs text-white-50).

# Regex explanation:
# <small[^>]*> matches opening small tag
# \s*\{\{\s+ matches opening {{ and following whitespace
# (msg\.sender\.get_full_name\|default:msg\.sender\.username) capture group 1
# \s+\}\}\s+-\s+\{\{\s+ matches }} - {{ and whitespace
# (msg\.created_at\|time:"H:i") capture group 2
# \s+\}\} matches closing }}
# \s*</small> matches closing tag

# Since re.sub replaces the whole match, we need to capture the opening tag too.

# Let's try to just target the variable replacement, allowing for any surrounding context.
# We are replacing:
# {{
#     msg.sender.get_full_name|default:msg.sender.username }} - {{ msg.created_at|time:"H:i"
#     }}
# with:
# {{ msg.sender.get_full_name|default:msg.sender.username }} - {{ msg.created_at|time:"H:i" }}

regex_pattern = r'\{\{\s+msg\.sender\.get_full_name\|default:msg\.sender\.username\s+\}\}\s+-\s+\{\{\s+msg\.created_at\|time:"H:i"\s+\}\}'

replacement = '{{ msg.sender.get_full_name|default:msg.sender.username }} - {{ msg.created_at|time:"H:i" }}'

# Check if we find it
matches = re.findall(regex_pattern, content, flags=re.MULTILINE | re.DOTALL)
print(f"Found {len(matches)} matches.")

if len(matches) > 0:
    new_content = re.sub(regex_pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully fixed chat message tags.")
    else:
        print("Regex matched but sub failed (should unexpected).")
else:
    print("No matches found. Printing snippet to debug.")
    # Find "msg.sender" to see what it looks like
    idx = content.find("msg.sender")
    if idx != -1:
        print(repr(content[idx:idx+150]))
