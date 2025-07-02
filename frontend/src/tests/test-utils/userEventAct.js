// src/tests/test-utils/userEventAct.js
import { act } from 'react';
import userEvent from '@testing-library/user-event';

export async function userEventClick(element) {
  await act(async () => {
    await userEvent.click(element);
  });
}

export async function userEventClear(element) {
  await act(async () => {
    await userEvent.clear(element);
  });
}

export async function userEventType(element, text) {
  await act(async () => {
    await userEvent.type(element, text);
  });
}
