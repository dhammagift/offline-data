# This script analyzes differences between the current branch and as_upstream to document every EBT modification.
import subprocess
import sys

def get_git_diff(filename):
    try:
        res = subprocess.run(
            ["git", "diff", "as_upstream", "--", filename],
            capture_output=True,
            text=True,
            check=True
        )
        return res.stdout
    except Exception as e:
        print(f"Error running git diff on {filename}: {e}")
        return ""

def summarize_diff(diff_text):
    lines = diff_text.splitlines()
    added_lines = []
    removed_lines = []
    
    current_hunk = []
    hunks = []
    
    for line in lines:
        if line.startswith("@@"):
            if current_hunk:
                hunks.append(current_hunk)
                current_hunk = []
        elif line.startswith("+") and not line.startswith("+++"):
            added_lines.append(line[1:])
            current_hunk.append(line)
        elif line.startswith("-") and not line.startswith("---"):
            removed_lines.append(line[1:])
            current_hunk.append(line)
            
    if current_hunk:
        hunks.append(current_hunk)
        
    return len(added_lines), len(removed_lines), hunks

def main():
    # Ensure we run from the repository root
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    os.chdir(repo_root)

    core_files = [
        ".gitignore",
        "index.html",
        "css/css.css",
        "css/menu.css",
        "css/w3.css",
        "js/footer.js",
        "js/controlpanel.js"
    ]
    
    print("# EXHAUSTIVE CATALOG OF CORE FILE CHANGES VS UPSTREAM\n")
    
    for f in core_files:
        print(f"## File: `{f}`")
        diff = get_git_diff(f)
        if not diff:
            print("No differences found.\n")
            continue
            
        added, removed, hunks = summarize_diff(diff)
        print(f"- Total Lines Added: {added}")
        print(f"- Total Lines Removed/Replaced: {removed}")
        print("- Detailed Modifications:")
        
        # Parse hunk hunks to make it human readable
        # Group adjacent additions/deletions
        hunk_idx = 1
        for hunk in hunks:
            adds = [l[1:] for l in hunk if l.startswith("+")]
            dels = [l[1:] for l in hunk if l.startswith("-")]
            
            print(f"  {hunk_idx}. Hunk change:")
            if dels:
                print("     * **Removed/Replaced**:")
                for d in dels[:5]:  # Limit to 5 for readability
                    clean_d = d.strip()
                    if clean_d:
                        print(f"       `{clean_d}`")
                if len(dels) > 5:
                    print(f"       *(... and {len(dels) - 5} more lines)*")
            if adds:
                print("     * **Added/Substituted**:")
                for a in adds[:5]:  # Limit to 5 for readability
                    clean_a = a.strip()
                    if clean_a:
                        print(f"       `{clean_a}`")
                if len(adds) > 5:
                    print(f"       *(... and {len(adds) - 5} more lines)*")
            hunk_idx += 1
        print("\n")

if __name__ == "__main__":
    main()
