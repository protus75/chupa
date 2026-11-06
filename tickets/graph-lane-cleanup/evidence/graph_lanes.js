// Lane check for graph-lane-cleanup: two dependents of one parent share its lane.
// Exits 0 when shared, 1 on the defect (a third lane for the parent opens).
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ctx = {};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(__dirname, '..', '..', 'vscode-chupa', 'media', 'graph.js'), 'utf8') + ';this.toViewModels = toViewModels;', ctx);
const vms = ctx.toViewModels([
	{ id: 'a', parentIds: ['b', 'd'] },
	{ id: 'b', parentIds: ['c', 'd'] },
	{ id: 'c', parentIds: ['d'] },
	{ id: 'd', parentIds: [] },
]);
process.exit(vms.some(m => m.outputSwimlanes.filter(n => n.id === 'd').length > 2) ? 1 : 0);
