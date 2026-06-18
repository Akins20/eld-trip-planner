// Centralized constants - no magic numbers/colors inline in components.

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// A sample cross-country trip used by "Try an example" and the guided tour.
export const EXAMPLE_TRIP = {
  current_location: 'Chicago, IL',
  pickup_location: 'Dallas, TX',
  dropoff_location: 'Los Angeles, CA',
  current_cycle_used: '8',
  start_datetime: '',
};

export const STATUS = {
  OFF: 'off_duty',
  SLEEPER: 'sleeper',
  DRIVING: 'driving',
  ON_DUTY: 'on_duty',
};

// Rows top-to-bottom on the FMCSA ELD grid (`short` is the in-grid gutter label).
export const STATUS_ROWS = [
  { key: STATUS.OFF, label: 'Off Duty', short: '1. Off' },
  { key: STATUS.SLEEPER, label: 'Sleeper Berth', short: '2. Sleeper' },
  { key: STATUS.DRIVING, label: 'Driving', short: '3. Driving' },
  { key: STATUS.ON_DUTY, label: 'On Duty (ND)', short: '4. On Duty' },
];

export const STATUS_COLORS = {
  [STATUS.OFF]: '#64748b',
  [STATUS.SLEEPER]: '#7c3aed',
  [STATUS.DRIVING]: '#2563eb',
  [STATUS.ON_DUTY]: '#f59e0b',
};

// Fallback color for an unrecognized stop kind.
export const DEFAULT_STOP_COLOR = '#2563eb';

// Map marker + stop-list styling per stop kind.
export const STOP_META = {
  start: { label: 'Departure', color: '#16a34a' },
  pickup: { label: 'Pickup', color: '#0891b2' },
  dropoff: { label: 'Dropoff', color: '#dc2626' },
  fuel: { label: 'Fuel stop', color: '#f59e0b' },
  break: { label: '30-min break', color: '#64748b' },
  rest: { label: '10-hr rest', color: '#7c3aed' },
  restart: { label: '34-hr restart', color: '#9333ea' },
};

// ELD log grid SVG geometry (a 24-hour, 4-row grid).
export const GRID = {
  left: 80, // row-label gutter
  right: 58, // totals gutter
  top: 24, // hour-label band
  rowH: 30,
  hourW: 31, // 24 * 31 = 744 px grid width
  remarksH: 104,
  subTicks: 4, // 15-minute subdivisions per hour
  dutyLineW: 3.4, // duty-status run stroke
  transitionW: 2, // vertical transition stroke
  hourLineW: 1, // hourly grid line
  subLineW: 0.6, // 15-minute grid line
  remarkOffset: 18, // remark text y offset below the grid
  tickLen: 10, // remark tick length
};

// Non-status colors used when drawing the ELD grid chrome.
export const GRID_COLORS = {
  hourLine: '#cbd2da',
  subLine: '#eef1f4',
  separator: '#cbd2da',
  transition: '#334155',
  remarkTick: '#94a3b8',
};
