import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import TripForm from './TripForm';

describe('TripForm', () => {
  it('blocks submit and shows errors when empty', () => {
    const onSubmit = vi.fn();
    render(<TripForm onSubmit={onSubmit} />);
    fireEvent.click(screen.getByRole('button', { name: /plan trip/i }));
    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByText(/current location is required/i)).toBeInTheDocument();
  });

  it('fills the example and submits a parsed payload', () => {
    const onSubmit = vi.fn();
    render(<TripForm onSubmit={onSubmit} />);
    fireEvent.click(screen.getByRole('button', { name: /try an example/i }));
    fireEvent.click(screen.getByRole('button', { name: /plan trip/i }));
    expect(onSubmit).toHaveBeenCalledTimes(1);
    expect(onSubmit.mock.calls[0][0]).toMatchObject({
      current_location: 'Chicago, IL',
      pickup_location: 'Dallas, TX',
      dropoff_location: 'Los Angeles, CA',
      current_cycle_used: 8,
    });
  });

  it('rejects a cycle value outside 0-70', () => {
    const onSubmit = vi.fn();
    render(<TripForm onSubmit={onSubmit} />);
    fireEvent.change(screen.getByLabelText(/current location/i), { target: { value: 'A' } });
    fireEvent.change(screen.getByLabelText(/pickup/i), { target: { value: 'B' } });
    fireEvent.change(screen.getByLabelText(/dropoff/i), { target: { value: 'C' } });
    fireEvent.change(screen.getByLabelText(/cycle used/i), { target: { value: '90' } });
    fireEvent.click(screen.getByRole('button', { name: /plan trip/i }));
    expect(onSubmit).not.toHaveBeenCalled();
    expect(screen.getByText(/between 0 and 70/i)).toBeInTheDocument();
  });
});
