# Flowline Design System Specification

## 1. Visual Identity & Design Principles
- **Aesthetic**: Calm, precise, trustworthy, modern financial workspace.
- **Density**: High information density for ledger/tabular views, balanced with spacious visual breathing room on dashboard overviews.
- **Depth & Separation**: Subtle borders (`divider`) as primary boundary separation; minimal elevation shadows.
- **Motion**: Subtle, functional transitions (120ms - 200ms) for drawer collapsibility, modals, and toasts. No distracting flourishes.

---

## 2. Color System Tokens

### Dark Theme (Default)
| Token Name | Hex Code | Purpose |
|------------|----------|---------|
| `appBackground` | `#17251F` | Deep forest tone for primary application canvas |
| `sidebarBackground` | `#1D2C23` | Anchored navigation drawer surface |
| `primarySurface` | `#26382F` | Main card and panel background |
| `elevatedSurface` | `#30473A` | Modals, floating dropdowns, highlighted rows |
| `primaryText` | `#F5F6F2` | High-contrast body, titles, financial figures |
| `secondaryText` | `#B8C6BC` | Subtitles, labels, timestamps, metadata |
| `primaryAccent` | `#B8F28B` | Mint green key interactive callouts & primary buttons |
| `accentHover` | `#C9F8A6` | Active hover state on primary interactive elements |
| `divider` | `#34483C` | Subtle surface borders and table row lines |
| `positive` | `#B8F28B` | Inflow, savings achievements, surplus cash flow |
| `negative` | `#FFB4A9` | Outflows, debt liabilities, budget overruns |
| `informational` | `#82C9D4` | Soft cyan for transfers, notes, status badges |
| `warning` | `#E9BE76` | Warm amber for approaching budget limits (75-90%) |

### Light Theme
| Token Name | Hex Code | Purpose |
|------------|----------|---------|
| `appBackground` | `#F5F6F2` | Crisp parchment base canvas |
| `sidebarBackground` | `#EDF1EA` | Soft contrasting navigation drawer |
| `primarySurface` | `#FFFFFF` | Pure white cards and panels |
| `elevatedSurface` | `#FFFFFF` | Elevated popups with subtle borders |
| `primaryText` | `#17251F` | Deep charcoal for readability |
| `secondaryText` | `#536258` | Muted sage for secondary text |
| `primaryAccent` | `#426D35` | Forest green primary brand accent |
| `accentHover` | `#34572A` | Hover state for accent buttons |
| `divider` | `#DCE4DA` | Light hairline borders |
| `positive` | `#286B43` | Dark green for income / inflows |
| `negative` | `#B54136` | Terracotta red for expenses / debt |
| `informational` | `#246C82` | Deep teal for info badges |
| `warning` | `#855A12` | Dark gold for warning thresholds |

---

## 3. Typography
- **Primary Typeface**: Inter, Segoe UI, Roboto, system sans-serif fallback.
- **Type Scale**:
  - `Display`: 32px (SemiBold) - Big figures / net worth headline
  - `PageTitle`: 26px (SemiBold) - Page headers
  - `SectionHeading`: 18px (Medium) - Card section titles
  - `CardHeading`: 15px (Medium) - Metric labels
  - `Body`: 14px (Regular) - Standard inputs, grid content
  - `SecondaryText`: 12px (Regular) - Helper text, timestamps, tags
  - `FinancialFigure`: 24px-32px (SemiBold, Tabular Numerals)
- **Tabular Figures**: Monetary numbers must enable monospace numeral alignment (`font.features: { "tnum": 1 }` or fixed-pitch rendering).

---

## 4. Spacing & Shape Geometry
- **Base Unit**: 4px
- **Scale**: 4px, 8px, 12px, 16px, 20px, 24px, 32px, 40px, 48px
- **Border Radii**:
  - Cards & Panels: 12px
  - Inputs & Dropdowns: 8px
  - Badges & Avatars: 6px
  - Buttons: 8px

---

## 5. Standard Component Specs
1. **PrimaryButton**: Solid accent fill, dark text in dark mode / white text in light mode, 40px height, 8px radius, focus outline.
2. **SecondaryButton**: Outlined with `divider`, transparent background, changes to `elevatedSurface` on hover.
3. **DestructiveButton**: Muted negative tint on hover, warning confirmation on click.
4. **CurrencyInput**: Leading ₹ prefix, thousands formatting, prevents invalid characters.
5. **StatusBadge**: Pill badge with semi-transparent background tint corresponding to state (`positive`, `negative`, `warning`, `informational`).
6. **DataTable**: Alternating subtle row backgrounds, fixed header, right-aligned monetary values, responsive column sizing.
