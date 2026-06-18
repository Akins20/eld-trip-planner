import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import LogGrid from './LogGrid';

const DAY = {
  date: '2026-06-18',
  totals: { off_duty: 8.5, sleeper: 4.5, driving: 11, on_duty: 0 },
  segments: [
    { status: 'off_duty', start_hour: 0, end_hour: 8.5 },
    { status: 'driving', start_hour: 8.5, end_hour: 19.5 },
    { status: 'sleeper', start_hour: 19.5, end_hour: 24 },
  ],
  remarks: [{ hour: 8.5, location: 'Chicago, IL', kind: 'start' }],
};

describe('LogGrid', () => {
  it('draws one colored line per duty segment', () => {
    const { container } = render(<LogGrid day={DAY} />);
    expect(container.querySelector('svg.log-grid')).toBeTruthy();
    const segmentLines = container.querySelectorAll('line[stroke-width="3.4"]');
    expect(segmentLines.length).toBe(DAY.segments.length);
  });

  it('renders the remarks location label', () => {
    const { getByText } = render(<LogGrid day={DAY} />);
    expect(getByText('Chicago, IL')).toBeTruthy();
  });

  it('renders a per-row total', () => {
    const { getByText } = render(<LogGrid day={DAY} />);
    expect(getByText('11:00')).toBeTruthy(); // driving total
  });
});
