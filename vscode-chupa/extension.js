'use strict';
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const { execFile } = require('child_process');

// The first workspace folder containing tickets.
function chupaRoot() {
	return (vscode.workspace.workspaceFolders ?? [])
		.map(f => f.uri.fsPath)
		.find(p => fs.existsSync(path.join(p, 'tickets')) && fs.statSync(path.join(p, 'tickets')).isDirectory());
}

function openTicket(rel) {
	const root = chupaRoot();
	if (root) {
		vscode.window.showTextDocument(vscode.Uri.file(path.join(root, rel)), { preview: true });
	}
}

const STEM = /^[a-z0-9][a-z0-9-]{1,63}$/;

function command(root) {
	return vscode.workspace.getConfiguration('chupa', vscode.Uri.file(root)).get('command');
}

function runData(root, args, options, callback) {
	const [binary, ...prefix] = command(root);
	execFile(binary, [...prefix, ...args], { cwd: root, ...options }, callback);
}

function devCommand(...args) {
	const root = chupaRoot();
	if (!root || !args.every(a => STEM.test(a))) return;
	const [binary, ...prefix] = command(root);
	const argv = [...prefix, ...args, ...(['confirm', 'reject'].includes(args[0]) ? ['--yes'] : [])];
	const task = new vscode.Task({ type: 'chupa' }, vscode.workspace.getWorkspaceFolder(vscode.Uri.file(root)), args.join(' '), 'chupa', new vscode.ProcessExecution(binary, argv, { cwd: root }));
	vscode.tasks.executeTask(task);
}

async function orderTicket(ctx, snapshot, field) {
	const root = chupaRoot();
	const row = snapshot.snap?.rows.find(r => r.stem === ctx?.chupaStem);
	if (!root || !row || !STEM.test(row.stem)) return;
	let args;
	if (field === 'priority') {
		const choice = await vscode.window.showQuickPick(['P0', 'P1', 'P2', 'P3'].map(label => ({ label, description: label === row.priority ? 'current' : '' })), { placeHolder: 'Set priority' });
		if (!choice) return;
		args = ['--priority', choice.label];
	} else {
		const choices = snapshot.snap.rows.filter(r => r.section !== 'merged' && r.stem !== row.stem && STEM.test(r.stem))
			.map(r => ({ label: r.stem, picked: row.runsBefore.includes(r.stem) }));
		const selected = await vscode.window.showQuickPick(choices, { canPickMany: true, placeHolder: 'Run before' });
		if (!selected) return;
		args = ['--runs-before', ...selected.map(item => item.label)];
	}
	runData(root, ['order', row.stem, ...args], {}, (err, stdout, stderr) => {
		if (err) vscode.window.showErrorMessage((stderr || err.message).trim());
		else snapshot.refresh();
	});
}

// A new Claude Code chat with the ticket in its prompt, through the /open URI its extension handles (read from its
// code, not documented, so an update may break it).
function askClaude(ctx, task) {
	const root = chupaRoot();
	const stem = ctx?.chupaStem;
	if (!root || !stem || !STEM.test(stem)) return;
	const kind = task === 'diagnose' && ctx.chupaSection === 'running' ? 'running' : task;
	runData(root, ['prompt', kind, stem], {}, (err, stdout, stderr) => {
		if (err) vscode.window.showErrorMessage((stderr || err.message).trim());
		else vscode.env.openExternal(vscode.Uri.parse(`${vscode.env.uriScheme}://anthropic.claude-code/open?prompt=${encodeURIComponent(stdout)}`));
	});
}

// One snapshot run feeds every view; it runs only while at least one view is visible.
class Snapshot {
	constructor() {
		this.snap = undefined;
		this.error = undefined;
		this.listeners = [];
		this.views = [];
		this.running = false;
		this.again = false;
	}

	refresh() {
		if (!this.views.some(v => v.visible)) {
			return;
		}
		if (this.running) {
			this.again = true;
			return;
		}
		const root = chupaRoot();
		if (!root) {
			this.publish(undefined, 'no workspace folder holds tickets/');
			return;
		}
		this.running = true;
		runData(root, ['snapshot'], { timeout: 30000, maxBuffer: 64 * 1024 * 1024 }, (err, stdout, stderr) => {
			this.running = false;
			if (err) {
				this.publish(this.snap, (stderr || err.message).trim().split('\n').pop());
			} else {
				this.publish(JSON.parse(stdout), undefined);
			}
			if (this.again) {
				this.again = false;
				this.refresh();
			}
		});
	}

