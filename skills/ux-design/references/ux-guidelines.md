# UX Guidelines Checklist

119 concrete UI/UX rules, grouped by category, each with a do / don't and a severity. The
`ux-design` skill uses this as its audit list.

Ported from the `ux-guidelines.csv` in
[nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill),
under the MIT License reproduced in [Upstream license](#upstream-license).

**Reading it:** severity Critical or High = fix before shipping; Medium = fix in the same pass if
touched; Low = taste. Platform column: Web / Mobile / All.

## Contents

- [Navigation](#navigation)
- [Animation](#animation)
- [Layout](#layout)
- [Touch](#touch)
- [Interaction](#interaction)
- [Accessibility](#accessibility)
- [Performance](#performance)
- [Forms](#forms)
- [Responsive](#responsive)
- [Typography](#typography)
- [Feedback](#feedback)
- [Content](#content)
- [Onboarding](#onboarding)
- [Search](#search)
- [Data Entry](#data-entry)
- [AI Interaction](#ai-interaction)
- [Spatial UI](#spatial-ui)
- [Sustainability](#sustainability)
- [Security / Accessibility](#security--accessibility)
- [Forms / Accessibility](#forms--accessibility)
- [Upstream license](#upstream-license)

## Navigation

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 1 | **Smooth Scroll** — Anchor links should scroll smoothly to target section | Web | Use scroll-behavior: smooth on html element | Jump directly without transition | High |
| 2 | **Sticky Navigation** — Fixed nav should not obscure content | Web | Add padding-top to body equal to nav height | Let nav overlap first section content | Medium |
| 3 | **Active State** — Current page/section should be visually indicated | All | Highlight active nav item with color/underline | No visual feedback on current location | Medium |
| 4 | **Back Button** — Users expect back to work predictably | Mobile | Preserve navigation history properly | Break browser/app back button behavior | High |
| 5 | **Deep Linking** — URLs should reflect current state for sharing | All | Update URL on state/view changes | Static URLs for dynamic content | Medium |
| 6 | **Breadcrumbs** — Show user location in site hierarchy | Web | Use for sites with 3+ levels of depth | Use for flat single-level sites | Low |

## Animation

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 7 | **Excessive Motion** — Too many animations cause distraction and motion sickness | All | Animate 1-2 key elements per view maximum | Animate everything that moves | High |
| 8 | **Duration Timing** — Motion duration depends on distance complexity platform and user context | All | Use shared motion tokens and test that feedback stays responsive | Present 150-300ms or any cutoff as a universal requirement | Medium |
| 9 | **Reduced Motion** — Respect user's motion preferences | All | Check prefers-reduced-motion media query | Ignore accessibility motion settings | High |
| 10 | **Loading States** — Show feedback during async operations | All | Use skeleton screens or spinners | Leave UI frozen with no feedback | High |
| 11 | **Hover vs Tap** — Hover effects don't work on touch devices | All | Use click/tap for primary interactions | Rely only on hover for important actions | High |
| 12 | **Continuous Animation** — Infinite animations are distracting | All | Use for loading indicators only | Use for decorative elements | Medium |
| 13 | **Transform Performance** — Some CSS properties trigger expensive repaints | Web | Use transform and opacity for animations | Animate width/height/top/left properties | Medium |
| 14 | **Easing Functions** — Easing should match how an element changes speed and purpose | All | Use deceleration when arriving acceleration when leaving and linear for constant-rate progress | Reject linear easing even for steady rotation or progress | Low |
| 108 | **Auto-Rotating Content Controls** — Auto-rotating content needs user control | All | Provide previous next and play/pause; stop on focus or hover and when reduced motion is requested | Auto-advance slides without a stop control | High |
| 119 | **Cancellable State Transitions** — Rapid compact-control changes can interrupt an in-flight transition | Web | Cancel or replace prior motion; set the final semantic state directly and handle cancellation cleanup | Depend on animationend or transitionend for required state correctness | High |

## Layout

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 15 | **Z-Index Management** — Stacking context conflicts cause hidden elements | Web | Define z-index scale system (10 20 30 50) | Use arbitrary large z-index values | High |
| 16 | **Overflow Hidden** — Hidden overflow can clip important content | Web | Test all content fits within containers | Blindly apply overflow-hidden | Medium |
| 17 | **Fixed Positioning** — Fixed elements can overlap or be inaccessible | Web | Account for safe areas and other fixed elements | Stack multiple fixed elements carelessly | Medium |
| 18 | **Stacking Context** — New stacking contexts reset z-index | Web | Understand what creates new stacking context | Expect z-index to work across contexts | Medium |
| 19 | **Content Jumping** — Images badges validation text and skeleton replacements can shift nearby content when they update | Web | Reserve appropriate space or keep async states in a stable content-driven container | Insert compact text or media without a layout strategy | High |
| 20 | **Viewport Units** — 100vh can be problematic on mobile browsers | Web | Use dvh or account for mobile browser chrome | Use 100vh for full-screen mobile layouts | Medium |
| 21 | **Container Width** — Content too wide is hard to read | Web | Limit max-width for text content (65-75ch) | Let text span full viewport width | Medium |
| 111 | **Long Token Wrapping** — URLs identifiers and user content must not force horizontal overflow | Web | Use overflow-wrap anywhere and let flex or grid text children shrink | Apply word-break break-all to all prose | High |
| 115 | **Chip Collection Reflow** — Filter chips and editable value collections must preserve labels when space or text size changes | All | Wrap the collection or use an operable +n disclosure for hidden overflow values | Force all chips into one clipped row or hide overflow values | High |

## Touch

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 22 | **Touch Target Size** — Touch target guidance depends on platform and web context | Mobile | Use 44pt on iOS and 48dp on Android; for web use the separate WCAG Target Size rule | Treat one unit or minimum as universal across platforms | High |
| 23 | **Touch Spacing** — Adjacent touch targets need adequate spacing | Mobile | Minimum 8px gap between touch targets | Tightly packed clickable elements | Medium |
| 24 | **Gesture Conflicts** — Custom gestures can conflict with system | Mobile | Avoid horizontal swipe on main content | Override system gestures | Medium |
| 25 | **Tap Delay** — 300ms tap delay feels laggy | Mobile | Use touch-action CSS or fastclick | Default mobile tap handling | Medium |
| 26 | **Pull to Refresh** — Accidental refresh is frustrating | Mobile | Disable where not needed | Enable by default everywhere | Low |
| 27 | **Haptic Feedback** — Tactile feedback improves interaction feel | Mobile | Use for confirmations and important actions | Overuse vibration feedback | Low |

## Interaction

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 28 | **Focus States** — Keyboard focus, including controls inside a modal, needs a visible indicator | All | Use a visible focus ring on every interactive control, including modal controls | Remove focus outline without replacement | High |
| 29 | **Hover States** — Visual feedback on interactive elements | Web | Change cursor and add subtle visual change | No hover feedback on clickable elements | Medium |
| 30 | **Active States** — Show immediate feedback on press/click | All | Add pressed/active state visual change | No feedback during interaction | Medium |
| 31 | **Disabled States** — Clearly indicate non-interactive elements | All | Reduce opacity and change cursor | Confuse disabled with normal state | Medium |
| 32 | **Loading Buttons** — Prevent double submission during async actions | All | Disable button and show loading state | Allow multiple clicks during processing | High |
| 33 | **Error Feedback** — Users need to know when something fails | All | Show clear error messages near problem | Silent failures with no feedback | High |
| 34 | **Success Feedback** — Confirm successful actions to users | All | Show success message or visual change | No confirmation of completed action | Medium |
| 35 | **Confirmation Dialogs** — Prevent accidental destructive actions | All | Confirm before delete/irreversible actions | Delete without confirmation | High |

## Accessibility

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 36 | **Color Contrast** — Text must be readable against background | All | Minimum 4.5:1 ratio for normal text | Low contrast text | High |
| 37 | **Color Only** — Don't convey information by color alone | All | Use icons/text in addition to color | Red/green only for error/success | High |
| 38 | **Alt Text** — Images need text alternatives | All | Descriptive alt text for meaningful images | Empty or missing alt attributes | High |
| 39 | **Heading Hierarchy** — Screen readers use headings for navigation | Web | Use sequential heading levels h1-h6 | Skip heading levels or misuse for styling | Medium |
| 40 | **ARIA Labels** — Interactive elements need accessible names | All | Add aria-label for icon-only buttons | Icon buttons without labels | High |
| 41 | **Keyboard Navigation** — Web users need complete keyboard navigation with visible focus on every operable control | Web | Keep tab order aligned with visual order and test every action without a pointer | Keyboard traps or illogical tab order | High |
| 42 | **Screen Reader** — Content should make sense when read aloud | All | Use semantic HTML and ARIA properly | Div soup with no semantics | Medium |
| 43 | **Form Labels** — Inputs must have associated labels | All | Use label with for attribute or wrap input | Placeholder-only inputs | High |
| 44 | **Error Messages** — Error messages must be announced | All | Use aria-live or role=alert for errors | Visual-only error indication | High |
| 45 | **Skip Links** — Allow keyboard users to skip navigation | Web | Provide skip to main content link | No skip link on nav-heavy pages | Medium |
| 99 | **Motion Sensitivity** — Parallax/Scroll-jacking causes nausea | All | Honor prefers-reduced-motion and present the final readable state without parallax or scroll-jacking | Force scroll effects | High |
| 100 | **Focus Not Obscured (Minimum)** — WCAG 2.2 AA requires keyboard focus to remain at least partially visible | Web | Offset sticky UI with scroll-padding and dismiss or move persistent overlays | Let headers footers banners or chat widgets fully cover focus | High |
| 101 | **Focus Not Obscured (Enhanced)** — WCAG 2.2 AAA requires keyboard focus to remain fully visible | Web | Keep the entire focused component unobscured by author-created content | Present this enhanced AAA criterion as an AA requirement or allow persistent UI to hide any part of focus | Medium |
| 102 | **Focus Appearance** — WCAG 2.2 AAA defines minimum area and contrast for focus indicators | Web | Use an indicator at least as large as a 2 CSS px perimeter with 3:1 state contrast | Present this enhanced AAA criterion as an AA requirement or use a thin low-contrast outline | Medium |
| 103 | **Dragging Movements** — WCAG 2.2 AA requires a single-pointer alternative for author-controlled drag operations | All | Add buttons menus or tap-to-move controls and retain keyboard operation | Make dragging the only way to reorder resize or select | High |
| 104 | **Target Size (Minimum)** — WCAG 2.2 AA requires 24 CSS px pointer targets or an applicable exception | Web | Use at least 24 by 24 CSS px or verify spacing equivalent inline user-agent or essential exceptions | Assume native 44pt or 48dp guidance defines web conformance | High |
| 105 | **Consistent Help** — WCAG 2.2 A requires repeated help mechanisms to stay in the same relative order | All | Keep contact self-help and automated help in consistent locations | Move help controls to different locations on each page | Medium |
| 112 | **Text Reflow and Spacing** — Text must remain available at narrow widths zoom and user spacing overrides | Web | Use fluid sizes content-driven height and unitless line height | Clip text in fixed-width or fixed-height boxes | Critical |
| 117 | **Compact Control Semantics** — Interactive chips need a native role accessible name state keyboard operation and visible focus | Web | Prefer a button and expose pressed or selected state that matches the visible label | Use a clickable div or reveal the only action on hover | Critical |
| 118 | **Contextual Live Badge Updates** — Async badge and count changes should announce a meaningful contextual status without moving focus | Web | Use one appropriate atomic status message such as 3 items in cart | Announce a bare number or make every badge a competing live region | High |

## Performance

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 46 | **Image Optimization** — Large images slow page load | All | Use appropriate size and format (WebP) | Unoptimized full-size images | High |
| 47 | **Lazy Loading** — Load content as needed | All | Lazy load below-fold images and content | Load everything upfront | Medium |
| 48 | **Code Splitting** — Large bundles slow initial load | Web | Split code by route/feature | Single large bundle | Medium |
| 49 | **Caching** — Repeat visits should be fast | Web | Set appropriate cache headers | No caching strategy | Medium |
| 50 | **Font Loading** — Web fonts can block rendering | Web | Use font-display swap or optional | Invisible text during font load | Medium |
| 51 | **Third Party Scripts** — External scripts can block rendering | Web | Load non-critical scripts async/defer | Synchronous third-party scripts | Medium |
| 52 | **Bundle Size** — Large JavaScript slows interaction | Web | Monitor and minimize bundle size | Ignore bundle size growth | Medium |
| 53 | **Render Blocking** — CSS/JS can block first paint | Web | Inline critical CSS defer non-critical | Large blocking CSS files | Medium |

## Forms

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 54 | **Input Labels** — Every input needs a visible label | All | Always show label above or beside input | Placeholder as only label | High |
| 55 | **Error Placement** — Each invalid field needs an inline error connected to that field | All | Show a specific error below the input and reference it with aria-describedby | Show only a top-level error without identifying each invalid field | High |
| 56 | **Inline Validation** — Validate as user types or on blur | All | Validate on blur for most fields | Validate only on submit | Medium |
| 57 | **Input Types** — Use appropriate input types | All | Use email tel number url etc | Text input for everything | Medium |
| 58 | **Autofill Support** — Help browsers autofill correctly | Web | Use autocomplete attribute properly | Block or ignore autofill | Medium |
| 59 | **Required Indicators** — Mark required fields clearly | All | Use asterisk or (required) text | No indication of required fields | Medium |
| 60 | **Password Visibility** — Let users see password while typing | All | Toggle to show/hide password | No visibility toggle | Medium |
| 61 | **Submit Feedback** — Confirm form submission status | All | Show loading then success/error state | No feedback after submit | High |
| 62 | **Input Affordance** — Inputs should look interactive | All | Use distinct input styling | Inputs that look like plain text | Medium |
| 63 | **Mobile Keyboards** — Show appropriate keyboard for input type | Mobile | Use inputmode attribute | Default keyboard for all inputs | Medium |
| 106 | **Redundant Entry** — WCAG 2.2 A avoids requiring the same information twice in one process | All | Auto-populate prior values or let users select previously entered information | Ask users to retype the same address or account data without necessity | Medium |

## Responsive

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 64 | **Mobile First** — Design for mobile then enhance for larger | Web | Start with mobile styles then add breakpoints | Desktop-first causing mobile issues | Medium |
| 65 | **Breakpoint Testing** — Test at all common screen sizes | Web | Test at 320 375 414 768 1024 1440 | Only test on your device | Medium |
| 66 | **Touch Friendly** — Mobile layouts need touch-sized targets | Web | Increase touch targets on mobile | Same tiny buttons on mobile | High |
| 67 | **Readable Font Size** — Text must be readable on all devices | All | Minimum 16px body text on mobile | Tiny text on mobile | High |
| 68 | **Viewport Meta** — Set viewport for mobile devices | Web | Use width=device-width initial-scale=1 | Missing or incorrect viewport | High |
| 69 | **Horizontal Scroll** — Avoid horizontal scrolling | Web | Ensure content fits viewport width | Content wider than viewport | High |
| 70 | **Image Scaling** — Images should scale with container | Web | Use max-width: 100% on images | Fixed width images overflow | Medium |
| 71 | **Table Handling** — Tables can overflow on mobile | Web | Use horizontal scroll or card layout | Wide tables breaking layout | Medium |

## Typography

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 72 | **Line Height** — Adequate line height improves readability | All | Use 1.5-1.75 for body text | Cramped or excessive line height | Medium |
| 73 | **Line Length** — Long lines are hard to read | Web | Limit to 65-75 characters per line | Full-width text on large screens | Medium |
| 74 | **Font Size Scale** — Consistent type hierarchy aids scanning | All | Use consistent modular scale | Random font sizes | Medium |
| 75 | **Font Loading** — Fonts should load without layout shift | Web | Reserve space with fallback font | Layout shift when fonts load | Medium |
| 76 | **Contrast Readability** — Body text needs good contrast | All | Use darker text on light backgrounds | Gray text on gray background | High |
| 77 | **Heading Clarity** — Headings should stand out from body | All | Clear size/weight difference | Headings similar to body text | Medium |
| 110 | **Heading Line Balance** — Short multi-line headings may use balanced wrapping as a progressive visual heuristic | Web | Bound the measure and test natural-wrap fallback across widths fonts and locales | Promise an exact final line or insert blanket nonbreaking spaces or hardcoded br tags | Medium |

## Feedback

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 78 | **Loading Indicators** — Loading feedback should match the expected wait and avoid flashing for near-instant work | All | Follow platform and component guidance; preserve layout focus and accessible busy status | Apply one timing threshold to every operation or leave long waits unexplained | High |
| 79 | **Empty States** — Guide users when no content exists | All | Show helpful message and action | Blank empty screens | Medium |
| 80 | **Error Recovery** — Help users recover from errors | All | Provide clear next steps | Error without recovery path | Medium |
| 81 | **Progress Indicators** — Show progress for multi-step processes | All | Step indicators or progress bar | No indication of progress | Medium |
| 82 | **Toast Notifications** — Transient messages for non-critical info | All | Auto-dismiss after 3-5 seconds | Toasts that never disappear | Medium |
| 83 | **Confirmation Messages** — Confirm successful actions | All | Brief success message | Silent success | Medium |

## Content

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 84 | **Truncation** — Handle long content gracefully | All | Truncate with ellipsis and expand option | Overflow or broken layout | Medium |
| 85 | **Date Formatting** — Use locale-appropriate date formats | All | Use relative or locale-aware dates | Ambiguous date formats | Low |
| 86 | **Number Formatting** — Format large numbers for readability | All | Use thousand separators or abbreviations | Long unformatted numbers | Low |
| 87 | **Placeholder Content** — Show realistic placeholders during dev | All | Use realistic sample data | Lorem ipsum everywhere | Low |
| 113 | **Essential Text Truncation** — Headings actions errors safety text and distinguishing names need complete access | All | Wrap stack resize or provide a visible full-detail path | Clamp essential meaning only to make cards uniform | Critical |
| 114 | **Compact Label Semantics** — Badges communicate state while chips or tags represent values or actions | All | Choose static or interactive markup from the label's meaning and ownership | Make every pill clickable or encode status with color alone | High |
| 116 | **Compact Label Overflow** — A badge chip or pill label should stay whole on one line when practical and disclose unavoidable truncation | All | Bound only unpredictable values; use nowrap with a shrinkable label; expose full text to keyboard pointer and touch users | Let one compact label wrap to a second line or use a hover-only tooltip | High |

## Onboarding

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 88 | **User Freedom** — Users should be able to skip tutorials | All | Provide Skip and Back buttons | Force linear unskippable tour | Medium |

## Search

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 89 | **Autocomplete** — Help users find results faster | Web | Show predictions as user types | Require full type and enter | Medium |
| 90 | **No Results** — Dead ends frustrate users | Web | Show 'No results' with suggestions | Blank screen or '0 results' | Medium |

## Data Entry

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 91 | **Bulk Actions** — Editing one by one is tedious | Web | Allow multi-select and bulk edit | Single row actions only | Low |

## AI Interaction

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 92 | **Disclaimer** — Users need to know they talk to AI | All | Clearly label AI generated content | Present AI as human | High |
| 93 | **Streaming** — Waiting for full text is slow | All | Stream text response token by token | Show loading spinner for 10s+ | Medium |
| 98 | **Feedback Loop** — AI needs user feedback to improve | All | Thumps up/down or 'Regenerate' | Static output only | Low |

## Spatial UI

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 94 | **Gaze Hover** — Elements should respond to eye tracking before pinch | VisionOS | Scale/highlight element on look | Static element until pinch | High |
| 95 | **Depth Layering** — UI needs Z-depth to separate content from environment | VisionOS | Use glass material and z-offset | Flat opaque panels blocking view | Medium |

## Sustainability

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 96 | **Auto-Play Video** — Autoplaying media consumes data and creates motion barriers | Web | Prefer click-to-play; provide pause and captions; stop off-screen and honor reduced motion | Auto-play high-resolution loops without pause or captions | Medium |
| 97 | **Asset Weight** — Heavy 3D/Image assets increase carbon footprint | Web | Compress and lazy load 3D models | Load 50MB textures | Medium |

## Security / Accessibility

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 107 | **Accessible Authentication (Minimum)** — WCAG 2.2 AA says authentication must not depend only on a cognitive function test unless an exception applies | All | Allow password managers and paste; offer passkeys OAuth or another non-cognitive method | Block paste or require manual OTP transcription with no alternative | Critical |

## Forms / Accessibility

| # | Rule | Platform | Do | Don't | Sev |
|---|---|---|---|---|---|
| 109 | **Focusable Error Summary** — An error summary for failed validation complements inline field errors and must be easy to find by keyboard and screen reader users | Web | Place it at the top of the form; move focus to its heading or container after failed submit; link each item to its invalid field; retain inline errors | Replace inline errors with a visual-only summary or move focus on every blur | High |

## Upstream license

```text
MIT License

Copyright (c) 2024 Next Level Builder

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
