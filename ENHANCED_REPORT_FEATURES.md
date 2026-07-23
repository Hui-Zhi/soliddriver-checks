# Enhanced HTML Report Features

**Version:** 3.0.9+  
**Date:** 2026-07-21

## Overview

The enhanced HTML report provides a modern, interactive interface for reviewing KMP validation results with significantly improved usability and accessibility.

## New Features

### 1. 🎨 **Modern Visual Design**

- **Clean, card-based layout** with better spacing and hierarchy
- **System font stack** for better cross-platform rendering
- **Smooth transitions** and hover effects
- **Professional color palette** with proper contrast ratios
- **Responsive design** that works on tablets and mobile

### 2. 🌓 **Dark Mode Support**

- **Automatic detection** via `prefers-color-scheme`
- **Manual toggle** button (🌓) in toolbar
- **Persistent preference** saved to localStorage
- **Theme-aware charts** that adapt colors automatically

### 3. 🔍 **Interactive Filtering & Search**

**Search Box:**
- Type to filter by package name, vendor, or path
- Real-time filtering with debounce
- **Keyboard shortcut:** `Ctrl/Cmd + F` to focus search

**Filter Buttons:**
- **✓ PASS Only** - Show only passing packages
- **⚠ WARNING Only** - Show only packages with warnings
- **✗ ERROR Only** - Show only packages with errors
- **🔄 Reset** - Clear all filters

**Visual Feedback:**
- "Showing X of Y packages" status
- "No packages match" message when filtered to zero

### 4. 📊 **Enhanced Data Visualization**

**Stats Cards:**
- Large, easy-to-read numbers
- Color-coded by status (green/orange/red)
- Hover animations

**Dual Chart System:**
- **Pie/Doughnut Chart** - Overall distribution (PASS/WARNING/ERROR)
- **Stacked Bar Chart** - Results grouped by vendor
- Both charts update with theme changes

### 5. 📋 **Column Sorting**

- **Click any header** to sort that column
- **Visual indicators:** ↕ (sortable), ▲ (ascending), ▼ (descending)
- **Natural sorting** for numbers and text
- **Persistent sort state** while filtering

### 6. 🎯 **Individual Cell Coloring**

**Before:** Entire row colored based on worst result  
**After:** Each cell colored independently

- **Green cells** (`status-pass`) - Check passed
- **Orange cells** (`status-warning`) - Minor warning
- **Red cells** (`status-error`) - Critical error

**Benefits:**
- Easier to scan large tables
- Quickly identify which specific checks failed
- Better color-blind accessibility (combined with text)

### 7. 📖 **Expandable Error Details**

Long error messages are automatically truncated:

**Collapsed:**
```
Required symbols not found in module: PDE_DATA, ___pskb_trim, ___ratelimit...
[Show more]
```

**Expanded:**
```
[Full error message in monospace font with scrollable content]
[Show less]
```

**Features:**
- **Smart truncation** at 100 characters for WARNING/ERROR cells
- **Monospace display** for full error text
- **Scrollable** content area (max 300px height)
- **Click to toggle** expand/collapse

### 8. 📥 **Export & Share**

**Export to JSON:**
- Downloads complete results as `kmp-check-results.json`
- Includes all data plus status flags
- Programmatic access to results

**Copy Results:**
- Copies summary stats to clipboard
- Quick sharing of high-level results

**Print Support:**
- Print-optimized CSS
- Hides interactive elements
- Clean layout for paper

### 9. ⌨️ **Keyboard Navigation & Accessibility**

**Keyboard Shortcuts:**
- `Ctrl/Cmd + F` - Focus search box
- `Esc` - Reset all filters
- `Tab` / `Shift+Tab` - Navigate interactive elements

**Accessibility Features:**
- Proper ARIA labels on inputs
- Focus indicators on all interactive elements
- Semantic HTML structure
- Screen reader friendly
- Sufficient color contrast (WCAG AA)

### 10. 🎨 **Better Typography**

**Monospace Paths:**
- File paths use monospace font
- Better readability for long paths
- Word-break handling

**Font Stack:**
```css
--font-main: -apple-system, BlinkMacSystemFont, 'Segoe UI', ...
--font-mono: 'SF Mono', Monaco, 'Cascadia Code', ...
```

**Improved Hierarchy:**
- Larger headers with better spacing
- Proper line-height for readability
- Consistent padding in all tables

### 11. 🔧 **Sticky Table Headers**

- Headers stay visible when scrolling long tables
- Always see column names
- Better orientation in large datasets

### 12. 📱 **Responsive Layout**

- **Desktop:** Dual-column chart layout
- **Tablet/Mobile:** Single-column stacked layout
- Flexible grid system
- Touch-friendly button sizes

## Technical Improvements

### CSS Variables for Theming

```css
:root {
  --primary-green: #30BA78;
  --pass-green: #4CAF50;
  --warning-orange: #FF9E02;
  --error-red: #C5161F;
  --bg-light: #FAFAFA;
  --text-primary: #212121;
  /* ... */
}
```

### Python Changes

**File:** `src/soliddriver_checks/cli/kmp_report.py`

**Changes:**
1. Individual cell CSS classes (`status-pass`, `status-warning`, `status-error`)
2. Sortable headers (`sortable` class)
3. Monospace font for paths (`mono` class)
4. Expandable content for long messages
5. Enhanced template: `kmp-report-enhanced.html.jinja`

### JavaScript Features

- **Search debouncing** (300ms delay)
- **LocalStorage** for theme persistence
- **Dynamic chart updates** on theme change
- **Smart filtering** with compound conditions
- **Table sorting** with natural comparison

## Browser Compatibility

- **Modern browsers** (Chrome, Firefox, Safari, Edge)
- **ES6+ JavaScript** (no transpilation)
- **CSS Grid & Flexbox** layouts
- **CSS Variables** for theming

**Minimum versions:**
- Chrome 88+
- Firefox 78+
- Safari 14+
- Edge 88+

## Performance

- **Lazy loading** of expandable content
- **Debounced search** to avoid excessive DOM updates
- **CSS transitions** for smooth animations
- **Efficient event delegation** for row clicks

## Migration Guide

### For Developers

**To enable enhanced reports:**

1. Use the new template:
   ```python
   kmp_tmpl = env.get_template("kmp-report-enhanced.html.jinja")
   ```

2. Update cell creation with status classes:
   ```python
   cell.set_attribute("class", "status-pass")  # or status-warning, status-error
   ```

3. Add sortable class to headers:
   ```python
   th("Name").set_attribute("class", "sortable")
   ```

### For Users

**No changes required!** The enhanced report is automatically generated when using:

```bash
soliddriver-checks /path/to/rpms -f html -o report.html
```

## Future Enhancements

Possible future additions:

1. **Column visibility toggle** - Show/hide specific columns
2. **Results comparison** - Compare two report files
3. **Permalink support** - Share URLs with filter state
4. **CSV export** - Download as spreadsheet
5. **Advanced filters** - Filter by multiple criteria
6. **Saved filter presets** - Quick filter templates
7. **Chart download** - Export charts as PNG
8. **Timeline view** - Compare results over time

## Feedback

For issues or feature requests:
- GitHub: https://github.com/SUSE/soliddriver-checks/issues
- Tag reports with: `enhancement`, `report-ui`

---

**Generated with ✨ by soliddriver-checks enhanced reporting**
