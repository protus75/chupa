'use strict';
/* global acquireVsCodeApi, toViewModels, renderGraph */

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
	const counts = {};
	for (const r of snap.rows) {
		counts[r.section] = (counts[r.section] ?? 0) + 1;
	}
	header.textContent = `engine ${snap.engine ? 'running' : 'stopped'} · ${counts.blocked ?? 0} blocked · ${counts.queued ?? 0} queued · ${counts.running ?? 0} running · ${counts.merged ?? 0} merged`;
	// Merged, running and queued rows form one line in run order, like main after squash merges. Branches are
	// Depends on edges between unmerged tickets only, transitively reduced; Details still lists every edge.
	const unmerged = new Set(snap.rows.filter(r => r.section !== 'merged').map(r => r.stem));
	const deps = new Map(snap.rows.map(r => [r.stem, r.depends.filter(d => unmerged.has(d))]));
	const reach = new Map();
	const reachable = stem => {
		if (!reach.has(stem)) {
			const seen = new Set();
			reach.set(stem, seen);
			for (const d of deps.get(stem) ?? []) {
				seen.add(d);
				reachable(d).forEach(x => seen.add(x));
			}
		}
		return reach.get(stem);
	};
	const reduced = stem => deps.get(stem).filter(d => !deps.get(stem).some(o => o !== d && reachable(o).has(d)));
	const items = snap.rows.map((r, i) => {
		const below = snap.rows[i + 1]?.stem;
		const kind = r.section === 'running' ? 'HEAD' : 'node';
		if (r.section === 'blocked') {
			return { id: r.stem, parentIds: reduced(r.stem), kind, laneColor: COLOR.blocked, branchColor: COLOR.blocked };
		}
		const branches = r.section === 'merged' ? [] : reduced(r.stem).filter(d => d !== below);
		return { id: r.stem, parentIds: below ? [below, ...branches] : branches, kind, laneColor: COLOR[r.section] };
	});
	const vms = toViewModels(items);
	const rows = snap.rows.map((r, i) => {
		const row = el('div', `row ${r.section}`);
		row.dataset.stem = r.stem;
		// Context keys for the right-click menu's `when` clauses in package.json; the command receives this object.
		row.dataset.vscodeContext = JSON.stringify({ chupaStem: r.stem, chupaSection: r.section, chupaHeld: r.held, preventDefaultContextMenuItems: true });
		row.append(renderGraph(vms[i], COLOR[r.section]));
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
	list.replaceChildren(...rows);
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
