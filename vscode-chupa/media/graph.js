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

function renderGraph(graph, dotColor, colors) {
	const svg = document.createElementNS(SVG_NS, 'svg');
	svg.classList.add('graph');
	for (const segment of graph.segments) {
		const color = colors[segment.section];
		const from = segment.from;
		const to = segment.to;
		if (segment.kind === 'straight') {
			svg.append(drawVerticalLine(SWIMLANE_WIDTH * (segment.lane + 1), 0, SWIMLANE_HEIGHT, color));
		} else if (segment.kind === 'down') {
			svg.append(drawVerticalLine(SWIMLANE_WIDTH * (segment.lane + 1), SWIMLANE_HEIGHT / 2, SWIMLANE_HEIGHT, color));
		} else if (segment.kind === 'top') {
			svg.append(drawVerticalLine(SWIMLANE_WIDTH * (segment.lane + 1), 0, SWIMLANE_HEIGHT / 2, color));
		} else {
			const path = createPath(color);
			if (segment.kind === 'into') {
				path.setAttribute('d', [
					`M ${SWIMLANE_WIDTH * (from + 1)} 0`,
					`A ${SWIMLANE_WIDTH} ${SWIMLANE_WIDTH} 0 0 1 ${SWIMLANE_WIDTH * from} ${SWIMLANE_WIDTH}`,
					`H ${SWIMLANE_WIDTH * (to + 1)}`,
				].join(' '));
			} else if (segment.kind === 'shift') {
				path.setAttribute('d', [
					`M ${SWIMLANE_WIDTH * (from + 1)} 0`,
					'V 6',
					`A ${SWIMLANE_CURVE_RADIUS} ${SWIMLANE_CURVE_RADIUS} 0 0 1 ${(SWIMLANE_WIDTH * (from + 1)) - SWIMLANE_CURVE_RADIUS} ${SWIMLANE_HEIGHT / 2}`,
					`H ${(SWIMLANE_WIDTH * (to + 1)) + SWIMLANE_CURVE_RADIUS}`,
					`A ${SWIMLANE_CURVE_RADIUS} ${SWIMLANE_CURVE_RADIUS} 0 0 0 ${SWIMLANE_WIDTH * (to + 1)} ${(SWIMLANE_HEIGHT / 2) + SWIMLANE_CURVE_RADIUS}`,
					`V ${SWIMLANE_HEIGHT}`,
				].join(' '));
			} else if (segment.kind === 'branch') {
				path.setAttribute('d', [
					`M ${SWIMLANE_WIDTH * to} ${SWIMLANE_HEIGHT / 2}`,
					`A ${SWIMLANE_WIDTH} ${SWIMLANE_WIDTH} 0 0 1 ${SWIMLANE_WIDTH * (to + 1)} ${SWIMLANE_HEIGHT}`,
					`M ${SWIMLANE_WIDTH * to} ${SWIMLANE_HEIGHT / 2}`,
					`H ${SWIMLANE_WIDTH * (from + 1)} `,
				].join(' '));
			} else if (segment.kind === 'join') {
				path.setAttribute('d', [
					`M ${SWIMLANE_WIDTH * (from + 1)} ${SWIMLANE_HEIGHT / 2}`,
					`H ${(SWIMLANE_WIDTH * (to + 1)) + SWIMLANE_CURVE_RADIUS}`,
					`A ${SWIMLANE_CURVE_RADIUS} ${SWIMLANE_CURVE_RADIUS} 0 0 0 ${SWIMLANE_WIDTH * (to + 1)} ${(SWIMLANE_HEIGHT / 2) + SWIMLANE_CURVE_RADIUS}`,
					`V ${SWIMLANE_HEIGHT}`,
				].join(' '));
			}
			svg.append(path);
		}
	}

	if (graph.dot === 'head') {
		svg.append(drawCircle(graph.circle, CIRCLE_RADIUS + 3, CIRCLE_STROKE_WIDTH, dotColor));
		svg.append(drawCircle(graph.circle, CIRCLE_STROKE_WIDTH, CIRCLE_RADIUS));
	} else if (graph.dot === 'merge') {
		svg.append(drawCircle(graph.circle, CIRCLE_RADIUS + 2, CIRCLE_STROKE_WIDTH, dotColor));
		svg.append(drawCircle(graph.circle, CIRCLE_RADIUS - 1, CIRCLE_STROKE_WIDTH, dotColor));
	} else {
		svg.append(drawCircle(graph.circle, CIRCLE_RADIUS + 1, CIRCLE_STROKE_WIDTH, dotColor));
	}

	svg.style.height = `${SWIMLANE_HEIGHT}px`;
	svg.style.width = `${SWIMLANE_WIDTH * graph.width}px`;
	return svg;
}
