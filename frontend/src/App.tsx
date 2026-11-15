import { useEffect, useState } from 'react';
import type { Habitat, TestRecord } from './types';
import { HABITATS } from './data/mockData';
import { getHabitats, getRankedTests } from './api/client';
import DashboardView from './components/DashboardView';

/** Keep the planet artwork, which only the frontend knows, on a backend habitat. */
function withArtwork(habitat: Habitat): Habitat {
  const local = HABITATS.find((h) => h.name === habitat.name);
  return { ...habitat, planetGif: local?.planetGif };
}

export default function App() {
  // The list starts from the built-in copy so the page can draw, then is
  // replaced by the backend's values, which carry the status and source link.
  const [habitats, setHabitats] = useState<Habitat[]>(HABITATS);
  const [selectedHabitat, setSelectedHabitat] = useState<Habitat>(HABITATS[2]); // Moon base default
  const [tests, setTests] = useState<TestRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState<number>(0);

  useEffect(() => {
    let active = true;
    getHabitats()
      .then((loaded) => {
        if (!active || loaded.length === 0) {
          return;
        }
        const next = loaded.map(withArtwork);
        setHabitats(next);
        setSelectedHabitat((current) => next.find((h) => h.name === current.name) ?? next[0]);
      })
      .catch((err: unknown) => {
        console.error('Failed to load habitats:', err);
      });
    return () => {
      active = false;
    };
  }, [reloadKey]);

  const habitatName = selectedHabitat.name;

  useEffect(() => {
    let active = true;
    setIsLoading(true);

    getRankedTests(selectedHabitat)
      .then((result) => {
        if (!active) {
          return;
        }
        setTests(result);
        setError(null);
      })
      .catch((err: unknown) => {
        if (!active) {
          return;
        }
        console.error('Failed to load ranked tests:', err);
        setTests([]);
        setError('Could not reach the ranking API. Is the backend running on :8000?');
      })
      .finally(() => {
        if (active) {
          setIsLoading(false);
        }
      });

    return () => {
      active = false;
    };
    // The ranking depends only on which habitat is chosen, not on the object identity.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [habitatName, reloadKey]);

  const handleSelectHabitat = (habitat: Habitat) => {
    setSelectedHabitat(habitat);
  };

  const handleRetry = () => {
    setReloadKey((key) => key + 1);
  };

  return (
    <DashboardView
      habitats={habitats}
      selectedHabitat={selectedHabitat}
      onSelectHabitat={handleSelectHabitat}
      tests={tests}
      isLoading={isLoading}
      error={error}
      onRetry={handleRetry}
    />
  );
}
