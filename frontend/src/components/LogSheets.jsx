import PropTypes from 'prop-types';
import { useState } from 'react';

import LogSheet from './LogSheet';
import './LogSheets.css';

function shortDate(iso) {
  const d = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export default function LogSheets({ plan }) {
  const days = plan.days || [];
  const [active, setActive] = useState(0);
  if (days.length === 0) return null;
  const current = days[Math.min(active, days.length - 1)];

  return (
    <section className="logs" id="logs" aria-label="Daily log sheets">
      <div className="section-head">
        <h2>Daily log sheets</h2>
        <p>
          {days.length} {days.length === 1 ? 'day' : 'days'}, every grid totals exactly 24 hours.
        </p>
      </div>

      {days.length > 1 && (
        <div className="day-tabs" role="tablist" aria-label="Choose a day">
          {days.map((d, i) => (
            <button
              key={d.day_number}
              type="button"
              role="tab"
              aria-selected={i === active}
              className={`day-tab${i === active ? ' is-active' : ''}`}
              onClick={() => setActive(i)}
            >
              <span>Day {d.day_number}</span>
              <span className="day-tab__date">{shortDate(d.date)}</span>
            </button>
          ))}
        </div>
      )}

      <div className="logs__panel" key={active}>
        <LogSheet day={current} plan={plan} />
      </div>
    </section>
  );
}

LogSheets.propTypes = { plan: PropTypes.object.isRequired };
