### 6. MULTILINGUAL AND ACCESSIBILITY IMPLEMENTATION
To serve diverse populations effectively, the system is built with internationalization (i18n) and accessibility as foundational requirements, not afterthoughts.

6.1 Real-Time Bilingual Switching
The application includes a persistent language toggle (English / Hindi). When activated, the system dynamically swaps the text content of the UI, form questions, and response options by referencing the dictionary under `data/core/`. Crucially, this re-rendering occurs without a page reload, preserving the patient's existing responses and current position in the assessment. Clinical Hindi translations utilize standardized, respectful psychiatric terminology to avoid colloquial or stigmatizing phrasing.

6.2 WCAG 2.1 AA Compliance
- Keyboard Navigation: All form elements, including complex matrix radio buttons, are fully operable via keyboard (Tab, Space, Enter).
- Screen Reader Compatibility: ARIA labels and roles (radiogroup, alertdialog, aria-live regions) are applied to all form inputs, ensuring screen readers accurately announce question text and response options.
- Visual Contrast: The UI adheres to strict color contrast ratios, and a high-contrast mode is available for visually impaired users.

---

