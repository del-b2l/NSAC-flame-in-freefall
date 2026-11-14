import { useEffect, useState } from 'react';
import type { Habitat, TestRecord } from './types';
import { HABITATS, SAMPLE_TESTS } from './data/mockData';
import { getRankedTests, rankTestsLocally } from './api/client';
import DashboardView from './components/DashboardView';

export default function App() {
  const [selectedHabitat, setSelectedHabitat] = useState<Habitat>(HABITATS[2]); // Moon base default
  const [tests, setTests] = useState<TestRecord[]>(() =>
    rankTestsLocally(SAMPLE_TESTS, HABITATS[2])
  );
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    getRankedTests(selectedHabitat)
      .then((result) => {
        if (active) {
          setTests(result);
          setError(null);
        }
      })
      .catch((err) => {
        if (active) {
          console.error('Failed to load ranked tests:', err);
          setError('Unable to reach telemetry backend. Displaying offline sample records.');
          setTests(rankTestsLocally(SAMPLE_TESTS, selectedHabitat));
        }
      });

    return () => {
      active = false;
    };
  }, [selectedHabitat]);

  const handleSelectHabitat = (habitat: Habitat) => {
    setSelectedHabitat(habitat);
  };

  const handleRetry = () => {
    setIsLoading(true);
    getRankedTests(selectedHabitat)
      .then((result) => {
        setTests(result);
        setError(null);
      })
      .catch((err) => {
        console.error('Retry failed:', err);
        setError('Connection retry unsuccessful. Showing offline sample records.');
        setTests(rankTestsLocally(SAMPLE_TESTS, selectedHabitat));
      })
      .finally(() => {
        setIsLoading(false);
      });
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
