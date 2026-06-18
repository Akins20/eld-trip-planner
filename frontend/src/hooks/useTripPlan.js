import { useCallback, useState } from 'react';

import { planTrip } from '../api/client';

/** Manages the request lifecycle for a trip plan (idle / loading / error / data). */
export function useTripPlan() {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const submit = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const data = await planTrip(payload);
      setPlan(data);
      return data;
    } catch (err) {
      setError(err.message);
      setPlan(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  // Loads a bundled sample plan (used by ?demo and as an offline fallback).
  const loadSample = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/sample-plan.json', { cache: 'no-cache' });
      if (!res.ok) throw new Error('Sample unavailable');
      const data = await res.json();
      setPlan(data);
      return data;
    } catch {
      setError('Could not load the sample plan.');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { plan, loading, error, submit, loadSample };
}
