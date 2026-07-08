#!/usr/bin/env python3
"""
check_diff.py - Audits the differences between the current branch and the clean upstream branch (as_upstream).
It lists unique EBT files and checks if modified sutta HTML files have the EBT UI enhancements.
"""

import os
import subprocess
import sys

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()

def main():
    # Ensure we run from the repository root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    os.chdir(repo_root)

    print("=== EBT Sync & Modification Auditor ===")
    
    # 1. Check if git repository is clean and we can find as_upstream
    branches = run_command("git branch")
    if "as_upstream" not in branches:
        print("Error: 'as_upstream' branch not found in local repository.", file=sys.stderr)
        sys.exit(1)
        
    print("\n--- 1. Unique EBT Files/Directories Status ---")
    unique_paths = [
        "parallels",
        "ebt-study",
        "ebt-study/māstudies",
        "home/mitra.html",
        "js/agama-controlpanel.js",
        "js/agama-en-index.js",
        "js/agama-footer.js",
        "js/dhammatalks-index.js",
        "js/parallels-data.js",
        "js/sutta-index.js",
        "js/sutta-search.js"
    ]
    for p in unique_paths:
        exists = os.path.exists(p)
        status = "Present" if exists else "Missing"
        print(f"[{'✓' if exists else '✗'}] {p}: {status}")
        
    print("\n--- 2. Core Files Modifications Status ---")
    core_files = [
        "index.html",
        ".gitignore",
        "js/footer.js",
        "css/css.css",
        "css/menu.css"
    ]
    for f in core_files:
        if not os.path.exists(f):
            print(f"[!] {f}: Does not exist locally.")
            continue
        # Compare with as_upstream
        diff = run_command(f"git diff as_upstream -- {f}")
        if diff:
            print(f"[✓] {f}: Modified (EBT changes applied)")
        else:
            print(f"[✗] {f}: Identical to upstream (EBT changes missing!)")
            
    print("\n--- 3. Sutta Files Integration Audit ---")
    print("Checking a sample of sutta files for EBT UI injection...")
    
    sutta_dirs = ["an", "sn", "mn", "dn", "ud", "dhp", "snp", "tha", "thi", "kp", "vi", "it", "kn", "guide"]
    total_checked = 0
    total_valid = 0
    missing_ebt = []
    
    # Walk through sutta and vinaya directories and check files
    for directory in sutta_dirs:
        if not os.path.exists(directory):
            continue
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".html") and not file.startswith("index") and not file.endswith("comp.html") and file != "eng_vibhanga.html":
                    filepath = os.path.join(root, file)
                    total_checked += 1
                    
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            # Check for theme-btns and sutta-search (Sutta files need both, Vinaya only theme-btns)
                            has_theme = "theme-btns" in content
                            needs_search = (directory != "vi")
                            has_search = "sutta-search.js" in content if needs_search else True
                            
                            if has_theme and has_search:
                                total_valid += 1
                            else:
                                missing_ebt.append(filepath)
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")
                        
    print(f"Checked {total_checked} sutta and vinaya files.")
    if total_checked > 0:
        print(f"Valid: {total_valid} / {total_checked} ({total_valid/total_checked*100:.1f}%)")
    else:
        print("No sutta or vinaya files found to check.")
    
    if missing_ebt:
        print(f"\n[!] Found {len(missing_ebt)} files missing EBT UI enhancements. First 10:")
        for path in missing_ebt[:10]:
            print(f"  - {path}")
    else:
        print("[✓] All checked sutta files have EBT UI enhancements correctly injected!")
        
if __name__ == "__main__":
    main()
