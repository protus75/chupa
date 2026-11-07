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
	if (row.review) {
		box.append(el('div', 'detail-meta', `review: ${row.review}`));
	}
	if (row.section === 'merged') {
		const c = row.commit;
		if (c) {
			box.append(section('Commit', el('div', 'detail-subject', c.subject)));
			box.append(el('div', 'detail-meta', `${c.short} · ${c.author} · ${c.dateAgo} (${c.dateDisplay})`));
		} else {
			box.append(el('div', 'detail-meta', 'no commit on main'));
		}
		if (row.mergedAt) {
			box.append(el('div', 'detail-meta', `settled ${row.mergedAtAgo} (${row.mergedAtDisplay})`));
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

function boxContent(row) {
	const result = el('div');
	const head = el('div', 'detail-title');
	head.append(el('span', `badge ${row.state}`, row.messageClass), el('span', 'detail-stem', ` ${row.id}`));
	result.append(head);
	for (const [label, text] of row.fields) result.append(section(label, el('div', 'detail-text', text)));
	const links = el('div', 'detail-links');
	if (row.path) links.append(openLink(row.path, 'Open message file'));
	if (row.link) links.append(openLink(row.link, 'Open ticket/record'));
	result.append(links);
	return result;
}

window.addEventListener('message', e => {
	const { snap, focus } = e.data;
	const box = focus?.kind === 'box' ? snap.box.find(r => r.id === focus.id) : undefined;
	const stem = focus?.kind === 'ticket' ? focus.id : snap.runningStem;
	const row = snap.rows.find(r => r.stem === stem);
	detail.replaceChildren(box ? boxContent(box) : row ? content(row) : el('div', 'detail-meta', 'Nothing running. Hover a ticket or message to see it here; click to pin.'));
});
vscode.postMessage({ type: 'ready' });
