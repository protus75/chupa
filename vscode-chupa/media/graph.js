// Row SVG drawing, ported from VS Code's src/vs/workbench/contrib/scm/browser/scmHistory.ts
// (Copyright (c) Microsoft Corporation, MIT License). Kept close to the original so the graph draws like the SCM view;
// dropped: references, incoming/outgoing-change nodes, hover rendering.
'use strict';

const SWIMLANE_HEIGHT = 22;
const SWIMLANE_WIDTH = 11;
const SWIMLANE_CURVE_RADIUS = 5;
const CIRCLE_RADIUS = 4;
const CIRCLE_STROKE_WIDTH = 2;
const SVG_NS = 'http://www.w3.org/2000/svg';

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

function renderGraph(graph, stem, dotColor, colors) {
	const svg = document.createElementNS(SVG_NS, 'svg');
	svg.classList.add('graph');
	const { lanesIn: inputSwimlanes, lanesOut: outputSwimlanes } = graph;
	const inputIndex = inputSwimlanes.findIndex(node => node.id === stem);
	const circleIndex = inputIndex !== -1 ? inputIndex : inputSwimlanes.length;
	const laneColor = circleIndex < outputSwimlanes.length ? colors[outputSwimlanes[circleIndex].section] :
		circleIndex < inputSwimlanes.length ? colors[inputSwimlanes[circleIndex].section] : dotColor;
	const circleColor = dotColor ?? laneColor;

	let outputSwimlaneIndex = 0;
	for (let index = 0; index < inputSwimlanes.length; index++) {
		const color = colors[inputSwimlanes[index].section];
		if (inputSwimlanes[index].id === null) {
			continue; // a gap held open by the row above: nothing to draw, and it has no output slot
		}
		if (inputSwimlanes[index].id === stem) {
			if (index !== circleIndex) {
				const path = createPath(color);
				path.setAttribute('d', [
					`M ${SWIMLANE_WIDTH * (index + 1)} 0`,
					`A ${SWIMLANE_WIDTH} ${SWIMLANE_WIDTH} 0 0 1 ${SWIMLANE_WIDTH * index} ${SWIMLANE_WIDTH}`,
					`H ${SWIMLANE_WIDTH * (circleIndex + 1)}`,
				].join(' '));
				svg.append(path);
			}
			// Each lane into the node fills one output slot: its first parent or a held-open gap.
			outputSwimlaneIndex++;
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

	// layout() places every parent edge in parentLanes: straight down, a branch to the right, or a join to the left.
	const { parentLanes } = graph;
	for (const laneIndex of parentLanes) {
		const color = colors[outputSwimlanes[laneIndex].section];
		if (laneIndex === circleIndex) {
			svg.append(drawVerticalLine(SWIMLANE_WIDTH * (circleIndex + 1), SWIMLANE_HEIGHT / 2, SWIMLANE_HEIGHT, laneColor));
		} else if (laneIndex > circleIndex) {
			const path = createPath(color);
			path.setAttribute('d', [
				`M ${SWIMLANE_WIDTH * laneIndex} ${SWIMLANE_HEIGHT / 2}`,
				`A ${SWIMLANE_WIDTH} ${SWIMLANE_WIDTH} 0 0 1 ${SWIMLANE_WIDTH * (laneIndex + 1)} ${SWIMLANE_HEIGHT}`,
				`M ${SWIMLANE_WIDTH * laneIndex} ${SWIMLANE_HEIGHT / 2}`,
				`H ${SWIMLANE_WIDTH * (circleIndex + 1)} `,
			].join(' '));
			svg.append(path);
		} else {
			const path = createPath(color);
			path.setAttribute('d', [
				`M ${SWIMLANE_WIDTH * (circleIndex + 1)} ${SWIMLANE_HEIGHT / 2}`,
				`H ${(SWIMLANE_WIDTH * (laneIndex + 1)) + SWIMLANE_CURVE_RADIUS}`,
				`A ${SWIMLANE_CURVE_RADIUS} ${SWIMLANE_CURVE_RADIUS} 0 0 0 ${SWIMLANE_WIDTH * (laneIndex + 1)} ${(SWIMLANE_HEIGHT / 2) + SWIMLANE_CURVE_RADIUS}`,
				`V ${SWIMLANE_HEIGHT}`,
			].join(' '));
			svg.append(path);
		}
	}

	if (inputIndex !== -1) {
		svg.append(drawVerticalLine(SWIMLANE_WIDTH * (circleIndex + 1), 0, SWIMLANE_HEIGHT / 2, colors[inputSwimlanes[inputIndex].section]));
	}

	if (graph.kind === 'head') {
		svg.append(drawCircle(circleIndex, CIRCLE_RADIUS + 3, CIRCLE_STROKE_WIDTH, circleColor));
		svg.append(drawCircle(circleIndex, CIRCLE_STROKE_WIDTH, CIRCLE_RADIUS));
	} else if (graph.parents.length > 1) {
		svg.append(drawCircle(circleIndex, CIRCLE_RADIUS + 2, CIRCLE_STROKE_WIDTH, circleColor));
		svg.append(drawCircle(circleIndex, CIRCLE_RADIUS - 1, CIRCLE_STROKE_WIDTH, circleColor));
	} else {
		svg.append(drawCircle(circleIndex, CIRCLE_RADIUS + 1, CIRCLE_STROKE_WIDTH, circleColor));
	}

	svg.style.height = `${SWIMLANE_HEIGHT}px`;
	svg.style.width = `${SWIMLANE_WIDTH * (Math.max(inputSwimlanes.length, outputSwimlanes.length, circleIndex + 1) + 1)}px`;
	return svg;
}
