import L from 'leaflet';
import PropTypes from 'prop-types';
import { useEffect } from 'react';
import { useMap } from 'react-leaflet';

const TRUCK_SVG = `
<svg viewBox="0 0 24 24" width="16" height="16" fill="none" aria-hidden="true">
  <rect x="2" y="7" width="11" height="8" rx="1.5" fill="#2563eb"/>
  <path d="M13 9h3.6l3.4 3.2V15H13z" fill="#1d4ed8"/>
  <rect x="15.4" y="9.8" width="2.6" height="2.3" rx="0.5" fill="#cfe0ff"/>
  <circle cx="6" cy="15.4" r="2.1" fill="#1f2937"/>
  <circle cx="16.4" cy="15.4" r="2.1" fill="#1f2937"/>
</svg>`;

/** A truck marker that continuously drives along the route polyline. */
export default function MovingTruck({ path }) {
  const map = useMap();

  useEffect(() => {
    if (!path || path.length < 2) return undefined;
    const icon = L.divIcon({
      className: 'route-truck-icon',
      html: `<div class="route-truck">${TRUCK_SVG}</div>`,
      iconSize: [30, 30],
      iconAnchor: [15, 15],
    });
    const marker = L.marker(path[0], {
      icon,
      interactive: false,
      keyboard: false,
      zIndexOffset: 1000,
    }).addTo(map);

    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduce) {
      marker.setLatLng(path[Math.floor(path.length / 2)]);
      return () => map.removeLayer(marker);
    }

    const total = path.length;
    const stride = Math.max(1, Math.floor(total / 260));
    const stepMs = 40;
    let i = 0;
    let last = 0;
    let raf = 0;
    const tick = (t) => {
      if (t - last >= stepMs) {
        last = t;
        i = (i + stride) % total;
        marker.setLatLng(path[i]);
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(raf);
      map.removeLayer(marker);
    };
  }, [map, path]);

  return null;
}

MovingTruck.propTypes = { path: PropTypes.array };
