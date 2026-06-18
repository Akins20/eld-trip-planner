import PropTypes from 'prop-types';
import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';

import './Tour.css';

const PAD = 8;
const CARD_W = 360;
const EDGE_MARGIN = 32;
const VIEWPORT_MARGIN = 16;
const BELOW_THRESHOLD = 220;
const CARD_GAP = 14;

function clampLeft(left) {
  const w = Math.min(CARD_W, window.innerWidth - EDGE_MARGIN);
  return Math.max(VIEWPORT_MARGIN, Math.min(left, window.innerWidth - w - VIEWPORT_MARGIN));
}

function rectFor(target) {
  if (!target) return null;
  const el = document.querySelector(target);
  if (!el) return null;
  const r = el.getBoundingClientRect();
  return {
    top: r.top - PAD,
    left: r.left - PAD,
    width: r.width + PAD * 2,
    height: r.height + PAD * 2,
  };
}

/** A skippable, keyboard-driven spotlight tour with focus management. */
export default function Tour({ steps, open, onClose, onAction }) {
  const [index, setIndex] = useState(0);
  const [rect, setRect] = useState(null);
  const cardRef = useRef(null);
  const openerRef = useRef(null);
  const wasOpen = useRef(false);

  useEffect(() => {
    if (open) {
      setIndex(0);
      openerRef.current = document.activeElement;
    }
  }, [open]);

  // Restore focus to whatever opened the tour, when it closes.
  useEffect(() => {
    if (wasOpen.current && !open && openerRef.current && openerRef.current.focus) {
      openerRef.current.focus();
    }
    wasOpen.current = open;
  }, [open]);

  const step = open ? steps[index] : null;
  const target = step ? step.target : null;

  // Scroll the target into view ONCE per step, then measure.
  useLayoutEffect(() => {
    if (!open) return undefined;
    if (target) {
      const el = document.querySelector(target);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    const id = requestAnimationFrame(() => setRect(rectFor(target)));
    return () => cancelAnimationFrame(id);
  }, [open, target]);

  // Re-read the rect (no scrolling) as the page scrolls or resizes.
  useEffect(() => {
    if (!open) return undefined;
    const reposition = () => setRect(rectFor(target));
    window.addEventListener('resize', reposition);
    window.addEventListener('scroll', reposition, true);
    return () => {
      window.removeEventListener('resize', reposition);
      window.removeEventListener('scroll', reposition, true);
    };
  }, [open, target]);

  // Move focus into the dialog on open and on each step.
  useEffect(() => {
    if (open && cardRef.current) cardRef.current.focus();
  }, [open, index]);

  const next = useCallback(() => {
    setIndex((i) => {
      if (i < steps.length - 1) return i + 1;
      onClose();
      return i;
    });
  }, [steps.length, onClose]);

  const back = useCallback(() => setIndex((i) => Math.max(0, i - 1)), []);

  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => {
      if (e.key === 'Escape') return onClose();
      if (e.key === 'ArrowRight') return next();
      if (e.key === 'ArrowLeft') return back();
      if (e.key === 'Tab' && cardRef.current) {
        const list = Array.from(
          cardRef.current.querySelectorAll('button, [href], [tabindex]:not([tabindex="-1"])')
        );
        if (list.length === 0) return undefined;
        const first = list[0];
        const last = list[list.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
      return undefined;
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, next, back, onClose]);

  if (!open || !step) return null;

  const centered = !rect;
  let cardStyle;
  if (!centered) {
    const placeBelow = window.innerHeight - (rect.top + rect.height) > BELOW_THRESHOLD;
    cardStyle = placeBelow
      ? { top: rect.top + rect.height + CARD_GAP, left: clampLeft(rect.left) }
      : { bottom: window.innerHeight - rect.top + CARD_GAP, left: clampLeft(rect.left) };
  }
  const isLast = index === steps.length - 1;

  return (
    <div className="tour" role="dialog" aria-modal="true" aria-label="Guided tour">
      <div className={`tour__layer${centered ? ' tour__layer--dim' : ''}`} />
      {!centered && (
        <div
          className="tour__spot"
          style={{ top: rect.top, left: rect.left, width: rect.width, height: rect.height }}
        />
      )}
      <div
        className={`tour__card${centered ? ' tour__card--center' : ''}`}
        style={cardStyle}
        ref={cardRef}
        tabIndex={-1}
      >
        <button className="tour__skip" type="button" onClick={onClose}>
          Skip tour
        </button>
        <p className="tour__count">
          Step {index + 1} of {steps.length}
        </p>
        <h3 className="tour__title">{step.title}</h3>
        <p className="tour__body">{step.body}</p>
        <div className="tour__dots" aria-hidden="true">
          {steps.map((s, i) => (
            <span key={s.title} className={i === index ? 'is-on' : ''} />
          ))}
        </div>
        <div className="tour__actions">
          {index > 0 ? (
            <button className="btn btn--ghost" type="button" onClick={back}>
              Back
            </button>
          ) : (
            <span />
          )}
          {step.cta ? (
            <button
              className="btn btn--primary"
              type="button"
              onClick={() => {
                onClose();
                if (onAction) onAction();
              }}
            >
              {step.cta}
            </button>
          ) : (
            <button className="btn btn--primary" type="button" onClick={next}>
              {isLast ? 'Done' : 'Next'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

Tour.propTypes = {
  steps: PropTypes.array.isRequired,
  open: PropTypes.bool,
  onClose: PropTypes.func.isRequired,
  onAction: PropTypes.func,
};
