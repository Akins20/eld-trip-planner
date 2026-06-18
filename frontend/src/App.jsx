import { useEffect, useRef, useState } from 'react';

import './App.css';
import LoadingState from './components/LoadingState';
import LogSheets from './components/LogSheets';
import RouteMap from './components/RouteMap';
import StopsList from './components/StopsList';
import Tour from './components/Tour';
import TripForm from './components/TripForm';
import TripSummary from './components/TripSummary';
import { EXAMPLE_TRIP } from './constants';
import { useTripPlan } from './hooks/useTripPlan';

const TOUR_SEEN_KEY = 'eld_tour_seen_v1';

const TOUR_STEPS = [
  {
    target: null,
    title: 'Plan a trip, get the logs',
    body: 'Give this app a trip and it returns an FMCSA-compliant plan: a route with fuel stops and rest breaks, plus a drawn daily log sheet for every day. Here is the 20-second tour.',
  },
  {
    target: '[data-tour="locations"]',
    title: '1. Where is the load going?',
    body: 'Enter the current location, the pickup, and the dropoff. Use real places like "Chicago, IL" or a full street address.',
  },
  {
    target: '[data-tour="cycle"]',
    title: '2. How much cycle is left?',
    body: 'Enter the on-duty hours already used in the current 70-hour / 8-day cycle. The plan budgets the rest of the trip around whatever you have left.',
  },
  {
    target: '[data-tour="example"]',
    title: 'Not sure what to type?',
    body: 'Tap "Try an example" to drop in a sample cross-country trip you can plan right away.',
  },
  {
    target: '[data-tour="plan"]',
    title: '3. Plan the trip',
    body: 'Hit Plan trip. The form slides aside, and the route, stops, and daily logs build on the right.',
  },
  {
    target: null,
    title: 'What you get back',
    body: 'A route map with every stop, a timeline of the whole trip, and one ELD log sheet per day, each grid totaling exactly 24 hours. Want to watch it happen?',
    cta: 'Show me an example',
  },
];

export default function App() {
  const { plan, loading, error, submit, loadSample } = useTripPlan();
  const [active, setActive] = useState(false);
  const [tourOpen, setTourOpen] = useState(false);
  const [prefill, setPrefill] = useState(null);
  const mainRef = useRef(null);

  useEffect(() => {
    if (new URLSearchParams(window.location.search).has('demo')) {
      setActive(true);
      setPrefill({ ...EXAMPLE_TRIP });
      loadSample();
      return;
    }
    try {
      if (!localStorage.getItem(TOUR_SEEN_KEY)) setTourOpen(true);
    } catch {
      /* localStorage unavailable; skip auto-tour */
    }
  }, [loadSample]);

  function closeTour() {
    setTourOpen(false);
    try {
      localStorage.setItem(TOUR_SEEN_KEY, '1');
    } catch {
      /* ignore */
    }
  }

  async function handleSubmit(payload) {
    setActive(true);
    if (window.innerWidth <= 900 && mainRef.current) {
      mainRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    await submit(payload);
  }

  function runExample() {
    setActive(true);
    setPrefill({ ...EXAMPLE_TRIP });
    handleSubmit({
      current_location: EXAMPLE_TRIP.current_location,
      pickup_location: EXAMPLE_TRIP.pickup_location,
      dropoff_location: EXAMPLE_TRIP.dropoff_location,
      current_cycle_used: parseFloat(EXAMPLE_TRIP.current_cycle_used),
    });
  }

  return (
    <div className="app">
      <header className="masthead">
        <div className="container masthead__top">
          <div className="brand">
            <BrandMark />
            <span>ELD Trip Planner</span>
          </div>
          <button className="masthead__help" type="button" onClick={() => setTourOpen(true)}>
            How it works
          </button>
        </div>
      </header>

      <main className={`stage container${active ? ' stage--active' : ''}`}>
        <div className="stage__intro">
          <h1 className="stage__title">
            Plan a trip, see every stop and rest, and get the daily logs drawn for you.
          </h1>
          <p className="stage__sub">
            Property-carrying driver, 70-hour / 8-day cycle, FMCSA Hours of Service with no adverse
            conditions.
          </p>
        </div>

        <div className="workspace">
          <aside className="workspace__form">
            <TripForm onSubmit={handleSubmit} loading={loading} prefill={prefill} />
          </aside>

          <div className="workspace__main" ref={mainRef}>
            {error && (
              <div className="notice notice--error" role="alert">
                <strong>Couldn&apos;t plan the trip.</strong> {error}
              </div>
            )}

            {loading && <LoadingState />}

            {plan && !loading && (
              <section className="results" aria-label="Trip results">
                <TripSummary plan={plan} />
                <div className="results__split">
                  <RouteMap plan={plan} />
                  <StopsList stops={plan.stops} />
                </div>
                <LogSheets plan={plan} />
              </section>
            )}
          </div>
        </div>
      </main>

      <Tour steps={TOUR_STEPS} open={tourOpen} onClose={closeTour} onAction={runExample} />
    </div>
  );
}

function BrandMark() {
  return (
    <svg
      className="brand__mark"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
    >
      <rect x="1.5" y="1.5" width="21" height="21" rx="6" fill="var(--accent)" />
      {[7, 11, 15, 19].map((y, i) => (
        <line
          key={y}
          className="brand__line"
          x1="5"
          y1={y}
          x2="19"
          y2={y}
          stroke="#fff"
          strokeWidth="1.4"
          opacity="0.95"
          style={{ animationDelay: `${i * 90}ms` }}
        />
      ))}
    </svg>
  );
}
