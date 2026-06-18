import 'leaflet/dist/leaflet.css';

import PropTypes from 'prop-types';
import { useEffect, useMemo } from 'react';
import { MapContainer, Polyline, TileLayer, useMap } from 'react-leaflet';

import { STATUS, STATUS_COLORS } from '../constants';
import MovingTruck from './MovingTruck';
import './RouteMap.css';

const US_CENTER = [39.5, -98.35];

function FitBounds({ positions }) {
  const map = useMap();
  useEffect(() => {
    if (positions && positions.length > 1) {
      map.fitBounds(positions, { padding: [42, 42] });
    }
  }, [map, positions]);
  return null;
}

FitBounds.propTypes = { positions: PropTypes.array };

export default function RouteMap({ plan }) {
  const geometry = useMemo(() => plan.route.geometry || [], [plan]);
  const center = geometry[Math.floor(geometry.length / 2)] || US_CENTER;

  return (
    <section className="map-section" aria-label="Route map">
      <div className="section-head">
        <h2>Route</h2>
        <p>The routed path on a truck profile. Every stop and rest is in the timeline.</p>
      </div>

      <div className="map-frame">
        <MapContainer className="map" center={center} zoom={5} scrollWheelZoom={false}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {geometry.length > 1 && (
            <Polyline
              positions={geometry}
              smoothFactor={0}
              pathOptions={{ color: STATUS_COLORS[STATUS.DRIVING], weight: 4, opacity: 0.85 }}
            />
          )}
          {geometry.length > 1 && <MovingTruck path={geometry} />}
          <FitBounds positions={geometry} />
        </MapContainer>
      </div>
    </section>
  );
}

RouteMap.propTypes = { plan: PropTypes.object.isRequired };
