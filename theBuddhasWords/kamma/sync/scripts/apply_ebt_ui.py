#!/usr/bin/env python3
"""
apply_ebt_ui.py - Programmatically injects EBT UI enhancements into clean Sutta HTML files.
Usage:
  python3 apply_ebt_ui.py --file path/to/file.html
  python3 apply_ebt_ui.py --all
"""

import os
import re
import sys

# EBT UI replacement templates
THEME_BUTTONS_HTML = """\t\t<div class="theme-btns">
\t\t\t<button class="theme-btn theme-btn-light" onclick="set_theme('light')" title="Light mode">Light</button>
\t\t\t<button class="theme-btn theme-btn-sepia" onclick="set_theme('sepia')" title="Sepia mode">Sepia</button>
\t\t\t<button class="theme-btn theme-btn-dark" onclick="set_theme('dark')" title="Dark mode">Dark</button>
\t\t</div>"""

THEME_SEARCH_ROW_HTML = """\t\t<div class="theme-search-row">
\t\t\t<input id="sutta-search" type="text" placeholder="mn153, sn5.08" autocomplete="off" spellcheck="false">
\t\t\t<span id="sutta-search-error"></span>
\t\t</div>"""

BACK_TO_TOP_HTML = """<div class="back-to-top-row"><a href="javascript:void(0)" onclick="window.scrollTo({top:0,behavior:'smooth'});" class="cp-btn back-to-top-btn">Back to Top</a></div>\n"""

THEME_INIT_JS = """ <script>
			var app = document.getElementsByTagName("BODY")[0];
			var savedTheme = localStorage.lightMode || "light";
			app.setAttribute("light-mode", savedTheme);
 </script>"""

THEME_TOGGLE_JS = """ <script>
			function set_theme(theme) {
				var app = document.getElementsByTagName("BODY")[0];
				localStorage.lightMode = theme;
				app.setAttribute("light-mode", theme);
				document.querySelectorAll(".theme-btn").forEach(function(btn) {
					btn.classList.remove("active-theme");
				});
				var activeBtn = document.querySelector(".theme-btn-" + theme);
				if (activeBtn) activeBtn.classList.add("active-theme");
			}
			// Also keep old name alive in case anything calls it
			function toggle_light_mode() {
				var cur = localStorage.lightMode || "light";
				set_theme(cur === "light" ? "dark" : "light");
			}

			window.addEventListener("storage", function () {
				var t = localStorage.lightMode || "light";
				app.setAttribute("light-mode", t);
			}, false);

 </script>"""

