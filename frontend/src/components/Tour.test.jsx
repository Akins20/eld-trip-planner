import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import Tour from './Tour';

const STEPS = [
  { target: null, title: 'Welcome', body: 'Intro body' },
  { target: null, title: 'Second', body: 'Second body' },
  { target: null, title: 'Last', body: 'Last body', cta: 'Run it' },
];

describe('Tour', () => {
  it('renders nothing when closed', () => {
    const { container } = render(<Tour steps={STEPS} open={false} onClose={() => {}} />);
    expect(container.firstChild).toBeNull();
  });

  it('shows the first step and advances with Next', () => {
    render(<Tour steps={STEPS} open onClose={vi.fn()} />);
    expect(screen.getByText('Welcome')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    expect(screen.getByText('Second')).toBeInTheDocument();
  });

  it('can be skipped at any point', () => {
    const onClose = vi.fn();
    render(<Tour steps={STEPS} open onClose={onClose} />);
    fireEvent.click(screen.getByRole('button', { name: /skip tour/i }));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('runs the final call-to-action and closes', () => {
    const onClose = vi.fn();
    const onAction = vi.fn();
    render(<Tour steps={STEPS} open onClose={onClose} onAction={onAction} />);
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    fireEvent.click(screen.getByRole('button', { name: 'Next' }));
    fireEvent.click(screen.getByRole('button', { name: 'Run it' }));
    expect(onAction).toHaveBeenCalledTimes(1);
    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
