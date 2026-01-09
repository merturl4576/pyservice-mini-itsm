import os

file_path = r'c:\Users\MERT\Desktop\servicenow python project\pyservice\templates\remote_support\session_room.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Join split endif
# "Session Completed</span>{%\n                    endif %}"
# We will look for "{%\n" and "endif %}" pattern more loosely or just replace the specific string locally.

# Let's try a robust replace.
# The split looks like: ...Completed</span>{%\n                    endif %}
# We want: ...Completed</span>{% endif %}

fixed_content = content.replace("Session Completed</span>{%\n                    endif %}", "Session Completed</span>{% endif %}")
fixed_content = fixed_content.replace("Session Completed</span>{%\n                    endif %}", "Session Completed</span>{% endif %}") # Duplicate just in case

# Try generic regex-like replacement for specific lines if exact string match fails due to spaces
import re
# Pattern 1: ...Completed</span>{% \s+ endif %}
fixed_content = re.sub(r'Session Completed</span>{%\s+endif %}', 'Session Completed</span>{% endif %}', fixed_content)


# Fix 2: Join split else
# "...request...{% else\n                        %}No messages..."
# We want: ...request...{% else %}No messages...

fixed_content = re.sub(r'waiting for a technician to accept your request...{% else\s+%}No messages', 'Waiting for a technician to accept your request...{% else %}No messages', fixed_content, flags=re.IGNORECASE)

# Verify if changed
if content == fixed_content:
    print("No changes were made. Patterns might not match.")
    # Debug: print relevant parts
    print("Debug - Content around broken area 1:")
    idx = content.find("Session Completed")
    if idx != -1:
        print(repr(content[idx:idx+100]))
    
    print("Debug - Content around broken area 2:")
    idx = content.find("technician to accept your request")
    if idx != -1:
        print(repr(content[idx:idx+100]))

else:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    print("Successfully wrote fixed content to file.")
