import { screen, fireEvent, waitFor, within } from '@testing-library/react';
import App from '../App';
import { renderWithAct } from './test-utils/renderWithAct';
import {
  userEventClick,
  userEventClear,
  userEventType,
} from './test-utils/userEventAct';

beforeEach(() => {
  global.fetch = jest.fn((url, options) => {
    if (
      url.includes('/plants') &&
      options?.method === 'POST' &&
      global.__TEST_FAIL_POST
    ) {
      return Promise.resolve({ ok: false });
    }

    if (url.includes('/plants') && !options) {
      return Promise.resolve({ json: () => Promise.resolve([]), ok: true });
    }

    if (url.includes('/plants') && options?.method === 'POST') {
      return Promise.resolve({ json: () => Promise.resolve({}), ok: true });
    }
    if (url.includes('/plants') && options?.method === 'PUT') {
      return Promise.resolve({ json: () => Promise.resolve({}), ok: true });
    }
    if (url.includes('/plants') && options?.method === 'DELETE') {
      return Promise.resolve({ json: () => Promise.resolve({}), ok: true });
    }
    return Promise.resolve({ json: () => Promise.resolve([]), ok: true });
  });
});

afterEach(() => {
  jest.clearAllMocks();
  delete global.__TEST_FAIL_POST;
});

