# This script bundles the project into tbw-ebt.zip, excluding EBT sync workflows, agent guidelines, and Git configurations.
import os
import zipfile

def main():
    # Ensure we run from the repository root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    os.chdir(repo_root)

    zip_filename = "tbw-ebt.zip"
    
    # Files and folders to exclude
    exclude_dirs = {".git", "kamma", ".claude", ".agents"}
    exclude_files = {"AGENTS.md", "CLAUDE.md", ".gitignore", zip_filename}
    
    print(f"Creating archive {zip_filename}...")
    
    file_count = 0
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("."):
            # Filter out excluded directories in-place to prevent walking them
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file in exclude_files:
                    continue
                
                # Build relative path
                filepath = os.path.normpath(os.path.join(root, file))
                # Skip if it is a directory or doesn't exist
                if not os.path.isfile(filepath):
                    continue
                    
                # Do not zip paths starting with excluded directories or files
                parts = filepath.split(os.sep)
                if any(p in exclude_dirs for p in parts) or parts[-1] in exclude_files:
                    continue
                
                # Add to zip
                zipf.write(filepath)
                file_count += 1
                
    print(f"Archive created successfully with {file_count} files.")

if __name__ == "__main__":
    main()
