import { L, t } from './i18n.js';
import { state, CLINICAL_DATA, choicesForDomain, defaultChoicesForDomain, selectedDomainForms } from './state.js';
import { DOMAIN_GROUPS } from './domain-groups.js';

function renderDomainGrid() {
    const list = document.getElementById('domain-list');
    if (!CLINICAL_DATA || !list) return;

    const query = (document.getElementById('domain-search')?.value || '').trim().toLocaleLowerCase();
    const domains = CLINICAL_DATA.domains.map(domain => {
        const topic = t('topic.' + domain.id, L(domain.name));
        const available = choicesForDomain(domain);
        const names = available.map(id => id === 'base'
            ? (domain.baseInstrument || domain.originalLabel || '')
            : L(CLINICAL_DATA.scales[id]?.name));
        return { domain, topic, available, names, searchable: [topic, ...names].join(' ').toLocaleLowerCase() };
    }).filter(item => {
        const configured = Boolean(item.domain.forms?.length || item.domain.baseInstrument ||
            item.domain.originalLabel || item.domain.questions?.some(question => question.scaleId));
        if (configured && !item.available.length) {
            state.selectedDomains.delete(item.domain.id);
            state.scaleChoices.delete(item.domain.id);
            return false;
        }
        return !query || item.searchable.includes(query);
    });

    const fragment = document.createDocumentFragment();
    const pills = document.createElement('div');
    pills.className = 'domain-groups';

    const clearErrorWhenSelectionIsValid = () => {
        const error = document.getElementById('domains-error');
        if (!error || error.classList.contains('hidden')) return;
        const hasUnchosenScaleList = selectedDomainForms().some(selected =>
            choicesForDomain(selected).length && !(selected.selectedForms || []).length);
        if (!state.selectedDomains.size) error.textContent = t('domains.error');
        else if (hasUnchosenScaleList) error.textContent = t('domains.error.scales');
        else error.classList.add('hidden');
    };

    const updatePillCount = (domainId, selectedCount) => {
        const pill = document.getElementById('topic-pill-' + domainId);
        if (!pill) return;
        pill.querySelector('.topic-pill-count')?.remove();
        if (!selectedCount) return;
        const badge = document.createElement('span');
        badge.className = 'topic-pill-count';
        badge.textContent = String(selectedCount);
        badge.setAttribute('aria-label', `${selectedCount} ${state.lang === 'hi' ? 'मापनियाँ चुनी गईं' : 'scales selected'}`);
        pill.append(badge);
    };

    const domainById = new Map(domains.map(item => [item.domain.id, item]));
    const assigned = new Set();
    const groups = DOMAIN_GROUPS.map(group => {
        const entries = group.domains.map(id => domainById.get(id)).filter(Boolean)
            .sort((a, b) => a.topic.localeCompare(b.topic, state.lang));
        entries.forEach(item => assigned.add(item.domain.id));
        return { group, entries };
    }).filter(group => group.entries.length);
    const uncategorized = domains.filter(item => !assigned.has(item.domain.id));
    if (uncategorized.length) {
        groups.push({
            group: { id: 'more_topics', label: 'domain-group.more' },
            entries: uncategorized.sort((a, b) => a.topic.localeCompare(b.topic, state.lang))
        });
    }

    groups.forEach(({ group, entries }) => {
        const details = document.createElement('details');
        details.className = 'domain-group';
        details.open = Boolean(query) || state.openDomainGroups.has(group.id);
        details.addEventListener('toggle', () => {
            if (query) return;
            if (details.open) state.openDomainGroups.add(group.id);
            else state.openDomainGroups.delete(group.id);
        });

        const summary = document.createElement('summary');
        summary.className = 'domain-group-summary';
        const label = document.createElement('span');
        label.textContent = t(group.label);
        const count = document.createElement('span');
        count.className = 'domain-group-count';
        count.textContent = t('domains.group.count').replace('{count}', String(entries.length));
        summary.append(label, count);
        const selectedInGroup = entries.filter(({ domain }) => state.selectedDomains.has(domain.id)).length;
        if (selectedInGroup) {
            const selectedCount = document.createElement('span');
            selectedCount.className = 'domain-group-selected';
            selectedCount.textContent = t('domains.group.selected').replace('{count}', String(selectedInGroup));
            summary.append(selectedCount);
        }
        details.append(summary);

        const groupPills = document.createElement('div');
        groupPills.className = 'domain-pills';
        groupPills.setAttribute('role', 'group');
        groupPills.setAttribute('aria-label', t(group.label));

        entries.forEach(({ domain, topic }) => {
            const selected = state.selectedDomains.has(domain.id);
            const button = document.createElement('button');
            button.type = 'button';
            button.id = 'topic-pill-' + domain.id;
            button.className = 'topic-pill' + (selected ? ' selected' : '');
            button.setAttribute('aria-pressed', String(selected));
            button.setAttribute('aria-controls', 'selected-topic-scales');
            const name = document.createElement('span');
            name.textContent = topic;
            button.append(name);
            const saved = state.scaleChoices.get(domain.id);
            const selectedScaleCount = Array.isArray(saved) ? saved.length : saved ? 1 : 0;
            if (selectedScaleCount) {
                const badge = document.createElement('span');
                badge.className = 'topic-pill-count';
                badge.textContent = String(selectedScaleCount);
                badge.setAttribute('aria-label', `${selectedScaleCount} ${state.lang === 'hi' ? 'मापनियाँ चुनी गईं' : 'scales selected'}`);
                button.append(badge);
            }
            button.addEventListener('click', () => {
                if (selected) {
                    state.selectedDomains.delete(domain.id);
                    state.scaleChoices.delete(domain.id);
                } else {
                    state.selectedDomains.add(domain.id);
                }
                renderDomainGrid();
                document.getElementById(button.id)?.focus({ preventScroll: true });
                clearErrorWhenSelectionIsValid();
            });
            groupPills.append(button);
        });
        details.append(groupPills);
        pills.append(details);
    });

    if (query && !domains.length) {
        const empty = document.createElement('p');
        empty.className = 'domain-search-empty';
        empty.textContent = t('domains.search.empty');
        pills.append(empty);
    }
    fragment.append(pills);

    const summary = document.createElement('p');
    summary.className = 'topic-selection-summary';
    summary.setAttribute('role', 'status');
    summary.setAttribute('aria-live', 'polite');
    const updateSelectionSummary = () => {
        const topicCount = state.selectedDomains.size;
        const selectedDomains = selectedDomainForms();
        const scaleCount = selectedDomains.reduce((total, domain) =>
            total + (domain.selectedForms || []).length, 0);
        const itemCount = selectedDomains.reduce((total, domain) => {
            const selectedForms = domain.selectedForms || [];
            if (!selectedForms.length) return total + (domain.questions || []).filter(question => !question.scaleId).length;
            return total + selectedForms.reduce((formTotal, id) => {
                if (id === 'base') return formTotal + (domain.questions || []).filter(question => !question.scaleId).length;
                const form = CLINICAL_DATA.scales[id];
                const questions = form?.parts?.flatMap(part => part.questions || []) || [];
                return formTotal + questions.filter(question => !question.nonScored && !question.tickBox).length;
            }, 0);
        }, 0);
        summary.textContent = t('domains.selection.summary')
            .replace('{topics}', String(topicCount))
            .replace('{scales}', String(scaleCount))
            .replace('{items}', String(itemCount));
    };
    updateSelectionSummary();
    fragment.append(summary);

    const selectedList = document.createElement('div');
    selectedList.className = 'topic-scale-shortlists';
    selectedList.id = 'selected-topic-scales';

    const selected = CLINICAL_DATA.domains
        .filter(domain => state.selectedDomains.has(domain.id))
        .map(domain => {
            const topic = t('topic.' + domain.id, L(domain.name));
            const available = choicesForDomain(domain);
            const names = available.map(id => id === 'base'
                ? (domain.baseInstrument || domain.originalLabel || '')
                : L(CLINICAL_DATA.scales[id]?.name));
            return { domain, topic, available, names };
        })
        .filter(item => !query || item.topic.toLocaleLowerCase().includes(query) ||
            item.names.some(name => name.toLocaleLowerCase().includes(query)));

    selected.forEach(({ domain, topic, available, names }) => {
        const section = document.createElement('section');
        section.className = 'topic-scale-shortlist';
        const heading = document.createElement('h3');
        heading.id = 'topic-scales-' + domain.id;
        heading.textContent = (state.lang === 'hi' ? 'मापनियाँ · ' : 'Scales · ') + topic;
        section.setAttribute('aria-labelledby', heading.id);
        section.append(heading);

        if (!available.length) {
            const note = document.createElement('p');
            note.className = 'scale-shortlist-prompt';
            note.textContent = t('domains.builtin.note');
            section.append(note);
            selectedList.append(section);
            return;
        }

        const saved = state.scaleChoices.get(domain.id);
        const chosen = new Set(Array.isArray(saved)
            ? saved.filter(id => available.includes(id))
            : saved && available.includes(saved) ? [saved]
                : defaultChoicesForDomain(domain));
        const options = document.createElement('div');
        options.className = 'scale-choice-list';
        options.setAttribute('role', 'group');
        options.setAttribute('aria-labelledby', heading.id);
        const domainMatches = query && topic.toLocaleLowerCase().includes(query);

        if (!chosen.size) {
            const required = document.createElement('p');
            required.className = 'scale-selection-needed';
            required.textContent = t('domains.scale.required');
            section.append(required);
        }

        available.forEach((id, index) => {
            const name = names[index];
            if (query && !domainMatches && !name.toLocaleLowerCase().includes(query)) return;
            const scale = id === 'base' ? null : CLINICAL_DATA.scales[id];
            const label = document.createElement('label');
            label.className = 'scale-choice-option';
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = id;
            checkbox.checked = chosen.has(id);
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) chosen.add(id);
                else chosen.delete(id);
                state.scaleChoices.set(domain.id, [...chosen]);
                updatePillCount(domain.id, chosen.size);
                updateSelectionSummary();
                clearErrorWhenSelectionIsValid();
            });
            const scaleName = document.createElement('span');
            scaleName.className = 'scale-choice-name';
            scaleName.textContent = name;
            label.append(checkbox, scaleName);
            if (scale) {
                const meta = document.createElement('span');
                meta.className = 'scale-choice-meta';
                const itemCount = (scale.parts || []).reduce((total, part) =>
                    total + (part.questions || []).filter(question => !question.nonScored && !question.tickBox).length, 0);
                if (itemCount) {
                    meta.textContent = `${itemCount} ${state.lang === 'hi' ? 'प्रश्न' : 'items'}`;
                    label.append(meta);
                }
            }
            options.append(label);
        });
        if (!options.childElementCount) {
            const empty = document.createElement('p');
            empty.className = 'domain-search-empty';
            empty.textContent = t('domains.search.empty');
            section.append(empty);
        } else section.append(options);
        selectedList.append(section);
    });

    if (!selected.length) {
        const prompt = document.createElement('p');
        prompt.className = 'scale-shortlist-prompt';
        const key = state.selectedDomains.size
            ? 'domains.selection.searchEmpty'
            : query ? 'domains.selection.searchPrompt' : 'domains.selection.prompt';
        prompt.textContent = t(key);
        selectedList.append(prompt);
    }
    fragment.append(selectedList);
    list.replaceChildren(fragment);
}

export { renderDomainGrid };
