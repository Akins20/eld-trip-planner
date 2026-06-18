import PropTypes from 'prop-types';
import { useId, useState } from 'react';

import './Tooltip.css';

/** A small accessible tooltip shown on hover or keyboard focus. */
export default function Tooltip({ label, children }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  return (
    <span
      className="tip"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
    >
      <span className="tip__anchor" tabIndex={0} aria-describedby={open ? id : undefined}>
        {children}
      </span>
      <span role="tooltip" id={id} className={`tip__bubble${open ? ' is-open' : ''}`}>
        {label}
      </span>
    </span>
  );
}

Tooltip.propTypes = {
  label: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
};
