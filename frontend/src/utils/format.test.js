import { describe, expect, it } from 'vitest';

import { clockLabel, formatDate, formatHours, formatMiles, hoursToHHMM } from './format';

describe('format helpers', () => {
  it('hoursToHHMM formats decimal hours', () => {
    expect(hoursToHHMM(0)).toBe('0:00');
    expect(hoursToHHMM(0.25)).toBe('0:15');
    expect(hoursToHHMM(1.5)).toBe('1:30');
    expect(hoursToHHMM(11)).toBe('11:00');
  });

  it('formatMiles rounds and adds a thousands separator', () => {
    expect(formatMiles(0)).toBe('0 mi');
    expect(formatMiles(1500.4)).toBe('1,500 mi');
  });

  it('formatHours keeps two decimals', () => {
    expect(formatHours(2)).toBe('2.00 h');
    expect(formatHours(7.755)).toBe('7.75 h');
  });

  it('clockLabel renders a 24-hour wall clock', () => {
    expect(clockLabel(0)).toBe('00:00');
    expect(clockLabel(8.5)).toBe('08:30');
    expect(clockLabel(24)).toBe('00:00');
  });

  it('formatDate renders a readable date', () => {
    expect(formatDate('2026-06-18')).toMatch(/Jun 18,? 2026/);
  });
});