describe('Plant Tracker App', () => {
  test('renders app title', async () => {
    await renderWithAct(<App />);
    expect(await screen.findByText(/🌿 My Plant Tracker/i)).toBeInTheDocument();
  });

  test('switches language on button click', async () => {
    await renderWithAct(<App />);
    await userEventClick(screen.getByRole('button', { name: /日本語へ/i }));
    expect(screen.getByText(/植物リスト/)).toBeInTheDocument();
  });

  test('renders title in English', async () => {
    await renderWithAct(<App />);
    await waitFor(() => {
      expect(screen.getByText(/My Plant Tracker/)).toBeInTheDocument();
    });
  });

  test('toggles to Japanese title', async () => {
    await renderWithAct(<App />);
    await userEventClick(screen.getByRole('button', { name: /日本語へ/i }));
    expect(await screen.findByText(/植物リスト/)).toBeInTheDocument();
  });

  test('has accessible form inputs and buttons', async () => {
    await renderWithAct(<App />);
    expect(
      screen.getByRole('textbox', { name: /name \(en\)/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('textbox', { name: /class \(en\)/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('textbox', { name: /name \(ja\)/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('textbox', { name: /class \(ja\)/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /add plant/i })
    ).toBeInTheDocument();
  });

  test('renders input fields', async () => {
    await renderWithAct(<App />);
    const formElement = screen.getByTestId('add-form');
    expect(
      within(formElement).getByLabelText(/Name \(EN\)/i)
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/Class \(EN\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Name \(JA\)/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Class \(JA\)/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/search plants/i)).toBeInTheDocument();
  });

  test('renders Add Plant button', async () => {
    await renderWithAct(<App />);
    expect(
      screen.getByRole('button', { name: /add plant/i })
    ).toBeInTheDocument();
  });

  test('adds plant successfully', async () => {
    await renderWithAct(<App />);
    const form = screen.getByTestId('add-form');

    fireEvent.change(within(form).getByLabelText(/Name \(EN\)/i), {
      target: { value: 'Lily' },
    });
    fireEvent.change(screen.getByLabelText(/Class \(EN\)/i), {
      target: { value: 'Flower' },
    });
    fireEvent.change(screen.getByLabelText(/Name \(JA\)/i), {
      target: { value: 'ユリ' },
    });
    fireEvent.change(screen.getByLabelText(/Class \(JA\)/i), {
      target: { value: '花' },
    });

    await userEventClick(screen.getByRole('button', { name: /add plant/i }));

    await waitFor(() => {
      expect(
        screen.getByText(/✅ Plant added successfully!/i)
      ).toBeInTheDocument();
    });
  });

  test('shows error message when adding plant fails', async () => {
    global.__TEST_FAIL_POST = true;
    await renderWithAct(<App />);
    const form = screen.getByTestId('add-form');

    fireEvent.change(within(form).getByLabelText(/Name \(EN\)/i), {
      target: { value: 'Lily' },
    });
    fireEvent.change(screen.getByLabelText(/Class \(EN\)/i), {
      target: { value: 'Flower' },
    });
    fireEvent.change(screen.getByLabelText(/Name \(JA\)/i), {
      target: { value: 'ユリ' },
    });
    fireEvent.change(screen.getByLabelText(/Class \(JA\)/i), {
      target: { value: '花' },
    });

    await userEventClick(screen.getByRole('button', { name: /add plant/i }));

    await waitFor(() => {
      expect(screen.getByText(/❌ Failed to add plant/i)).toBeInTheDocument();
    });
  });

  test('shows error on empty form submit', async () => {
    await renderWithAct(<App />);
    await userEventClick(screen.getByRole('button', { name: /add plant/i }));
    await waitFor(() => {
      expect(screen.getByText(/English name is required/i)).toBeInTheDocument();
    });
  });

  test('filters by search input', async () => {
    fetch.mockResolvedValueOnce({
      json: () =>
        Promise.resolve([
          { plant_id: 1, plant_name_en: 'Rose', plant_class_en: 'Flower' },
          { plant_id: 2, plant_name_en: 'Maple', plant_class_en: 'Tree' },
        ]),
      ok: true,
    });

    await renderWithAct(<App />);
    fireEvent.change(screen.getByPlaceholderText(/search plants/i), {
      target: { value: 'rose' },
    });

    await waitFor(() => {
      expect(screen.getByText(/Rose/)).toBeInTheDocument();
      expect(screen.queryByText(/Maple/)).not.toBeInTheDocument();
    });
  });

  test('sorts by date', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('sort_by_date')) {
        return Promise.resolve({
          json: () =>
            Promise.resolve([
              {
                plant_id: 2,
                plant_name_en: 'Zinnia',
                plant_class_en: 'Flower',
              },
            ]),
          ok: true,
        });
      }
      return Promise.resolve({ json: () => Promise.resolve([]), ok: true });
    });

    await renderWithAct(<App />);
    await userEventClick(screen.getByRole('button', { name: /Newest First/i }));
    await waitFor(() => {
      expect(screen.getByText(/Zinnia/)).toBeInTheDocument();
    });
  });

  test('displays edit modal', async () => {
    fetch.mockResolvedValueOnce({
      json: () =>
        Promise.resolve([
          { plant_id: 1, plant_name_en: 'Oak', plant_class_en: 'Tree' },
        ]),
      ok: true,
    });

    await renderWithAct(<App />);
    await waitFor(() => screen.getByText('Edit'));
    await userEventClick(screen.getByText('Edit'));
    expect(await screen.findByText(/Edit Plant/i)).toBeInTheDocument();
  });

  test('edits a plant successfully via modal', async () => {
    fetch.mockResolvedValueOnce({
      json: () =>
        Promise.resolve([
          {
            plant_id: 1,
            plant_name_en: 'Oak',
            plant_class_en: 'Tree',
            plant_name_ja: 'オーク',
            plant_class_ja: '木',
            plant_date: '2023-01-01',
          },
        ]),
      ok: true,
    });

    await renderWithAct(<App />);
    await waitFor(() => screen.getByText('Edit'));
    await userEventClick(screen.getByText('Edit'));

    const modal = screen.getByRole('dialog');
    await userEventClear(within(modal).getByLabelText(/Name \(EN\)/i));
    await userEventType(
      within(modal).getByLabelText(/Name \(EN\)/i),
      'Oak Updated'
    );

    fetch.mockResolvedValueOnce({ json: () => Promise.resolve({}), ok: true }); // PUT
    fetch.mockResolvedValueOnce({ json: () => Promise.resolve([]), ok: true }); // refetch

    await userEventClick(screen.getByRole('button', { name: /save/i }));

    await waitFor(() => {
      expect(screen.queryByText(/edit plant/i)).not.toBeInTheDocument();
      expect(
        screen.getByText(/plant updated successfully/i)
      ).toBeInTheDocument();
    });
  });

  test('deletes a plant', async () => {
    fetch.mockResolvedValueOnce({
      json: () =>
        Promise.resolve([
          { plant_id: 1, plant_name_en: 'Bamboo', plant_class_en: 'Grass' },
        ]),
      ok: true,
    });

    await renderWithAct(<App />);
    await waitFor(() => screen.getByText('Delete'));
    await userEventClick(screen.getByText('Delete'));

    await waitFor(() => {
      expect(screen.getByText(/deleted successfully/i)).toBeInTheDocument();
    });
  });
});
