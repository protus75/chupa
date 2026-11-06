// Swimlane layout and row SVG, ported from VS Code's src/vs/workbench/contrib/scm/browser/scmHistory.ts
// (Copyright (c) Microsoft Corporation, MIT License). Kept close to the original so the graph draws like the SCM view;
// dropped: references, incoming/outgoing-change nodes, hover rendering.
'use strict';

const SWIMLANE_HEIGHT = 22;
const SWIMLANE_WIDTH = 11;
const SWIMLANE_CURVE_RADIUS = 5;
const CIRCLE_RADIUS = 4;
const CIRCLE_STROKE_WIDTH = 2;
const SVG_NS = 'http://www.w3.org/2000/svg';

const LANE_COLORS = [1, 2, 3, 4, 5].map(i => `var(--vscode-scmGraph-foreground${i}, ${['#FFB000', '#DC267F', '#994F00', '#40B0A6', '#B66DFF'][i - 1]})`);

function createPath(color, strokeWidth = 1) {
	const path = document.createElementNS(SVG_NS, 'path');
	path.setAttribute('fill', 'none');
	path.setAttribute('stroke-width', `${strokeWidth}px`);
	path.setAttribute('stroke-linecap', 'round');
	path.style.stroke = color;
	return path;
}

function drawCircle(index, radius, strokeWidth, color) {
	const circle = document.createElementNS(SVG_NS, 'circle');
	circle.setAttribute('cx', `${SWIMLANE_WIDTH * (index + 1)}`);
	circle.setAttribute('cy', `${SWIMLANE_WIDTH}`);
	circle.setAttribute('r', `${radius}`);
	circle.style.strokeWidth = `${strokeWidth}px`;
	if (color) {
		circle.style.fill = color;
	}
	return circle;
}

function drawVerticalLine(x1, y1, y2, color, strokeWidth = 1) {
	const path = createPath(color, strokeWidth);
	path.setAttribute('d', `M ${x1} ${y1} V ${y2}`);
	return path;
}

function findLastIndex(nodes, id) {
	for (let i = nodes.length - 1; i >= 0; i--) {
		if (nodes[i].id === id) {
			return i;
		}
	}
	return -1;
}

// items: [{ id, parentIds, kind?, laneColor?, branchColor? }] top row first; a parent must appear below its child to be joined.
// laneColor colors the first-parent lane, branchColor the other parents' lanes; unset falls back to the SCM rotation.
function toViewModels(items) {
	let colorIndex = -1;
	const viewModels = [];
	for (const item of items) {
		const inputSwimlanes = (viewModels.at(-1)?.outputSwimlanes ?? []).map(n => ({ ...n }));
		const outputSwimlanes = [];
		let firstParentAdded = false;
		// Unlike git history, a parentless row is not the root: lanes for other rows still pass through it.
		for (const node of inputSwimlanes) {
			if (node.id === item.id) {
				if (!firstParentAdded && item.parentIds.length > 0) {
					outputSwimlanes.push({ id: item.parentIds[0], color: item.laneColor ?? node.color });
					firstParentAdded = true;
				}
				continue;
			}
			outputSwimlanes.push({ ...node });
		}
		for (let i = firstParentAdded ? 1 : 0; i < item.parentIds.length; i++) {
			let color = i === 0 ? item.laneColor : item.branchColor;
			if (!color) {
				colorIndex = (colorIndex + 1) % LANE_COLORS.length;
				color = LANE_COLORS[colorIndex];
			}
			outputSwimlanes.push({ id: item.parentIds[i], color });
		}
		viewModels.push({ item, kind: item.kind ?? 'node', inputSwimlanes, outputSwimlanes });
	}
	return viewModels;
}

