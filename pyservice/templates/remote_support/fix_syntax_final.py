import re
import os

file_path = r'c:\Users\MERT\Desktop\servicenow python project\pyservice\templates\remote_support\session_room.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Generic fix for ANY block tag split across lines
# Matches {% followed by content with newlines before %}
# We'll replace newlines with spaces within the tag
def join_tags(match):
    tag_content = match.group(0)
    # Replace newlines and multiple spaces with single space
    clean = re.sub(r'\s+', ' ', tag_content)
    return clean

# Fix {% ... %} splits
content = re.sub(
    r'\{%.*?%\}', 
    join_tags, 
    content, 
    flags=re.DOTALL
)

# Fix {{ ... }} splits
content = re.sub(
    r'\{\{.*?\}\}', 
    join_tags, 
    content, 
    flags=re.DOTALL
)

# Specific fixes for aesthetic formatting if needed (removing extra spaces)
content = content.replace('{% endif %}', '{% endif %}')
content = content.replace('{% else %}', '{% else %}')

# Validate counts
open_ifs = len(re.findall(r'\{% if ', content))
end_ifs = len(re.findall(r'\{% endif %\}', content))

print(f"Fixed content. Open IFs: {open_ifs}, End IFs: {end_ifs}")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
