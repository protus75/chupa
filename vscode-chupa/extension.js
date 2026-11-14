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

function command(root) {
	return vscode.workspace.getConfiguration('chupa', vscode.Uri.file(root)).get('command');
}

function runData(root, args, options, callback) {
	const [binary, ...prefix] = command(root);
	execFile(binary, [...prefix, ...args], { cwd: root, ...options }, (err, stdout, stderr) => {
		if (err?.code === 'ENOENT') {
			callback(new Error(`chupa command not found: ${binary} (run from ${root}). Set chupa.command in settings.`), stdout, '');
		} else callback(err, stdout, stderr);
	});
}

function devCommand(...args) {
	const root = chupaRoot();
	if (!root) return;
	const [binary, ...prefix] = command(root);
	const argv = [...prefix, ...args];
	const task = new vscode.Task({ type: 'chupa', args }, vscode.workspace.getWorkspaceFolder(vscode.Uri.file(root)), args.join(' '), 'chupa', new vscode.ProcessExecution(binary, argv, { cwd: root }));
	vscode.tasks.executeTask(task);
}

async function orderTicket(ctx, snapshot, field) {
	const root = chupaRoot();
	const row = snapshot.snap?.rows.find(r => r.stem === ctx?.chupaStem);
	if (!root || !row) return;
	let args;
	if (field === 'priority') {
		const choice = await vscode.window.showQuickPick(row.priorityChoices, { placeHolder: 'Set priority' });
		if (!choice) return;
		args = ['--priority', choice.label];
	} else {
		const selected = await vscode.window.showQuickPick(row.runsBeforeChoices, { canPickMany: true, placeHolder: 'Run before' });
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
	if (!root || !stem) return;
	runData(root, ['prompt', task, stem], {}, (err, stdout, stderr) => {
		if (err) vscode.window.showErrorMessage((stderr || err.message).trim());
		else vscode.env.openExternal(vscode.Uri.parse(`${vscode.env.uriScheme}://anthropic.claude-code/open?prompt=${encodeURIComponent(stdout)}`));
	});
}

// One snapshot run feeds every view and the Activity Bar badge.
class Snapshot {
	constructor() {
		this.snap = undefined;
		this.error = undefined;
		this.listeners = [];
		this.running = false;
		this.again = false;
	}

	refresh() {
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
				this.publish(this.snap, (stderr || err.message).trim());
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
		if (snap) vscode.commands.executeCommand('setContext', 'chupa.engineRunning', snap.engine);
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
		webviewHtml(this.extensionUri, view.webview, '<div id="header">loading…</div><div id="list"></div>', ['graph.js', 'view.js']);
		view.webview.onDidReceiveMessage(msg => {
			if (msg.type === 'ready') {
				this.snapshot.snap ? this.post() : this.snapshot.refresh();
			} else if (msg.type === 'focus') {
				this.details.setFocus('ticket', msg.stem);
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

class BoxView {
	constructor(extensionUri, snapshot, details) {
		this.extensionUri = extensionUri;
		this.snapshot = snapshot;
		this.details = details;
		snapshot.listeners.push(() => this.post());
	}
	resolveWebviewView(view) {
		this.view = view;
		webviewHtml(this.extensionUri, view.webview, '<div id="header">loading…</div><div id="list"></div>', ['box.js']);
		view.webview.onDidReceiveMessage(msg => {
			if (msg.type === 'ready') this.snapshot.snap ? this.post() : this.snapshot.refresh();
			else if (msg.type === 'focus') this.details.setFocus('box', msg.id);
			else if (msg.type === 'open' && msg.path) openTicket(msg.path);
		});
		view.onDidChangeVisibility(() => view.visible && this.snapshot.refresh());
	}
	post() {
		const { snap, error } = this.snapshot;
		if (error) this.view?.webview.postMessage({ type: 'error', message: error });
		else if (snap) this.view?.webview.postMessage({ type: 'data', snap });
	}
}

class DetailsView {
	constructor(extensionUri, snapshot) {
		this.extensionUri = extensionUri;
		this.snapshot = snapshot;
		this.focus = undefined;
		this.focuses = {};
		snapshot.listeners.push(() => this.post());
	}

	resolveWebviewView(view) {
		this.view = view;
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

	setFocus(kind, id) {
		const previous = this.focuses[kind];
		this.focuses[kind] = id;
		const other = kind === 'box' ? 'ticket' : 'box';
		if (id && id !== previous) this.focus = { kind, id };
		else if (!id && this.focus?.kind === kind) this.focus = this.focuses[other] ? { kind: other, id: this.focuses[other] } : undefined;
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
		const item = new vscode.TreeItem(`${step.timeDisplay}  ${step.stem ?? ''}`);
		item.description = step.text;
		item.tooltip = `${step.dateDisplay}\n${step.stem ? step.stem + ': ' : ''}${step.text}`;
		const icons = { preflight_start: ['rocket'], preflight_ok: ['rocket', 'testing.iconPassed'], preflight_failed: ['rocket', 'testing.iconFailed'], retro_check_start: ['calendar'], retro_check_ok: ['calendar', 'testing.iconPassed'], retro_check_failed: ['calendar', 'testing.iconFailed'], requisition_review_start: ['law'], requisition_review_ok: ['law', 'testing.iconPassed'], requisition_review_failed: ['law', 'testing.iconFailed'], stage_start: ['question'], stage_ok: ['question', 'testing.iconPassed'], stage_failed: ['question', 'testing.iconFailed'], author_start: ['edit'], author_ok: ['edit', 'testing.iconPassed'], author_failed: ['edit', 'testing.iconFailed'], engine_start: ['debug-start'], engine_stop: ['debug-stop'], engine_lost: ['warning'], implement_start: ['code'], implement_ok: ['code', 'testing.iconPassed'], implement_failed: ['code', 'testing.iconFailed'], review_start: ['eye'], review_ok: ['eye', 'testing.iconPassed'], review_failed: ['eye', 'testing.iconFailed'], diagnose_start: ['debug'], diagnose_ok: ['debug', 'testing.iconPassed'], diagnose_failed: ['debug', 'testing.iconFailed'], rework_start: ['tools'], rework_ok: ['tools', 'testing.iconPassed'], rework_failed: ['tools', 'testing.iconFailed'], retro_start: ['history'], retro_ok: ['history', 'testing.iconPassed'], retro_failed: ['history', 'testing.iconFailed'], check_start: ['checklist'], check_ok: ['checklist', 'testing.iconPassed'], check_failed: ['checklist', 'testing.iconFailed'], merge_start: ['git-merge'], merge_ok: ['git-merge', 'testing.iconPassed'], merge_failed: ['git-merge', 'testing.iconFailed'], triage_start: ['inbox'], triage_ok: ['inbox', 'testing.iconPassed'], triage_failed: ['inbox', 'testing.iconFailed'] };
		const [icon, color] = icons[step.kind];
		item.iconPath = new vscode.ThemeIcon(icon, color ? new vscode.ThemeColor(color) : undefined);
		if (step.path) {
			item.command = { command: 'chupa.openTicket', title: 'Open step file', arguments: [step.path] };
		}
		return item;
	}
}

class StatsTree {
	constructor(snapshot) {
		this.rows = [];
		this.running = false;
		this.again = false;
		this.changed = new vscode.EventEmitter();
		this.onDidChangeTreeData = this.changed.event;
		snapshot.listeners.push(() => this.refresh());
	}

	refresh() {
		if (!this.view?.visible) return;
		if (this.running) {
			this.again = true;
			return;
		}
		const root = chupaRoot();
		if (!root) {
			this.rows = [{ label: 'no workspace folder holds tickets/', description: '', children: [] }];
			this.changed.fire();
			return;
		}
		this.running = true;
		const window = vscode.workspace.getConfiguration('chupa', vscode.Uri.file(root)).get('statsWindow');
		runData(root, ['stats', '--tree', '--window', window], { timeout: 30000 }, (err, stdout, stderr) => {
			this.running = false;
			this.rows = err ? [{ label: (stderr || err.message).trim(), description: '', children: [] }] : JSON.parse(stdout);
			this.changed.fire();
			if (this.again) {
				this.again = false;
				this.refresh();
			}
		});
	}

	getChildren(row) { return row ? row.children : this.rows; }

	getTreeItem(row) {
		const item = new vscode.TreeItem(row.label, row.children.length ? vscode.TreeItemCollapsibleState.Collapsed : vscode.TreeItemCollapsibleState.None);
		item.description = row.description;
		return item;
	}
}

function activate(context) {
	const snapshot = new Snapshot();
	const details = new DetailsView(context.extensionUri, snapshot);
	const tickets = new TicketsView(context.extensionUri, snapshot, details);
	const box = new BoxView(context.extensionUri, snapshot, details);
	const steps = new StepsTree(snapshot);
	const stepsView = vscode.window.createTreeView('chupa.steps', { treeDataProvider: steps });
	const stats = new StatsTree(snapshot);
	const statsView = vscode.window.createTreeView('chupa.stats', { treeDataProvider: stats });
	stats.view = statsView;
	statsView.onDidChangeVisibility(e => e.visible && stats.refresh());
	snapshot.listeners.push(() => { stepsView.badge = snapshot.snap?.badge ?? undefined; });
	stepsView.onDidChangeVisibility(e => e.visible && snapshot.refresh());
	context.subscriptions.push(
		stepsView,
		statsView,
		vscode.window.registerWebviewViewProvider('chupa.details', details),
		vscode.window.registerWebviewViewProvider('chupa.tickets', tickets),
		vscode.window.registerWebviewViewProvider('chupa.box', box),
		vscode.commands.registerCommand('chupa.box.open', ctx => openTicket(ctx.chupaPath)),
		vscode.commands.registerCommand('chupa.box.link', ctx => openTicket(ctx.chupaLink)),
		vscode.commands.registerCommand('chupa.box.triage', ctx => devCommand('triage', ...ctx.chupaIds)),
		vscode.commands.registerCommand('chupa.box.dismiss', ctx => devCommand('dismiss', ...ctx.chupaIds)),
		vscode.commands.registerCommand('chupa.box.discuss', ctx => {
			const root = chupaRoot();
			if (!root) return;
			runData(root, ['prompt', 'box', ...ctx.chupaIds], {}, (err, stdout, stderr) => {
				if (err) vscode.window.showErrorMessage((stderr || err.message).trim());
				else vscode.env.openExternal(vscode.Uri.parse(`${vscode.env.uriScheme}://anthropic.claude-code/open?prompt=${encodeURIComponent(stdout)}`));
			});
		}),
		vscode.commands.registerCommand('chupa.bulkTriage', () => devCommand('triage')),
		vscode.commands.registerCommand('chupa.refresh', () => { snapshot.refresh(); stats.refresh(); }),
		vscode.commands.registerCommand('chupa.openTicket', openTicket),
		vscode.commands.registerCommand('chupa.lifecycle', () => showLifecycle(context.extensionUri)),
		vscode.commands.registerCommand('chupa.openSettings', () => vscode.commands.executeCommand('workbench.action.openSettings', '@ext:chunkydragon.vscode-chupa')),
		vscode.commands.registerCommand('chupa.ticket.open', ctx => openTicket(`tickets/${ctx.chupaStem}/ticket.md`)),
		vscode.commands.registerCommand('chupa.ticket.review', ctx => devCommand('review', ctx.chupaStem)),
		vscode.commands.registerCommand('chupa.ticket.lint', ctx => devCommand('lint', ctx.chupaStem)),
		vscode.commands.registerCommand('chupa.ticket.priority', ctx => orderTicket(ctx, snapshot, 'priority')),
		vscode.commands.registerCommand('chupa.ticket.runsBefore', ctx => orderTicket(ctx, snapshot, 'runsBefore')),
		vscode.commands.registerCommand('chupa.ticket.run', ctx => devCommand('run', ctx.chupaStem)),
		vscode.commands.registerCommand('chupa.ticket.confirm', ctx => devCommand(...snapshot.snap.verdictCommands.confirm, ctx.chupaStem)),
		vscode.commands.registerCommand('chupa.ticket.reject', ctx => devCommand(...snapshot.snap.verdictCommands.reject, ctx.chupaStem)),
		vscode.commands.registerCommand('chupa.ticket.askDiagnose', ctx => askClaude(ctx, 'diagnose')),
		vscode.commands.registerCommand('chupa.ticket.askReview', ctx => askClaude(ctx, 'review')),
		vscode.commands.registerCommand('chupa.ticket.askDrafts', () => {
			const root = chupaRoot();
			if (!root) return;
			runData(root, ['prompt', 'drafts'], {}, (err, stdout, stderr) => {
				if (err) vscode.window.showErrorMessage((stderr || err.message).trim());
				else vscode.env.openExternal(vscode.Uri.parse(`${vscode.env.uriScheme}://anthropic.claude-code/open?prompt=${encodeURIComponent(stdout)}`));
			});
		}),
		vscode.commands.registerCommand('chupa.engine', async () => {
			const choice = await vscode.window.showQuickPick(snapshot.snap?.engineVerbs ?? []);
			if (choice) devCommand(...choice.argv);
		}),
		vscode.commands.registerCommand('chupa.playDrain', () => devCommand(...snapshot.snap.drainCommand)),
		vscode.commands.registerCommand('chupa.playServe', () => devCommand('serve')),
		vscode.commands.registerCommand('chupa.stopRunning', () => devCommand('stop')),
		vscode.commands.registerCommand('chupa.openConfig', () => {
			if (snapshot.snap) vscode.window.showTextDocument(vscode.Uri.file(snapshot.snap.configPath), { preview: true });
		}),
	);

	let timer;
	const soon = () => {
		clearTimeout(timer);
		timer = setTimeout(() => snapshot.refresh(), 700);
	};
	let watchers = [], watchList;
	snapshot.listeners.push(() => {
		const next = snapshot.snap?.watch;
		if (!next || JSON.stringify(next) === watchList) return;
		watchers.forEach(watcher => watcher.dispose());
		watchList = JSON.stringify(next);
		watchers = next.map(({ base, glob }) => {
			const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(base, glob));
			watcher.onDidChange(soon);
			watcher.onDidCreate(soon);
			watcher.onDidDelete(soon);
			return watcher;
		});
	});
	context.subscriptions.push({ dispose: () => watchers.forEach(watcher => watcher.dispose()) });

	// The running step's elapsed time moves without any file changing; 0 seconds leaves only file-change refreshes.
	let tick;
	const schedule = () => {
		clearInterval(tick);
		const seconds = vscode.workspace.getConfiguration('chupa').get('refreshSeconds');
		tick = seconds > 0 ? setInterval(() => snapshot.refresh(), seconds * 1000) : undefined;
	};
	schedule();
	snapshot.refresh();
	context.subscriptions.push(vscode.workspace.onDidChangeConfiguration(e => {
		if (e.affectsConfiguration('chupa.refreshSeconds')) schedule();
		if (e.affectsConfiguration('chupa.statsWindow')) stats.refresh();
	}));
	context.subscriptions.push({ dispose: () => clearInterval(tick) });
}

module.exports = { activate, deactivate() {} };
