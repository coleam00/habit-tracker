import { request } from '../../../lib/api';

export const fetchHabits = () => request('/habits/');

export const fetchHabit = (id) => request(`/habits/${id}`);

export const createHabit = (data) =>
  request('/habits/', {
    method: 'POST',
    body: JSON.stringify(data),
  });

export const updateHabit = (id, data) =>
  request(`/habits/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });

export const deleteHabit = (id) =>
  request(`/habits/${id}`, {
    method: 'DELETE',
  });

export const archiveHabit = (id) =>
  request(`/habits/${id}/archive`, {
    method: 'PATCH',
  });

export const completeHabit = (id, date) =>
  request(`/habits/${id}/complete`, {
    method: 'POST',
    body: JSON.stringify({ date }),
  });

export const skipHabit = (id, date, reason = null) =>
  request(`/habits/${id}/skip`, {
    method: 'POST',
    body: JSON.stringify({ date, reason }),
  });

export const uncompleteHabit = (id, date) =>
  request(`/habits/${id}/completions/${date}`, {
    method: 'DELETE',
  });

export const fetchCompletions = (id, start = null, end = null) => {
  const params = new URLSearchParams();
  if (start) params.append('start', start);
  if (end) params.append('end', end);
  const query = params.toString();
  return request(`/habits/${id}/completions${query ? `?${query}` : ''}`);
};
