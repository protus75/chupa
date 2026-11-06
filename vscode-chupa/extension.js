'use strict';
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
const { execFile } = require('child_process');

// The chupa checkout: the first workspace folder holding watch.py and this extension's snapshot script.
function chupaRoot() {
	return (vscode.workspace.workspaceFolders ?? [])
		.map(f => f.uri.fsPath)
		.find(p => fs.existsSync(path.join(p, 'watch.py')) && fs.existsSync(path.join(p, 'vscode-chupa', 'snapshot.py')));
}

class TicketsView {
	constructor(extensionUri) {
		this.extensionUri = extensionUri;
		this.view = undefined;
		this.running = false;
		this.again = false;
	}

	resolveWebviewView(view) {
		this.view = view;
		const media = vscode.Uri.joinPath(this.extensionUri, 'media');
		view.webview.options = { enableScripts: true, localResourceRoots: [media] };
		const nonce = crypto.randomBytes(16).toString('base64');
		const uri = f => view.webview.asWebviewUri(vscode.Uri.joinPath(media, f));
		view.webview.html = `<!doctype html>
<html><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${view.webview.cspSource}; script-src 'nonce-${nonce}';">
<link rel="stylesheet" href="${uri('view.css')}">
</head><body>
<div id="header">loading…</div><div id="detail"></div><div id="split" title="Drag to resize"></div><div id="list"></div>
<script nonce="${nonce}" src="${uri('graph.js')}"></script>
<script nonce="${nonce}" src="${uri('view.js')}"></script>
</body></html>`;
		view.webview.onDidReceiveMessage(msg => {
			if (msg.type === 'ready') {
				this.refresh();
			} else if (msg.type === 'open') {
				const root = chupaRoot();
				if (root) {
					vscode.window.showTextDocument(vscode.Uri.file(path.join(root, msg.path)), { preview: true });
				}
			}
		});
		view.onDidChangeVisibility(() => view.visible && this.refresh());
	}

	refresh() {
		if (!this.view?.visible) {
			return;
		}
		if (this.running) {
			this.again = true;
			return;
		}
		const root = chupaRoot();
		if (!root) {
			this.view.webview.postMessage({ type: 'error', message: 'no workspace folder holds watch.py and vscode-chupa/snapshot.py' });
			return;
		}
		this.running = true;
		const python = path.join(root, '.venv', 'bin', 'python');
		execFile(python, [path.join(root, 'vscode-chupa', 'snapshot.py')], { cwd: root, timeout: 30000, maxBuffer: 64 * 1024 * 1024 }, (err, stdout, stderr) => {
			this.running = false;
			if (err) {
				this.view?.webview.postMessage({ type: 'error', message: (stderr || err.message).trim().split('\n').pop() });
			} else {
				this.view?.webview.postMessage({ type: 'data', snap: JSON.parse(stdout) });
			}
			if (this.again) {
				this.again = false;
				this.refresh();
			}
		});
	}
}

function activate(context) {
	const provider = new TicketsView(context.extensionUri);
	context.subscriptions.push(vscode.window.registerWebviewViewProvider('chupa.tickets', provider));
	context.subscriptions.push(vscode.commands.registerCommand('chupa.refresh', () => provider.refresh()));

	let timer;
	const soon = () => {
		clearTimeout(timer);
		timer = setTimeout(() => provider.refresh(), 700);
	};
	const root = chupaRoot();
	if (root) {
		for (const glob of ['.chupa/state/{journal/*.jsonl,queue.json,engine.log}', 'tickets/*/ticket.md']) {
			const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(root, glob));
			watcher.onDidChange(soon);
			watcher.onDidCreate(soon);
			watcher.onDidDelete(soon);
			context.subscriptions.push(watcher);
		}
	}
	// The running step's elapsed time moves without any file changing; 0 seconds leaves only file-change refreshes.
	let tick;
	const schedule = () => {
		clearInterval(tick);
		const seconds = vscode.workspace.getConfiguration('chupa').get('refreshSeconds', 15);
		tick = seconds > 0 ? setInterval(() => provider.refresh(), seconds * 1000) : undefined;
	};
	schedule();
	context.subscriptions.push(vscode.workspace.onDidChangeConfiguration(e => e.affectsConfiguration('chupa.refreshSeconds') && schedule()));
	context.subscriptions.push({ dispose: () => clearInterval(tick) });
}

module.exports = { activate, deactivate() {} };
