import { useState, useEffect, useCallback } from 'react';

export const useLocation = () => {
  const [location, setLocation] = useState({ lat: 40.8135, lng: -74.0745 }); // MetLife Stadium default
  const [error, setError] = useState(null);
  const [watching, setWatching] = useState(false);

  const getLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setError('Geolocation not supported');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      (err) => setError(err.message),
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  }, []);

  const watchLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setError('Geolocation not supported');
      return null;
    }
    setWatching(true);
    return navigator.geolocation.watchPosition(
      (pos) => setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      (err) => setError(err.message),
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
    );
  }, []);

  const stopWatching = useCallback((watchId) => {
    if (watchId) navigator.geolocation.clearWatch(watchId);
    setWatching(false);
  }, []);

  useEffect(() => {
    getLocation();
  }, []);

  return { location, error, watching, getLocation, watchLocation, stopWatching };
};