def process_file(filepath):
    try:
        # Ignore dummy template file
        if "eng_vibhanga.html" in filepath:
            return False, "Skipped dummy file"

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        original_content = content

        # Determine which elements are needed for this page
        needs_search = True
        
        # Check if it is a Vinaya file
        if "vi/" in filepath:
            needs_search = False
        # Check if it is a helper home file
        elif "home/" in filepath:
            filename = os.path.basename(filepath)
            if filename not in ["index.html", "engsearch.html", "palisearch.html"]:
                needs_search = False

        # 1. Clean up any existing EBT UI elements to ensure we run cleanly and relocations work
        content = re.sub(r'\s*<div class="theme-btns">.*?</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'\s*<div class="theme-search-row">.*?</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div class="centered">.*?</div>\s*<!-- Centered -->', '', content, flags=re.DOTALL)

        # 2. Inject Theme Buttons and Search Row (if needed) below navbar
        navbar_match = re.search(r'(</div>\s*<!--\s*(?:End\s+)?navbar\s*-->)', content, re.IGNORECASE)
        if navbar_match:
            injection = "\n" + THEME_BUTTONS_HTML
            if needs_search:
                injection += "\n" + THEME_SEARCH_ROW_HTML
            content = content.replace(navbar_match.group(1), navbar_match.group(1) + injection)
            count1 = 1
        else:
            count1 = 0

        # 3. Update index.html links to home/index.html
        href_pattern = re.compile(r'href="(\.*/)index\.html"')
        content, count2 = href_pattern.subn(r'href="\1home/index.html"', content)

        # 4. Inject Back to Top row before footer div if not present
        if "back-to-top-btn" not in content:
            footer_div_pattern = re.compile(r'(<div class="w3-white bwcontainer2">\s*(?:<!--\s*Footer\s*div\s*-->)?)', re.IGNORECASE)
            if footer_div_pattern.search(content):
                content, count3 = footer_div_pattern.subn(BACK_TO_TOP_HTML + r'\1', content, count=1)
            else:
                count3 = 0
        else:
            count3 = 0

        # 5. Clean up old theme init block and replace with the updated one
        theme_init_cleaned = re.sub(r'<script>\s*var app = document\.getElementsByTagName\("BODY"\)\[0\];\s*var savedTheme = localStorage\.lightMode.*?</script>', '', content, flags=re.DOTALL)
        theme_init_cleaned = re.sub(r'<script>\s*var app = document\.getElementsByTagName\("BODY"\)\[0\];\s*if\s*\(localStorage\.lightMode\s*==\s*"dark"\).*?</script>', '', theme_init_cleaned, flags=re.DOTALL)
        head_close_match = re.search(r'(\s*</head>)', theme_init_cleaned, re.IGNORECASE)
        if head_close_match:
            content = theme_init_cleaned.replace(head_close_match.group(1), THEME_INIT_JS + head_close_match.group(1))
            count4 = 1
        else:
            count4 = 0

        # 6. Clean up old theme toggle block and replace with the updated one
        theme_toggle_cleaned = re.sub(r'<script>\s*function set_theme\(theme\).*?</script>', '', content, flags=re.DOTALL)
        theme_toggle_cleaned = re.sub(r'<script>\s*function toggle_light_mode\(\).*?</script>', '', theme_toggle_cleaned, flags=re.DOTALL)
        body_close_match = re.search(r'(\s*</body>)', theme_toggle_cleaned, re.IGNORECASE)
        if body_close_match:
            content = theme_toggle_cleaned.replace(body_close_match.group(1), THEME_TOGGLE_JS + body_close_match.group(1))
            count5 = 1
        else:
            count5 = 0

        # 7. Inject sutta-search.js script tag before </body> if needs_search is True
        count6 = 0
        if needs_search:
            js_path_match = re.search(r'src="(\.*/)js/footer\.js"', content)
            if js_path_match:
                rel_path = js_path_match.group(1)
            else:
                rel_path = "../"  # Fallback

            content = re.sub(r'<script\s+src=".*?js/sutta-search\.js"></script>\s*', '', content)
            search_script_tag = f' <script src="{rel_path}js/sutta-search.js"></script>\n'
            body_close_match = re.search(r'(\s*</body>)', content, re.IGNORECASE)
            if body_close_match:
                content = content.replace(body_close_match.group(1), search_script_tag + body_close_match.group(1))
                count6 = 1
        else:
            content = re.sub(r'<script\s+src=".*?js/sutta-search\.js"></script>\s*', '', content)

        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            return True, f"Success (relocated: buttons={count1}, href={count2}, btt={count3}, initjs={count4}, togglejs={count5}, script={count6})"
        else:
            return False, "No changes needed"

    except Exception as e:
        return False, f"Error: {e}"

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    os.chdir(repo_root)

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 apply_ebt_ui.py --file path/to/file.html")
        print("  python3 apply_ebt_ui.py --all")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "--file":
        if len(sys.argv) < 3:
            print("Error: Missing file path")
            sys.exit(1)
        filepath = sys.argv[2]
        success, msg = process_file(filepath)
        print(f"File {filepath}: {'[OK]' if success else '[SKIP/FAIL]'} - {msg}")

    elif mode == "--all":
        print("Applying EBT UI to all files...")
        sutta_dirs = ["an", "sn", "mn", "dn", "ud", "dhp", "snp", "tha", "thi", "kp", "vi", "home", "ebt-study", "it", "kn", "guide"]
        total_files = 0
        updated_files = 0
        skipped_files = 0
        errors = 0

        for directory in sutta_dirs:
            if not os.path.exists(directory):
                continue
            for root, _, files in os.walk(directory):
                for file in files:
                    is_html = file.endswith(".html")
                    is_root_index = (directory != "home" and file.startswith("index"))
                    
                    if is_html and not is_root_index:
                        if directory != "ebt-study" and file.endswith("comp.html"):
                            continue
                        
                        filepath = os.path.join(root, file)
                        total_files += 1
                        success, msg = process_file(filepath)
                        if success:
                            updated_files += 1
                        elif "Error" in msg:
                            print(f"Error on {filepath}: {msg}")
                            errors += 1
                        else:
                            skipped_files += 1

        print(f"\nProcessing Complete:")
        print(f"  Total Checked: {total_files}")
        print(f"  Updated:       {updated_files}")
        print(f"  Skipped:       {skipped_files}")
        print(f"  Errors:        {errors}")

if __name__ == "__main__":
    main()
