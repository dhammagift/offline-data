# Plan: Relocate Random and Pāḷi Buttons to Theme Row Right Corner

## Architecture Decisions
- **Dynamic Relocation via central JS/CSS**: We will use jQuery inside `js/controlpanel.js` to wrap the theme buttons and relocate the control panel buttons into `.theme-btns` on DOM load. We will style the layout using scoped CSS in `css/css.css` under the `.theme-btns.theme-btns-relocated` selector.
- **Rationale**:
  - Avoids rewriting thousands of static HTML files, preserving clean git histories and minimizing merge conflicts with upstream.
  - Ensures robust alignment of buttons regardless of layout differences across different screen sizes.
  - Perfectly aligns with the project's offline client-side architecture since JS/jQuery is already mandatory for themes and Pāḷi dictionary lookups.
- **Phases**: Split into Phase 1 (Single test page verification) and Phase 2 (Global rollout to all pages) to allow manual inspection before wide application.

---

## Phase 1: Test Page Implementation (Single Page)

### Task 1: Update Central Javascript for Conditional Relocation
- [x] Add DOM manipulation logic in `js/controlpanel.js` to:
  - Check if the current page is the test page `dn1.html`.
  - Wrap existing theme buttons in `.theme-switch-group`.
  - Wrap `#randomSutta` and `#pali` in `.control-group`.
  - Append `.control-group` to `.theme-btns` and add class `.theme-btns-relocated` to it.
  - Remove the empty `#controlpanel` wrapper.
  → verify: Open `dn/dn1.html` in browser, verify in developer tools that the DOM has been restructured with `.theme-switch-group` and `.control-group` inside `.theme-btns-relocated`.

### Task 2: Implement Scoped CSS for the New Layout
- [x] Add styling rules for `.theme-btns.theme-btns-relocated` in `css/css.css`:
  - **Desktop (>908px)**: Flex row with `justify-content: space-between` and `padding-right: 25px`.
  - **Mobile (<=908px)**: Flex column with `align-items: center` and a `gap: 8px` between groups.
  - **Button alignment**: Adjust `.control-group .cp-btn` to match `.theme-btn` height (`1.8em`), font-size (`80%`), and transition states, while retaining brown colors.
  → verify: Check the CSS styling of `#randomSutta` and `#pali` on `dn/dn1.html` in developer tools; confirm they inherit `height: 1.8em` and align horizontally with theme buttons on desktop.

### Task 3: Perform Single-Page Verification
- [x] Verify the layout and functionality on `dn/dn1.html`:
  - Desktop view: Confirm theme buttons are on the left, Random/Pāḷi on the right corner.
  - Mobile view: Confirm theme buttons and Random/Pāḷi buttons are centered on two separate lines.
  - Scroll behavior: Verify all buttons scroll out of view when scrolling down.
  - Functionality: Confirm Pāḷi toggle and Random redirect work correctly.
  - Other pages: Confirm other pages (e.g., `dn/dn2.html`) still show standard floating buttons.
  → verify: Manually verify all checks, record screenshots/results, and ask user for approval.

---

## Phase 2: Global Rollout (All Pages)

### Task 4: Rollout Relocation Region-Wide
- [x] Remove the conditional `dn1.html` restriction in `js/controlpanel.js` so that the relocation code executes on every page.
  → verify: Inspect `js/controlpanel.js` and verify no `dn1.html` path-matching conditional remains.

### Task 5: Verify Multi-Page Layouts
- [x] Perform smoke tests across multiple sutta categories:
  - Verify layout on `dn/dn2.html`
  - Verify layout on `mn/mn1.html`
  - Verify layout on `an/an1.html`
  - Verify layout on `sn/sn1.1.html`
  → verify: Check both desktop and mobile views on these pages; confirm correct alignment, functionality, and scroll behavior on all of them.

### Task 6: Documentation and Guideline Update
- [x] Update the synchronization guidelines (`kamma/sync/guideline.md`) to document these changes in `js/controlpanel.js` and `css/css.css`.
  → verify: Run `git diff kamma/sync/guideline.md` to confirm the updates are written.
