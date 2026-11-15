import { useEffect, useState } from 'react';

export interface ApiState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
}

/**
 * Load one backend resource and track its loading and error state.
 * `key` re-runs the request when it changes (for example the habitat name).
 */
export function useApi<T>(load: () => Promise<T>, key: string = ''): ApiState<T> {
  const [state, setState] = useState<ApiState<T>>({ data: null, error: null, loading: true });

  useEffect(() => {
    let active = true;
    setState((previous) => ({ ...previous, loading: true, error: null }));
    load()
      .then((data) => {
        if (active) {
          setState({ data, error: null, loading: false });
        }
      })
      .catch((err: unknown) => {
        if (active) {
          setState({ data: null, error: err instanceof Error ? err.message : String(err), loading: false });
        }
      });
    return () => {
      active = false;
    };
    // `load` is recreated on every render; `key` says when the request changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return state;
}
