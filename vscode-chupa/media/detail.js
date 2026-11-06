'use strict';
/* global acquireVsCodeApi */

const vscode = acquireVsCodeApi();
const detail = document.getElementById('detail');

function el(tag, cls, text) {
	const node = document.createElement(tag);
	if (cls) {
		node.className = cls;
	}
	if (text !== undefined) {
		node.textContent = text;
	}
	return node;
}

function when(iso) {
	const d = new Date(iso);
	const mins = Math.round((Date.now() - d.getTime()) / 60000);
	const ago = mins < 60 ? `${mins} min ago` : mins < 2880 ? `${Math.round(mins / 60)} hr ago` : `${Math.round(mins / 1440)} days ago`;
	return `${ago} (${d.toLocaleString()})`;
}

function openLink(path, label = 'Open ticket.md') {
	const a = el('a', 'link', label);
	a.href = '#';
	a.addEventListener('click', e => {
		e.preventDefault();
		vscode.postMessage({ type: 'open', path });
	});
	return a;
}

function section(title, body) {
	const wrap = el('div', 'detail-section');
	wrap.append(el('div', 'detail-heading', title));
	wrap.append(body);
	return wrap;
}

function content(row) {
	const box = el('div');
	const head = el('div', 'detail-title');
	head.append(el('span', `badge ${row.section}`, row.section), el('span', 'detail-stem', ` ${row.stem}`));
	box.append(head);
	box.append(el('div', 'detail-meta', row.status + (row.priority ? ` · ${row.priority}` : '')));
	if (row.section === 'merged') {
		const c = row.commit;
		if (c) {
			box.append(section('Commit', el('div', 'detail-subject', c.subject)));
			box.append(el('div', 'detail-meta', `${c.short} · ${c.author} · ${when(c.date)}`));
		} else {
			box.append(el('div', 'detail-meta', 'no commit on main'));
		}
		if (row.mergedAt) {
			box.append(el('div', 'detail-meta', `settled ${when(row.mergedAt)}`));
		}
	} else {
		box.append(section('Goal / Why', el('div', 'detail-text', row.goal || '(none)')));
		box.append(section('Runs before', el('div', 'detail-text', row.runsBefore.length ? row.runsBefore.join(', ') : '(none)')));
	}
	if (row.depends.length) {
		box.append(section('Depends on', el('div', 'detail-text', row.depends.join(', '))));
	}
	const links = el('div', 'detail-links');
	links.append(openLink(row.path));
	box.append(links);
	return box;
}

// focus is the Tickets view's pinned or hovered stem; undefined falls back to the running ticket.
window.addEventListener('message', e => {
	const { snap, focus } = e.data;
	const stem = focus ?? snap.rows.find(r => r.section === 'running')?.stem;
	const row = snap.rows.find(r => r.stem === stem);
	detail.replaceChildren(row ? content(row) : el('div', 'detail-meta', 'Nothing running. Hover a ticket to see it here; click to pin.'));
});
vscode.postMessage({ type: 'ready' });
