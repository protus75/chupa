'use strict';
/* global acquireVsCodeApi, renderGraph */

const vscode = acquireVsCodeApi();
const list = document.getElementById('list');
const header = document.getElementById('header');

// Status colors for dots and for each section's own lanes.
const COLOR = {
	merged: 'var(--chupa-merged)',
	running: 'var(--chupa-queued)',
	queued: 'var(--chupa-queued)',
	blocked: 'var(--chupa-blocked)',
};

// The Details view shows the pinned row, else the hovered row, else the running ticket (focus undefined).
// Click pins a row so the mouse can leave the list without losing it.
let pinned;
let hovered;

function focus() {
	for (const node of list.children) {
		node.classList.toggle('pinned', node.dataset.stem === pinned);
	}
	vscode.postMessage({ type: 'focus', stem: pinned ?? hovered });
}

list.addEventListener('mouseleave', () => {
	hovered = undefined;
	focus();
});

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

function render(snap) {
	const counts = snap.counts;
	const lock = el('span', '', snap.lock ? '🔒' : '🔓');
	lock.title = snap.lock || 'unlocked';
	const commitLock = el('span', '', snap.commitLock ? '🔒' : '🔓');
	commitLock.title = snap.commitLock || 'unlocked';
	header.replaceChildren('engine ', lock, ' · commit ', commitLock, ` · ${counts.blocked ?? 0} blocked · ${counts.queued ?? 0} queued · ${counts.running ?? 0} running · ${counts.merged ?? 0} merged`);
	const rows = snap.rows.map(r => {
		const row = el('div', `row ${r.section}`);
		row.dataset.stem = r.stem;
		// Context keys for the right-click menu's `when` clauses in package.json; the command receives this object.
		row.dataset.vscodeContext = JSON.stringify({ ...r.menu, chupaStem: r.stem, preventDefaultContextMenuItems: true });
		row.append(renderGraph(r.graph, COLOR[r.section], COLOR));
		if (r.priorityTag) {
			row.append(el('span', 'priority', r.priorityTag));
		}
		row.append(el('span', 'stem', r.stem));
		row.append(el('span', 'status', r.status));
		row.addEventListener('mouseenter', () => {
			hovered = r.stem;
			focus();
		});
		row.addEventListener('click', () => {
			pinned = pinned === r.stem ? undefined : r.stem;
			focus();
		});
		row.addEventListener('dblclick', () => vscode.postMessage({ type: 'open', path: r.path }));
		return row;
	});
	list.replaceChildren(...snap.verdictDecisions.map(d => el('div', 'status', `${d.request_id}: ${d.verb} ${d.stem}: ${d.decision} -- ${d.reason}`)), ...rows);
	if (pinned && !snap.rows.some(r => r.stem === pinned)) {
		pinned = undefined;
	}
	focus();
}

window.addEventListener('message', e => {
	const msg = e.data;
	if (msg.type === 'data') {
		render(msg.snap);
	} else if (msg.type === 'error') {
		header.textContent = `snapshot failed: ${msg.message}`;
	}
});
vscode.postMessage({ type: 'ready' });
