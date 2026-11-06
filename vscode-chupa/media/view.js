'use strict';
/* global acquireVsCodeApi, toViewModels, renderGraph */

const vscode = acquireVsCodeApi();
const list = document.getElementById('list');
const detail = document.getElementById('detail');
const header = document.getElementById('header');

// Status colors for dots and for each section's own lanes.
const COLOR = {
	merged: 'var(--chupa-merged)',
	running: 'var(--chupa-queued)',
	queued: 'var(--chupa-queued)',
	blocked: 'var(--chupa-blocked)',
};

list.addEventListener('mouseleave', () => {
	hovered = undefined;
	pinned || show(running);
});

// The detail pane's height is the user's last drag, kept in webview state across reloads.
const split = document.getElementById('split');
const saved = vscode.getState()?.detailHeight;
if (saved) {
	detail.style.height = `${saved}px`;
}
split.addEventListener('pointerdown', e => {
	split.setPointerCapture(e.pointerId);
	split.classList.add('dragging');
	const top = detail.getBoundingClientRect().top;
	const move = ev => {
		detail.style.height = `${Math.max(40, Math.min(window.innerHeight - 80, ev.clientY - top))}px`;
	};
	const up = () => {
		split.removeEventListener('pointermove', move);
		split.removeEventListener('pointerup', up);
		split.classList.remove('dragging');
		vscode.setState({ ...vscode.getState(), detailHeight: detail.offsetHeight });
	};
	split.addEventListener('pointermove', move);
	split.addEventListener('pointerup', up);
});

// The detail pane shows the pinned row, else the hovered row, else the running ticket.
// Click pins a row so the mouse can travel to the pane.
let pinned;
let hovered;
let running;
let byStem = new Map();

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

function detailContent(row) {
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

function show(stem) {
	const row = byStem.get(stem);
	detail.replaceChildren(row ? detailContent(row) : el('div', 'detail-meta', 'Nothing running. Hover a ticket to see it here; click to pin.'));
	for (const node of list.children) {
		node.classList.toggle('pinned', node.dataset.stem === pinned);
	}
}

function render(snap) {
	const counts = {};
	for (const r of snap.rows) {
		counts[r.section] = (counts[r.section] ?? 0) + 1;
	}
	header.textContent = `drain ${snap.drain ? 'running' : 'stopped'} · ${counts.blocked ?? 0} blocked · ${counts.queued ?? 0} queued · ${counts.running ?? 0} running · ${counts.merged ?? 0} merged`;
	// Merged, running and queued rows form one line in run order, like main after squash merges. Branches are
	// Depends on edges between unmerged tickets only, transitively reduced; the hover still lists every edge.
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
		row.append(renderGraph(vms[i], COLOR[r.section]));
		row.append(el('span', 'stem', r.stem));
		row.append(el('span', 'status', r.status));
		row.dataset.stem = r.stem;
		row.addEventListener('mouseenter', () => {
			hovered = r.stem;
			pinned || show(r.stem);
		});
		row.addEventListener('click', () => {
			pinned = pinned === r.stem ? undefined : r.stem;
			show(r.stem);
		});
		row.addEventListener('dblclick', () => vscode.postMessage({ type: 'open', path: r.path }));
		return row;
	});
	byStem = new Map(snap.rows.map(r => [r.stem, r]));
	list.replaceChildren(...rows);
	running = snap.rows.find(r => r.section === 'running')?.stem;
	show(pinned ?? hovered ?? running);
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
