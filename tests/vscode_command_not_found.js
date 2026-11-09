'use strict';

const Module = require('module');
const [root, binary] = process.argv.slice(2);
const disposable = { dispose() {} };
let tickets;
let receive;
const vscode = {
	Uri: { file: fsPath => ({ fsPath }), joinPath: (...parts) => parts.join('/') },
	workspace: {
		workspaceFolders: [{ uri: { fsPath: root } }],
		getConfiguration: () => ({ get: key => key === 'command' ? [binary] : 0 }),
		onDidChangeConfiguration: () => disposable,
	},
	window: {
		createTreeView: () => ({ ...disposable, onDidChangeVisibility() {} }),
		registerWebviewViewProvider: (id, provider) => { if (id === 'chupa.tickets') tickets = provider; return disposable; },
	},
	commands: { registerCommand: () => disposable },
	EventEmitter: class { constructor() { this.event = () => {}; } },
};
const load = Module._load;
Module._load = function (request, parent, isMain) {
	if (request === 'vscode') return vscode;
	return load.call(this, request, parent, isMain);
};
require('../vscode-chupa/extension.js').activate({ extensionUri: 'extension', subscriptions: [] });
tickets.resolveWebviewView({
	webview: {
		cspSource: 'test',
		asWebviewUri: uri => uri,
		onDidReceiveMessage: handler => { receive = handler; },
		postMessage: message => {
			if (message.type === 'error') {
				console.log(JSON.stringify(message.message));
				process.exit(0);
			}
		},
	},
	onDidChangeVisibility() {},
});
receive({ type: 'ready' });
