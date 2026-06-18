import PropTypes from 'prop-types';

import { DEFAULT_STOP_COLOR, STOP_META } from '../constants';
import { formatHours } from '../utils/format';
import './StopsList.css';

export default function StopsList({ stops }) {
  if (!stops || stops.length === 0) return null;

  return (
    <section className="stops" aria-label="Stops and rests">
      <div className="section-head">
        <h2>Timeline</h2>
        <p>Every duty change, in order of the trip.</p>
      </div>

      <ol className="timeline">
        {stops.map((s, i) => {
          const meta = STOP_META[s.kind] || { label: s.kind, color: DEFAULT_STOP_COLOR };
          return (
            <li className="timeline__item" key={`${s.kind}-${s.start_min}-${i}`}>
              <span className="timeline__dot" style={{ background: meta.color }} />
              <div className="timeline__body">
                <div className="timeline__head">
                  <span className="timeline__kind">{meta.label}</span>
                  {s.duration_hours > 0 && (
                    <span className="timeline__dur tnum">{formatHours(s.duration_hours)}</span>
                  )}
                </div>
                <div className="timeline__label">{s.label}</div>
                <div className="timeline__meta tnum">
                  {s.start_label}
                  {s.mile_marker != null ? ` · mile ${s.mile_marker.toLocaleString()}` : ''}
                </div>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

StopsList.propTypes = { stops: PropTypes.array };
