import PropTypes from 'prop-types';
import { useEffect, useState } from 'react';

import { EXAMPLE_TRIP } from '../constants';
import './TripForm.css';

const LOCATION_FIELDS = [
  { name: 'current_location', label: 'Current location', placeholder: 'Chicago, IL' },
  { name: 'pickup_location', label: 'Pickup', placeholder: 'Dallas, TX' },
  { name: 'dropoff_location', label: 'Dropoff', placeholder: 'Los Angeles, CA' },
];

const EMPTY = {
  current_location: '',
  pickup_location: '',
  dropoff_location: '',
  current_cycle_used: '',
  start_datetime: '',
};

export default function TripForm({ onSubmit, loading, prefill }) {
  const [values, setValues] = useState(EMPTY);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (prefill) {
      setValues({ ...EMPTY, ...prefill });
      setErrors({});
    }
  }, [prefill]);

  function set(name, value) {
    setValues((v) => ({ ...v, [name]: value }));
    if (errors[name]) setErrors((e) => ({ ...e, [name]: undefined }));
  }

  function validate() {
    const e = {};
    LOCATION_FIELDS.forEach(({ name, label }) => {
      if (!values[name].trim()) e[name] = `${label} is required`;
    });
    const cycle = parseFloat(values.current_cycle_used);
    if (values.current_cycle_used === '' || Number.isNaN(cycle)) {
      e.current_cycle_used = 'Enter hours (0-70)';
    } else if (cycle < 0 || cycle > 70) {
      e.current_cycle_used = 'Must be between 0 and 70';
    }
    setErrors(e);
    return e;
  }

  function handleSubmit(ev) {
    ev.preventDefault();
    const e = validate();
    const firstInvalid = Object.keys(e)[0];
    if (firstInvalid) {
      document.getElementById(firstInvalid)?.focus();
      return;
    }
    const payload = {
      current_location: values.current_location.trim(),
      pickup_location: values.pickup_location.trim(),
      dropoff_location: values.dropoff_location.trim(),
      current_cycle_used: parseFloat(values.current_cycle_used),
    };
    if (values.start_datetime) payload.start_datetime = values.start_datetime;
    onSubmit(payload);
  }

  return (
    <form className="trip-form" onSubmit={handleSubmit} noValidate>
      <div className="trip-form__grid" data-tour="locations">
        {LOCATION_FIELDS.map((f) => (
          <Field
            key={f.name}
            {...f}
            value={values[f.name]}
            error={errors[f.name]}
            onChange={(val) => set(f.name, val)}
          />
        ))}
      </div>
      <div className="trip-form__row">
        <Field
          name="current_cycle_used"
          label="Cycle used (hrs)"
          type="number"
          placeholder="8"
          min="0"
          max="70"
          step="0.25"
          tour="cycle"
          value={values.current_cycle_used}
          error={errors.current_cycle_used}
          hint="On-duty hours used in the 70/8 cycle"
          onChange={(val) => set('current_cycle_used', val)}
        />
        <Field
          name="start_datetime"
          label="Start (optional)"
          type="datetime-local"
          value={values.start_datetime}
          onChange={(val) => set('start_datetime', val)}
        />
        <div className="trip-form__actions">
          <button
            type="button"
            className="btn btn--ghost"
            data-tour="example"
            onClick={() => {
              setValues({ ...EMPTY, ...EXAMPLE_TRIP });
              setErrors({});
            }}
            disabled={loading}
          >
            Try an example
          </button>
          <button type="submit" className="btn btn--primary" data-tour="plan" disabled={loading}>
            {loading ? 'Planning...' : 'Plan trip'}
          </button>
        </div>
      </div>
    </form>
  );
}

TripForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  loading: PropTypes.bool,
  prefill: PropTypes.object,
};

function Field({ name, label, value, onChange, error, hint, type = 'text', tour, ...rest }) {
  const msgId = `${name}-msg`;
  const hasMsg = Boolean(error || hint);
  return (
    <label className={`field${error ? ' field--error' : ''}`} htmlFor={name} data-tour={tour}>
      <span className="field__label">{label}</span>
      <input
        id={name}
        name={name}
        type={type}
        className="field__input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-invalid={Boolean(error)}
        aria-describedby={hasMsg ? msgId : undefined}
        autoComplete="off"
        {...rest}
      />
      {error ? (
        <span id={msgId} role="alert" className="field__msg field__msg--error">
          {error}
        </span>
      ) : hint ? (
        <span id={msgId} className="field__msg">
          {hint}
        </span>
      ) : null}
    </label>
  );
}

Field.propTypes = {
  name: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  error: PropTypes.string,
  hint: PropTypes.string,
  type: PropTypes.string,
  tour: PropTypes.string,
  placeholder: PropTypes.string,
  min: PropTypes.string,
  max: PropTypes.string,
  step: PropTypes.string,
};
