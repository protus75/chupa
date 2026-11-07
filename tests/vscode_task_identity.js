'use strict';

const path = require('path');
const Module = require('module');
const root = path.resolve(__dirname, '..');
const definitions = [];
const handlers = {};
const disposable = { dispose() {} };
const watcher = { ...disposable, onDidChange() {}, onDidCreate() {}, onDidDelete() {} };
const vscode = {
	Uri: { file: fsPath => ({ fsPath }) },
	workspace: {
		workspaceFolders: [{ uri: { fsPath: root } }],
		getConfiguration: () => ({ get: key => key === 'command' ? ['true'] : 0 }),
		getWorkspaceFolder: () => ({ uri: { fsPath: root } }),
		createFileSystemWatcher: () => watcher,
		onDidChangeConfiguration: () => disposable,
	},
	window: {
		createTreeView: () => ({ ...disposable, onDidChangeVisibility() {} }),
		registerWebviewViewProvider: () => disposable,
	},
	commands: { registerCommand: (name, handler) => { handlers[name] = handler; return disposable; } },
	EventEmitter: class { constructor() { this.event = () => {}; } },
	RelativePattern: class {},
	Task: class { constructor(definition) { definitions.push(definition); } },
	ProcessExecution: class {},
	tasks: { executeTask() {} },
};
const load = Module._load;
Module._load = function (request, parent, isMain) {
	if (request === 'vscode') return vscode;
	if (request === 'child_process') return { execFile() {} };
	return load.call(this, request, parent, isMain);
};
require('../vscode-chupa/extension.js').activate({ extensionUri: {}, subscriptions: [] });
const context = { chupaStem: 'x' };
handlers['chupa.ticket.review'](context);
handlers['chupa.ticket.lint'](context);
handlers['chupa.ticket.review'](context);
console.log(JSON.stringify(definitions));
