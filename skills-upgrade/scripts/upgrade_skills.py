#!/usr/bin/env python3
import os
import sys
import urllib.request
import urllib.parse
import json
import subprocess

# Default directory for Antigravity skills
SKILLS_DIR = os.path.expanduser("~/.gemini/antigravity/skills")

# Skills that should not be automatically upgraded
IGNORED_SKILLS = ["skills-discovery"]

def search_skill_namespace(skill_folder_name):
    # Using space instead of hyphens yields better search results in the API
    search_query = skill_folder_name.replace('-', ' ')
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://claude-plugins.dev/api/skills?q={encoded_query}&limit=20"
    
    import ssl
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            skills = data.get('skills', [])
            
            # Find the exact match first
            matches = [s for s in skills if s['name'].lower() == skill_folder_name.lower()]
            
            # Fallback to loose matching if no exact match is found
            if not matches:
                matches = [s for s in skills if skill_folder_name.lower() in s['name'].lower()]
            
            if not matches:
                return None
                
            # Pick the skill with the highest stars if multiple matches exist
            best_match = sorted(matches, key=lambda x: x.get('stars', 0), reverse=True)[0]
            return best_match['namespace']
    except Exception as e:
        print(f"  [X] Error checking API for {skill_folder_name}: {e}")
        return None

def main():
    if not os.path.exists(SKILLS_DIR):
        print(f"Skills directory not found at {SKILLS_DIR}")
        sys.exit(1)

    print("🔍 Scanning installed skills...")
    # Get all immediate subdirectories representing the installed skills
    installed_skills = [
        d for d in os.listdir(SKILLS_DIR) 
        if os.path.isdir(os.path.join(SKILLS_DIR, d)) and not d.startswith('.')
    ]
    
    if not installed_skills:
        print("No skills found.")
        return

    print(f"📦 Found {len(installed_skills)} skills: {', '.join(installed_skills)}\n")

    for skill in installed_skills:
        print(f"🔄 Processing: {skill}")
        
        if skill in IGNORED_SKILLS:
            print(f"  [⏭️] Skipping '{skill}' (in IGNORED_SKILLS list).")
            continue
            
        namespace = search_skill_namespace(skill)
        
        if not namespace:
            print(f"  [!] Could not find matching registry entry for '{skill}'. Skipping.")
            continue
            
        print(f"  [*] Found namespace: {namespace}. Upgrading...")
        
        # Execute the upgrade via npx skills-installer
        result = subprocess.run(
            ["npx", "-y", "skills-installer", "install", namespace, "--client", "antigravity"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        
        if result.returncode == 0:
            print(f"  [+] Upgrade complete for {skill}!\n")
        else:
            print(f"  [X] Failed to upgrade {skill}. Output:\n{result.stdout}\n")

if __name__ == "__main__":
    main()
