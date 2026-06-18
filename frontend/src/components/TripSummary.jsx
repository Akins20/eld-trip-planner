import PropTypes from 'prop-types';

import { STOP_META } from '../constants';
import { useCountUp } from '../hooks/useCountUp';
import { formatMiles } from '../utils/format';
import Tooltip from './Tooltip';
import './TripSummary.css';

export default function TripSummary({ plan }) {
  const s = plan.summary;
  const g = plan.geocoded;
  const legs = plan.route.legs;
  const hours = (n) => `${n.toFixed(1)} h`;

  const metrics = [
    {
      label: 'Distance',
      value: s.total_distance_miles,
      decimals: 0,
      format: (n) => `${Math.round(n).toLocaleString()} mi`,
      tip: 'Total driving distance for the whole trip.',
    },
    {
      label: 'Drive time',
      value: s.total_drive_hours,
      decimals: 1,
      format: hours,
      tip: 'Hours behind the wheel at the modeled average truck speed.',
    },
    {
      label: 'On-duty total',
      value: s.total_on_duty_hours,
      decimals: 1,
      format: hours,
      tip: 'Driving plus on-duty-not-driving time (pickup, dropoff, fueling).',
    },
    {
      label: 'Trip span',
      value: s.num_days,
      decimals: 0,
      format: (n) => `${Math.round(n)} ${Math.round(n) === 1 ? 'day' : 'days'}`,
      tip: 'Calendar days the trip covers. One ELD log sheet per day.',
    },
    {
      label: 'Fuel / breaks / rests',
      static: `${s.num_fuel_stops} / ${s.num_breaks} / ${s.num_rests}`,
      tip: 'Fuel stops, 30-minute breaks, and 10-hour rests inserted to stay compliant.',
    },
    {
      label: 'Cycle left',
      value: s.cycle_hours_remaining_end,
      decimals: 1,
      format: hours,
      tip: 'Hours left in the 70-hour / 8-day cycle when the trip ends.',
    },
  ];

  return (
    <section className="summary" aria-label="Trip summary">
      <div className="summary__route reveal">
        <Node kind="start" label={g.current.label} />
        <Leg miles={legs[0] && legs[0].distance_miles} />
        <Node kind="pickup" label={g.pickup.label} />
        <Leg miles={legs[1] && legs[1].distance_miles} />
        <Node kind="dropoff" label={g.dropoff.label} />
      </div>

      <div className="summary__metrics">
        {metrics.map((m, i) => (
          <div className="metric reveal" key={m.label} style={{ animationDelay: `${i * 60}ms` }}>
            {m.static ? (
              <span className="metric__value tnum">{m.static}</span>
            ) : (
              <CountMetric value={m.value} decimals={m.decimals} format={m.format} />
            )}
            <Tooltip label={m.tip}>
              <span className="metric__label">{m.label}</span>
            </Tooltip>
          </div>
        ))}
      </div>

      {s.num_restarts > 0 && (
        <p className="summary__note">
          Includes {s.num_restarts}x 34-hour restart. The 70-hour cycle was exhausted en route.
        </p>
      )}
    </section>
  );
}

TripSummary.propTypes = { plan: PropTypes.object.isRequired };

function CountMetric({ value, decimals, format }) {
  const n = useCountUp(value, { decimals });
  return <span className="metric__value tnum">{format(n)}</span>;
}

CountMetric.propTypes = {
  value: PropTypes.number.isRequired,
  decimals: PropTypes.number.isRequired,
  format: PropTypes.func.isRequired,
};

function Node({ kind, label }) {
  const meta = STOP_META[kind];
  return (
    <span className="route-node">
      <span className="route-node__dot" style={{ background: meta.color }} />
      <span className="route-node__text">
        <span className="route-node__role">{meta.label}</span>
        <span className="route-node__label">{label}</span>
      </span>
    </span>
  );
}

Node.propTypes = { kind: PropTypes.string.isRequired, label: PropTypes.string.isRequired };

function Leg({ miles }) {
  return (
    <span className="route-leg" aria-hidden="true">
      <span className="route-leg__line" />
      <span className="route-leg__miles tnum">{miles != null ? formatMiles(miles) : ''}</span>
    </span>
  );
}

Leg.propTypes = { miles: PropTypes.number };
