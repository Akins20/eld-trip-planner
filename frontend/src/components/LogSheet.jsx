import PropTypes from 'prop-types';

import { STATUS_COLORS, STATUS_ROWS } from '../constants';
import { formatDate, formatMiles, hoursToHHMM } from '../utils/format';
import LogGrid from './LogGrid';
import './LogSheet.css';

export default function LogSheet({ day, plan }) {
  const total = STATUS_ROWS.reduce((sum, r) => sum + (day.totals[r.key] || 0), 0);

  return (
    <article className="sheet">
      <header className="sheet__head">
        <div>
          <p className="eyebrow">Driver&apos;s Daily Log · 24 hours</p>
          <h3 className="sheet__date">{formatDate(day.date)}</h3>
        </div>
        <dl className="sheet__facts">
          <Fact label="Day" value={`${day.day_number} of ${plan.days.length}`} />
          <Fact label="Miles today" value={formatMiles(day.miles)} />
          <Fact label="Total" value={`${hoursToHHMM(total)} h`} />
        </dl>
      </header>

      <div className="sheet__grid">
        <LogGrid day={day} />
      </div>

      <ul className="sheet__totals" aria-label="Hours by duty status">
        {STATUS_ROWS.map((r) => (
          <li key={r.key}>
            <span className="sheet__swatch" style={{ background: STATUS_COLORS[r.key] }} />
            <span className="sheet__totals-label">{r.label}</span>
            <span className="sheet__totals-val tnum">{hoursToHHMM(day.totals[r.key] || 0)}</span>
          </li>
        ))}
      </ul>
    </article>
  );
}

LogSheet.propTypes = {
  day: PropTypes.object.isRequired,
  plan: PropTypes.object.isRequired,
};

function Fact({ label, value }) {
  return (
    <div className="fact">
      <dt>{label}</dt>
      <dd className="tnum">{value}</dd>
    </div>
  );
}

Fact.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
};
