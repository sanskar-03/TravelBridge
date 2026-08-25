import os
from pathlib import Path

def fix_file(filepath):
    path = Path(filepath)
    if path.exists():
        content = path.read_text(encoding='utf-8')
        # Replace the markdown artifact with the plain URL
        bad_string = "[http://127.0.0.1:3000](http://127.0.0.1:3000)"
        good_string = "http://127.0.0.1:3000"
        
        if bad_string in content:
            content = content.replace(bad_string, good_string)
            path.write_text(content, encoding='utf-8')
            print(f"✅ Fixed CORS artifact in {filepath}")
        else:
            print(f"👍 No artifact found in {filepath}")
    else:
        print(f"ℹ️ File {filepath} not found.")

if __name__ == "__main__":
    print("🚀 Fixing CORS URLs...")
    fix_file(".env")
    fix_file(".env.example")
    fix_file("backend/travelbridge/settings.py")