import PropTypes from 'prop-types';
import { useEffect, useState } from 'react';

import './LoadingState.css';

const MESSAGES = [
  'Geocoding your locations',
  'Routing on a truck profile',
  'Placing fuel stops every 1,000 miles',
  'Inserting 30-minute breaks and 10-hour rests',
  'Drawing your daily log sheets',
];

export default function LoadingState() {
  const [i, setI] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setI((n) => (n + 1) % MESSAGES.length), 1500);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="loading" role="status" aria-live="polite">
      <TruckScene />
      <div className="loading__msg" key={i} aria-hidden="true">
        {MESSAGES[i]}
      </div>
      <div className="loading__bar" aria-hidden="true">
        <span />
      </div>
      <span className="sr-only">Planning your trip, this takes a few seconds.</span>
    </div>
  );
}

function TruckScene() {
  return (
    <svg
      className="loading__svg"
      width="240"
      height="92"
      viewBox="0 0 240 92"
      aria-hidden="true"
      focusable="false"
    >
      <g className="loading__speed">
        <line x1="6" y1="34" x2="30" y2="34" />
        <line x1="0" y1="46" x2="26" y2="46" />
        <line x1="8" y1="58" x2="34" y2="58" />
      </g>

      <g className="loading__truck">
        <rect x="46" y="24" width="96" height="38" rx="5" fill="var(--accent)" />
        <rect x="58" y="32" width="72" height="9" rx="2" fill="#ffffff" opacity="0.22" />
        <path d="M142 34 h22 l14 14 v14 h-36 z" fill="var(--accent-press)" />
        <rect x="164" y="37" width="13" height="11" rx="2" fill="#cfe0ff" />
        <Wheel cx="72" />
        <Wheel cx="160" />
      </g>

      <line className="loading__road" x1="0" y1="74" x2="240" y2="74" />
    </svg>
  );
}

function Wheel({ cx }) {
  const cy = 66;
  return (
    <g>
      <circle cx={cx} cy={cy} r="10" fill="#1f2937" />
      <circle cx={cx} cy={cy} r="7" fill="#374151" />
      <g className="loading__spokes">
        {[0, 60, 120, 180, 240, 300].map((deg) => (
          <line
            key={deg}
            x1={cx}
            y1={cy}
            x2={cx}
            y2={cy - 6.5}
            stroke="#cbd5e1"
            strokeWidth="1.3"
            strokeLinecap="round"
            transform={`rotate(${deg} ${cx} ${cy})`}
          />
        ))}
        <circle cx={cx} cy={cy - 6.5} r="1.5" fill="#facc15" />
        <circle cx={cx} cy={cy} r="2.4" fill="#e5e7eb" />
      </g>
    </g>
  );
}

Wheel.propTypes = { cx: PropTypes.number.isRequired };
