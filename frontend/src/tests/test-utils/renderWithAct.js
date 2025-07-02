import { act } from 'react';
import { render } from '@testing-library/react';

export async function renderWithAct(ui, options) {
  let result;
  await act(async () => {
    result = render(ui, options);
    // Wait a tick to allow useEffect and state updates to flush
    await Promise.resolve();
  });
  return result;
}