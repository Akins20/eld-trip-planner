import PropTypes from 'prop-types';

import { GRID, GRID_COLORS, STATUS_COLORS, STATUS_ROWS } from '../constants';
import { hoursToHHMM } from '../utils/format';

const ROW_INDEX = STATUS_ROWS.reduce((map, row, i) => ({ ...map, [row.key]: i }), {});
const GRID_W = 24 * GRID.hourW;
const GRID_H = STATUS_ROWS.length * GRID.rowH;
const SVG_W = GRID.left + GRID_W + GRID.right;
const SVG_H = GRID.top + GRID_H + GRID.remarksH;

const x = (hour) => GRID.left + hour * GRID.hourW;
const rowCenter = (status) => GRID.top + ROW_INDEX[status] * GRID.rowH + GRID.rowH / 2;

function hourText(h) {
  if (h === 0 || h === 24) return 'Midnight';
  if (h === 12) return 'Noon';
  return String(h > 12 ? h - 12 : h);
}

/** Draws one FMCSA 24-hour graph grid with the duty-status line and remarks. */
export default function LogGrid({ day }) {
  const segments = day.segments || [];
  const transitions = [];
  for (let i = 1; i < segments.length; i += 1) {
    transitions.push([segments[i].start_hour, segments[i - 1].status, segments[i].status]);
  }

  return (
    <svg
      className="log-grid"
      viewBox={`0 0 ${SVG_W} ${SVG_H}`}
      role="img"
      aria-label={`Duty status grid for ${day.date}`}
      preserveAspectRatio="xMidYMid meet"
    >
      {/* 15-minute + hourly vertical lines */}
      {Array.from({ length: 24 * GRID.subTicks + 1 }, (_, k) => {
        const hour = k / GRID.subTicks;
        const isHour = k % GRID.subTicks === 0;
        return (
          <line
            key={`v${k}`}
            x1={x(hour)}
            y1={GRID.top}
            x2={x(hour)}
            y2={GRID.top + GRID_H}
            stroke={isHour ? GRID_COLORS.hourLine : GRID_COLORS.subLine}
            strokeWidth={isHour ? GRID.hourLineW : GRID.subLineW}
          />
        );
      })}

      {/* Row separators + labels + totals */}
      {STATUS_ROWS.map((row, i) => {
        const y = GRID.top + i * GRID.rowH;
        const total = day.totals[row.key] || 0;
        return (
          <g key={row.key}>
            <line
              x1={GRID.left}
              y1={y}
              x2={GRID.left + GRID_W}
              y2={y}
              stroke={GRID_COLORS.separator}
              strokeWidth={GRID.hourLineW}
            />
            <text className="log-grid__rowlabel" x={GRID.left - 8} y={y + GRID.rowH / 2}>
              {row.short}
            </text>
            <text
              className="log-grid__total tnum"
              x={GRID.left + GRID_W + GRID.right - 6}
              y={y + GRID.rowH / 2}
            >
              {hoursToHHMM(total)}
            </text>
          </g>
        );
      })}
      <line
        x1={GRID.left}
        y1={GRID.top + GRID_H}
        x2={GRID.left + GRID_W}
        y2={GRID.top + GRID_H}
        stroke={GRID_COLORS.separator}
        strokeWidth={GRID.hourLineW}
      />

      {/* Hour labels (centered on each hour line) */}
      {Array.from({ length: 25 }, (_, h) => (
        <text
          key={`h${h}`}
          className="log-grid__hour"
          x={x(h)}
          y={GRID.top - 8}
          textAnchor="middle"
        >
          {hourText(h)}
        </text>
      ))}

      {/* Duty-status line: colored horizontal runs + neutral vertical transitions */}
      {transitions.map(([hour, from, to], i) => (
        <line
          key={`t${i}`}
          x1={x(hour)}
          y1={rowCenter(from)}
          x2={x(hour)}
          y2={rowCenter(to)}
          stroke={GRID_COLORS.transition}
          strokeWidth={GRID.transitionW}
        />
      ))}
      {segments.map((seg, i) => {
        const len = Math.max(1, (seg.end_hour - seg.start_hour) * GRID.hourW);
        return (
          <line
            key={`s${i}`}
            className="log-grid__run"
            x1={x(seg.start_hour)}
            y1={rowCenter(seg.status)}
            x2={x(seg.end_hour)}
            y2={rowCenter(seg.status)}
            stroke={STATUS_COLORS[seg.status]}
            strokeWidth={GRID.dutyLineW}
            strokeLinecap="round"
            style={{ '--len': len, strokeDasharray: len, animationDelay: `${i * 65}ms` }}
          />
        );
      })}

      <RemarksBand remarks={day.remarks || []} />
    </svg>
  );
}

LogGrid.propTypes = { day: PropTypes.object.isRequired };

function RemarksBand({ remarks }) {
  const baseY = GRID.top + GRID_H;
  return (
    <g>
      <text className="log-grid__rowlabel" x={GRID.left - 8} y={baseY + 14}>
        Remarks
      </text>
      {remarks.map((r, i) => {
        const px = x(r.hour);
        const ty = baseY + GRID.remarkOffset;
        return (
          <g key={`r${i}`}>
            <line
              x1={px}
              y1={baseY}
              x2={px}
              y2={baseY + GRID.tickLen}
              stroke={GRID_COLORS.remarkTick}
              strokeWidth={GRID.hourLineW}
            />
            <text className="log-grid__remark" x={px} y={ty} transform={`rotate(-55 ${px} ${ty})`}>
              {r.location}
            </text>
          </g>
        );
      })}
    </g>
  );
}

RemarksBand.propTypes = { remarks: PropTypes.array.isRequired };
