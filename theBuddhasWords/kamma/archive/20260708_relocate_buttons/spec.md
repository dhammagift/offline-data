# Spec: Relocate Random and Pāḷi Buttons to Theme Row with Distinct Separation

## Overview
Currently, the "Random" and "Pāḷi" buttons are rendered inside a fixed-position control panel (`#controlpanel`) that follows the user when scrolling. The user wants these buttons to stay at the top right of the page structure (scrolling naturally with the header) on the same horizontal level as the existing theme switch buttons, but positioned in the far right corner on desktop. On mobile, there must be a clear and distinct separation between the theme switcher buttons and the Random/Pāḷi buttons.

To ensure safety and ease of testing, we will first apply this change to a single test page (`dn/dn1.html`). Once manually verified, we will roll it out everywhere.

## What it should do
1. **Dynamic Grouping and Relocation**:
   On the test page (`dn/dn1.html`), when the DOM is ready:
   - Wrap the existing theme switcher buttons in a dedicated `<div class="theme-switch-group">`.
   - Wrap the "Random" and "Pāḷi" buttons in a dedicated `<div class="control-group">`.
   - Move the `.control-group` into the `.theme-btns` container.
   - Add the class `.theme-btns-relocated` to the main `.theme-btns` container.
   - Remove the empty `#controlpanel` wrapper.

2. **Desktop Layout (Screens > 908px)**:
   - The `.theme-btns-relocated` container will align its two groups on the same horizontal level.
   - The `.theme-switch-group` will remain left-aligned.
   - The `.control-group` containing "Random" and "Pāḷi" will align to the far right corner of the page.
   - The rightmost button ("Pāḷi") should align with the right margin of the layout (approx. 25px from the edge).

3. **Mobile Layout (Screens <= 908px)**:
   - The `.theme-btns-relocated` container will stack the two groups vertically (`flex-direction: column`) to ensure clear separation.
   - The `.theme-switch-group` will be centered horizontally.
   - The `.control-group` will be centered horizontally below the theme group, separated by a vertical gap (approx. 8px).

4. **Scroll Behavior**: All buttons must scroll out of view naturally with the page header.

5. **Button Styling**: Relocated buttons inside `.control-group` will be styled to match the vertical height (`1.8em`), font-size (`80%`), and paddings of the theme switcher buttons, while retaining their distinctive brown color scheme, hover states, and active state transitions.

6. **Isolation**: All other pages must remain unchanged during this initial test phase.

## Assumptions & Uncertainties
- **Dynamic Relocation**: We assume relocating the elements dynamically via central JavaScript (`js/controlpanel.js`) and central CSS (`css/css.css`) is the preferred approach, as it keeps the codebase clean, avoids static changes in thousands of HTML files, and preserves compatibility with upstream merges.
- **Path Detection**: We assume the test page can be identified by checking if the URL ends with `dn1.html`.

## Constraints
- **No Direct Sutta HTML Edits**: Never edit `dn/dn1.html` or other sutta pages directly (Golden Rule). We will achieve the test-phase relocation using centralized Javascript (`js/controlpanel.js`) and CSS (`css/css.css`).
- **Preserve Functionality**: Do not break the event handlers for Pāḷi translation toggle and Random redirection.

## How we'll know it's done
- Open `dn/dn1.html` on a desktop browser: "Random" and "Pāḷi" buttons are at the far right corner, inline horizontally with the theme switcher.
- Open `dn/dn1.html` on a mobile browser: Theme buttons are centered on one row, and Random/Pāḷi buttons are centered on a separate row below it, clearly separated.
- Scrolling down `dn/dn1.html` makes all buttons scroll out of view.
- Clicking "Pāḷi" on `dn/dn1.html` toggles Pāḷi translation column visibility.
- Clicking "Random" on `dn/dn1.html` redirects to a random sutta.
- Opening any other sutta page (e.g., `dn/dn2.html`) still shows the standard floating buttons.

## What's not included
- Modifying pages that do not include the control panel or theme buttons.
- Changing the layout of the quick search input row.
