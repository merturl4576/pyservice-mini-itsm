import re
import os

file_path = r'c:\Users\MERT\Desktop\servicenow python project\pyservice\templates\remote_support\session_room.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Join split elif/endif (Waiting for technician)
# Pattern: {% elif session.status == 'completed' %}...{%
#                     endif %}
content = re.sub(
    r'\{% elif session\.status == \'completed\' %\}.+?\{%\s+endif %\}',
    lambda m: m.group(0).replace('\n', '').replace('                    ', ''),
    content,
    flags=re.DOTALL
)

# Alternative Fix 1 if regex above is too specific or fails on whitespace
# Specifically looking for the split at lines 103-104
content = content.replace("%}\n                    endif %}", "%}{% endif %}")


# Fix 2: Join split else/endif (No messages yet)
# Pattern: ...{% else
#                         %}No messages...
content = re.sub(
    r'\{% else\s+%\}\s*No messages yet',
    '{% else %}No messages yet',
    content
)
content = re.sub(
    r'No messages yet\. Start the conversation!\{%\s+endif %\}',
    'No messages yet. Start the conversation!{% endif %}',
    content
)

# Fix 3: Script tags?
# Line 183: let lastMessageId = {% if chat_messages and chat_messages.last %}{{ chat_messages.last.id }}{% else %}0{% endif %};
# This looks fine in the file view.

# FIX 4: CHECK FOR UNCLOSED BLOCKS
# The error "Invalid block tag on line 374: 'endblock', expected 'elif', 'else' or 'endif'"
# usually means an IF or FOR was opened but not closed.

# Let's count tags
open_ifs = len(re.findall(r'\{% if ', content))
open_fors = len(re.findall(r'\{% for ', content))
end_ifs = len(re.findall(r'\{% endif %\}', content))
end_fors = len(re.findall(r'\{% endfor %\}', content))

print(f"Open Ifs: {open_ifs}, End Ifs: {end_ifs}")
print(f"Open Fors: {open_fors}, End Fors: {end_fors}")

# Logic to manually fix the specific known splits that cause this:
# Line 103-104:
# {% elif session.status == 'completed' %}<span class="badge bg-success">Session Completed</span>{%
#                     endif %}
# This split tag "{%\n endif %}" is invalid.
content = content.replace("{%\n                    endif %}", "{% endif %}")

# Line 123-124:
# {% if session.status == 'pending' %}Waiting for a technician to accept your request...{% else
#                         %}No messages yet.
content = content.replace("{% else\n                        %}", "{% else %}")

# Line 124-124 (end)
# ... conversation!{% endif %}  <- This looks ok in view, but let's be sure.

# Line 374 is endblock.
# If we fixed the splits above, the block structure should be valid.

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Attempted to fix split tags.")
