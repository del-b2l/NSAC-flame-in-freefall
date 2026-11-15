import { useEffect, useState } from 'react';
import type { Habitat, TestRecord } from './types';
import { HABITATS } from './data/mockData';
import { getRankedTests } from './api/client';
import DashboardView from './components/DashboardView';

export default function App() {
  const [selectedHabitat, setSelectedHabitat] = useState<Habitat>(HABITATS[2]); // Moon base default
  const [tests, setTests] = useState<TestRecord[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState<number>(0);

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
  }, [selectedHabitat, reloadKey]);

  const handleSelectHabitat = (habitat: Habitat) => {
    setSelectedHabitat(habitat);
  };

  const handleRetry = () => {
    setReloadKey((key) => key + 1);
  };

  return (
    <DashboardView
      habitats={HABITATS}
      selectedHabitat={selectedHabitat}
      onSelectHabitat={handleSelectHabitat}
      tests={tests}
      isLoading={isLoading}
      error={error}
      onRetry={handleRetry}
    />
  );
}