// dotColor overrides the node fill so the dot carries the ticket's status color; lanes keep the SCM palette.
function renderGraph(vm, dotColor) {
	const svg = document.createElementNS(SVG_NS, 'svg');
	svg.classList.add('graph');
	const { item, inputSwimlanes, outputSwimlanes } = vm;
	const inputIndex = inputSwimlanes.findIndex(node => node.id === item.id);
	const circleIndex = inputIndex !== -1 ? inputIndex : inputSwimlanes.length;
	const laneColor = circleIndex < outputSwimlanes.length ? outputSwimlanes[circleIndex].color :
		circleIndex < inputSwimlanes.length ? inputSwimlanes[circleIndex].color : dotColor;
	const circleColor = dotColor ?? laneColor;

	let outputSwimlaneIndex = 0;
	for (let index = 0; index < inputSwimlanes.length; index++) {
		const color = inputSwimlanes[index].color;
		if (inputSwimlanes[index].id === item.id) {
			if (index !== circleIndex) {
				const path = createPath(color);
				path.setAttribute('d', [
					`M ${SWIMLANE_WIDTH * (index + 1)} 0`,
					`A ${SWIMLANE_WIDTH} ${SWIMLANE_WIDTH} 0 0 1 ${SWIMLANE_WIDTH * index} ${SWIMLANE_WIDTH}`,
					`H ${SWIMLANE_WIDTH * (circleIndex + 1)}`,
				].join(' '));
				svg.append(path);
			} else {
				outputSwimlaneIndex++;
			}
		} else if (outputSwimlaneIndex < outputSwimlanes.length && inputSwimlanes[index].id === outputSwimlanes[outputSwimlaneIndex].id) {
			if (index === outputSwimlaneIndex) {
				svg.append(drawVerticalLine(SWIMLANE_WIDTH * (index + 1), 0, SWIMLANE_HEIGHT, color));
			} else {
				const path = createPath(color);
				path.setAttribute('d', [
					`M ${SWIMLANE_WIDTH * (index + 1)} 0`,
					'V 6',
					`A ${SWIMLANE_CURVE_RADIUS} ${SWIMLANE_CURVE_RADIUS} 0 0 1 ${(SWIMLANE_WIDTH * (index + 1)) - SWIMLANE_CURVE_RADIUS} ${SWIMLANE_HEIGHT / 2}`,
					`H ${(SWIMLANE_WIDTH * (outputSwimlaneIndex + 1)) + SWIMLANE_CURVE_RADIUS}`,
					`A ${SWIMLANE_CURVE_RADIUS} ${SWIMLANE_CURVE_RADIUS} 0 0 0 ${SWIMLANE_WIDTH * (outputSwimlaneIndex + 1)} ${(SWIMLANE_HEIGHT / 2) + SWIMLANE_CURVE_RADIUS}`,
					`V ${SWIMLANE_HEIGHT}`,
				].join(' '));
				svg.append(path);
			}
			outputSwimlaneIndex++;
		}
	}

	for (let i = 1; i < item.parentIds.length; i++) {
		const parentOutputIndex = findLastIndex(outputSwimlanes, item.parentIds[i]);
		if (parentOutputIndex === -1) {
			continue;
		}
		const path = createPath(outputSwimlanes[parentOutputIndex].color);
		path.setAttribute('d', [
			`M ${SWIMLANE_WIDTH * parentOutputIndex} ${SWIMLANE_HEIGHT / 2}`,
			`A ${SWIMLANE_WIDTH} ${SWIMLANE_WIDTH} 0 0 1 ${SWIMLANE_WIDTH * (parentOutputIndex + 1)} ${SWIMLANE_HEIGHT}`,
			`M ${SWIMLANE_WIDTH * parentOutputIndex} ${SWIMLANE_HEIGHT / 2}`,
			`H ${SWIMLANE_WIDTH * (circleIndex + 1)} `,
		].join(' '));
		svg.append(path);
	}

	if (inputIndex !== -1) {
		svg.append(drawVerticalLine(SWIMLANE_WIDTH * (circleIndex + 1), 0, SWIMLANE_HEIGHT / 2, inputSwimlanes[inputIndex].color));
	}
	if (item.parentIds.length > 0) {
		svg.append(drawVerticalLine(SWIMLANE_WIDTH * (circleIndex + 1), SWIMLANE_HEIGHT / 2, SWIMLANE_HEIGHT, laneColor));
	}

	if (vm.kind === 'HEAD') {
		svg.append(drawCircle(circleIndex, CIRCLE_RADIUS + 3, CIRCLE_STROKE_WIDTH, circleColor));
		svg.append(drawCircle(circleIndex, CIRCLE_STROKE_WIDTH, CIRCLE_RADIUS));
	} else if (item.parentIds.length > 1) {
		svg.append(drawCircle(circleIndex, CIRCLE_RADIUS + 2, CIRCLE_STROKE_WIDTH, circleColor));
		svg.append(drawCircle(circleIndex, CIRCLE_RADIUS - 1, CIRCLE_STROKE_WIDTH, circleColor));
	} else {
		svg.append(drawCircle(circleIndex, CIRCLE_RADIUS + 1, CIRCLE_STROKE_WIDTH, circleColor));
	}

	svg.style.height = `${SWIMLANE_HEIGHT}px`;
	svg.style.width = `${SWIMLANE_WIDTH * (Math.max(inputSwimlanes.length, outputSwimlanes.length, circleIndex + 1) + 1)}px`;
	return svg;
}
