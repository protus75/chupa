'use strict';

const path = require('path');
const Module = require('module');
const root = path.resolve(__dirname, '..');
const disposable = { dispose() {} };
let steps;
const vscode = {
	Uri: { file: fsPath => ({ fsPath }) },
	workspace: {
		workspaceFolders: [{ uri: { fsPath: root } }],
		getConfiguration: () => ({ get: key => key === 'command' ? ['true'] : 0 }),
		onDidChangeConfiguration: () => disposable,
	},
	window: {
		createTreeView: (id, options) => {
			if (id === 'chupa.steps') steps = options.treeDataProvider;
			return { ...disposable, onDidChangeVisibility() {} };
		},
		registerWebviewViewProvider: () => disposable,
	},
	commands: { registerCommand: () => disposable },
	EventEmitter: class { constructor() { this.event = () => {}; } },
	TreeItem: class {},
	ThemeIcon: class { constructor(id) { this.id = id; } },
	ThemeColor: class {},
};
const load = Module._load;
Module._load = function (request, parent, isMain) {
	if (request === 'vscode') return vscode;
	if (request === 'child_process') return { execFile() {} };
	return load.call(this, request, parent, isMain);
};
require('../vscode-chupa/extension.js').activate({ extensionUri: {}, subscriptions: [] });
const icons = {};
for (const kind of JSON.parse(process.argv[2])) {
	try { icons[kind] = steps.getTreeItem({ kind }).iconPath.id; }
	catch { icons[kind] = null; }
}
console.log(JSON.stringify(icons));