	publish(snap, error) {
		this.snap = snap;
		this.error = error;
		this.listeners.forEach(f => f());
	}
}

function webviewHtml(extensionUri, webview, body, scripts) {
	const media = vscode.Uri.joinPath(extensionUri, 'media');
	webview.options = { enableScripts: true, localResourceRoots: [media] };
	const nonce = crypto.randomBytes(16).toString('base64');
	const uri = f => webview.asWebviewUri(vscode.Uri.joinPath(media, f));
	webview.html = `<!doctype html>
<html><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource}; script-src 'nonce-${nonce}';">
<link rel="stylesheet" href="${uri('view.css')}">
</head><body>
${body}
${scripts.map(s => `<script nonce="${nonce}" src="${uri(s)}"></script>`).join('\n')}
</body></html>`;
}

function showLifecycle(extensionUri) {
	const media = vscode.Uri.joinPath(extensionUri, 'media');
	const panel = vscode.window.createWebviewPanel('chupa.lifecycle', 'chupa ticket lifecycle', vscode.ViewColumn.Active, { localResourceRoots: [media] });
	const svg = panel.webview.asWebviewUri(vscode.Uri.joinPath(media, 'ticket-lifecycle.svg'));
	panel.webview.html = `<!doctype html>
<html><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src ${panel.webview.cspSource};">
</head><body><img src="${svg}" alt="chupa ticket lifecycle"></body></html>`;
}

class TicketsView {
	constructor(extensionUri, snapshot, details) {
		this.extensionUri = extensionUri;
		this.snapshot = snapshot;
		this.details = details;
		snapshot.listeners.push(() => this.post());
	}

	resolveWebviewView(view) {
		this.view = view;
		this.snapshot.views.push(view);
		webviewHtml(this.extensionUri, view.webview, '<div id="header">loading…</div><div id="list"></div>', ['graph.js', 'view.js']);
		view.webview.onDidReceiveMessage(msg => {
			if (msg.type === 'ready') {
				this.snapshot.snap ? this.post() : this.snapshot.refresh();
			} else if (msg.type === 'focus') {
				this.details.setFocus(msg.stem);
			} else if (msg.type === 'open') {
				openTicket(msg.path);
			}
		});
		view.onDidChangeVisibility(() => view.visible && this.snapshot.refresh());
	}

	post() {
		const { snap, error } = this.snapshot;
		if (error) {
			this.view?.webview.postMessage({ type: 'error', message: error });
		} else if (snap) {
			this.view?.webview.postMessage({ type: 'data', snap });
		}
	}
}

class DetailsView {
	constructor(extensionUri, snapshot) {
		this.extensionUri = extensionUri;
		this.snapshot = snapshot;
		this.focus = undefined;
		snapshot.listeners.push(() => this.post());
	}

	resolveWebviewView(view) {
		this.view = view;
		this.snapshot.views.push(view);
		webviewHtml(this.extensionUri, view.webview, '<div id="detail"></div>', ['detail.js']);
		view.webview.onDidReceiveMessage(msg => {
			if (msg.type === 'ready') {
				this.snapshot.snap ? this.post() : this.snapshot.refresh();
			} else if (msg.type === 'open') {
				openTicket(msg.path);
			}
		});
		view.onDidChangeVisibility(() => view.visible && this.post());
	}

	setFocus(stem) {
		this.focus = stem;
		this.post();
	}

	post() {
		if (this.snapshot.snap) {
			this.view?.webview.postMessage({ snap: this.snapshot.snap, focus: this.focus });
		}
	}
}

// Recent Steps is a native tree, newest first, like watch's "Recent steps".
class StepsTree {
	constructor(snapshot) {
		this.snapshot = snapshot;
		this.changed = new vscode.EventEmitter();
		this.onDidChangeTreeData = this.changed.event;
		snapshot.listeners.push(() => this.changed.fire());
	}

	getChildren() {
		return this.snapshot.snap?.steps ?? [];
	}

	getTreeItem(step) {
		const clock = new Date(step.ts).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
		const item = new vscode.TreeItem(`${clock}  ${step.stem ?? ''}`);
		item.description = step.text;
		item.tooltip = `${new Date(step.ts).toLocaleString()}\n${step.stem ? step.stem + ': ' : ''}${step.text}`;
		const icon = step.stem ? (step.text.endsWith(' start') ? 'debug-start' : step.text.includes('ok') ? 'pass' : 'circle-slash') :
			step.text.includes('ended without a stop record') ? 'warning' : step.text.includes(' started ') ? 'debug-start' : 'debug-stop';
		item.iconPath = new vscode.ThemeIcon(icon);
		if (step.stem) {
			item.command = { command: 'chupa.openTicket', title: 'Open ticket.md', arguments: [`tickets/${step.stem}/ticket.md`] };
		}
		return item;
	}
}

