// Pure formatting helpers (unit-tested; no React).

/** Decimal hours -> "H:MM" (e.g. 1.5 -> "1:30"). */
export function hoursToHHMM(hours) {
  const totalMin = Math.round(Number(hours) * 60);
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  return `${h}:${String(m).padStart(2, '0')}`;
}

/** Decimal hours -> "1.50 h". */
export function formatHours(hours) {
  return `${Number(hours).toFixed(2)} h`;
}

/** Miles -> "1,234 mi". */
export function formatMiles(miles) {
  return `${Math.round(Number(miles)).toLocaleString()} mi`;
}

/** Grid hour (0..24) -> wall-clock "HH:MM" with a leading zero. */
export function clockLabel(hour) {
  const totalMin = Math.round(Number(hour) * 60) % (24 * 60);
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
}

/** ISO date "2026-06-18" -> "Thu, Jun 18 2026". */
export function formatDate(iso) {
  const d = new Date(`${iso}T00:00:00`);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}