function activate(context) {
	const snapshot = new Snapshot();
	const details = new DetailsView(context.extensionUri, snapshot);
	const tickets = new TicketsView(context.extensionUri, snapshot, details);
	const steps = new StepsTree(snapshot);
	const stepsView = vscode.window.createTreeView('chupa.steps', { treeDataProvider: steps });
	snapshot.views.push(stepsView);
	stepsView.onDidChangeVisibility(e => e.visible && snapshot.refresh());
	context.subscriptions.push(
		stepsView,
		vscode.window.registerWebviewViewProvider('chupa.details', details),
		vscode.window.registerWebviewViewProvider('chupa.tickets', tickets),
		vscode.commands.registerCommand('chupa.refresh', () => snapshot.refresh()),
		vscode.commands.registerCommand('chupa.openTicket', openTicket),
		vscode.commands.registerCommand('chupa.lifecycle', () => showLifecycle(context.extensionUri)),
		vscode.commands.registerCommand('chupa.openSettings', () => vscode.commands.executeCommand('workbench.action.openSettings', '@ext:chupa.vscode-chupa')),
		vscode.commands.registerCommand('chupa.ticket.open', ctx => openTicket(`tickets/${ctx.chupaStem}/ticket.md`)),
		vscode.commands.registerCommand('chupa.ticket.review', ctx => devCommand('review', ctx.chupaStem)),
		vscode.commands.registerCommand('chupa.ticket.lint', ctx => devCommand('lint', ctx.chupaStem)),
		vscode.commands.registerCommand('chupa.ticket.priority', ctx => orderTicket(ctx, snapshot, 'priority')),
		vscode.commands.registerCommand('chupa.ticket.runsBefore', ctx => orderTicket(ctx, snapshot, 'runsBefore')),
		vscode.commands.registerCommand('chupa.ticket.run', ctx => devCommand('run', ctx.chupaStem)),
		vscode.commands.registerCommand('chupa.ticket.confirm', ctx => devCommand('confirm', ctx.chupaStem)),
		vscode.commands.registerCommand('chupa.ticket.reject', ctx => devCommand('reject', ctx.chupaStem)),
		vscode.commands.registerCommand('chupa.ticket.askDiagnose', ctx => askClaude(ctx, 'diagnose')),
		vscode.commands.registerCommand('chupa.ticket.askReview', ctx => askClaude(ctx, 'review')),
		...['drain', 'stop', 'kill', 'status'].map(verb => vscode.commands.registerCommand(`chupa.${verb}`, () => devCommand(verb))),
	);

	let timer;
	const soon = () => {
		clearTimeout(timer);
		timer = setTimeout(() => snapshot.refresh(), 700);
	};
	const root = chupaRoot();
	if (root) {
		const watch = (base, glob) => {
			const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(base, glob));
			watcher.onDidChange(soon);
			watcher.onDidCreate(soon);
			watcher.onDidDelete(soon);
			context.subscriptions.push(watcher);
			return watcher;
		};
		watch(root, 'tickets/*/ticket.md');
		let stateWatcher, stateDir;
		snapshot.listeners.push(() => {
			const next = snapshot.snap?.stateDir;
			if (next && next !== stateDir) {
				stateWatcher?.dispose();
				stateDir = next;
				stateWatcher = watch(next, '{journal/*.jsonl,queue.json,engine.log}');
			}
		});
	}

	// The running step's elapsed time moves without any file changing; 0 seconds leaves only file-change refreshes.
	let tick;
	const schedule = () => {
		clearInterval(tick);
		const seconds = vscode.workspace.getConfiguration('chupa').get('refreshSeconds', 15);
		tick = seconds > 0 ? setInterval(() => snapshot.refresh(), seconds * 1000) : undefined;
	};
	schedule();
	context.subscriptions.push(vscode.workspace.onDidChangeConfiguration(e => e.affectsConfiguration('chupa.refreshSeconds') && schedule()));
	context.subscriptions.push({ dispose: () => clearInterval(tick) });
}

module.exports = { activate, deactivate() {} };
