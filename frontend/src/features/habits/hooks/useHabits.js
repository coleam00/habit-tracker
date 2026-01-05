import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchHabits,
  fetchHabit,
  createHabit,
  updateHabit,
  deleteHabit,
  completeHabit,
  uncompleteHabit,
  skipHabit,
} from '../api/habits';

export function useHabits() {
  return useQuery({
    queryKey: ['habits'],
    queryFn: async () => {
      const data = await fetchHabits();
      return data.habits;
    },
  });
}

export function useHabit(id) {
  return useQuery({
    queryKey: ['habits', id],
    queryFn: () => fetchHabit(id),
    enabled: !!id,
  });
}

export function useCreateHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createHabit,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
    },
  });
}

export function useUpdateHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }) => updateHabit(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
      queryClient.invalidateQueries({ queryKey: ['habits', id] });
    },
  });
}

export function useDeleteHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteHabit,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
    },
  });
}

export function useCompleteHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, date }) => completeHabit(id, date),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
      queryClient.invalidateQueries({ queryKey: ['completions', id] });
    },
  });
}

export function useUncompleteHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, date }) => uncompleteHabit(id, date),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
      queryClient.invalidateQueries({ queryKey: ['completions', id] });
    },
  });
}

export function useSkipHabit() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, date, reason }) => skipHabit(id, date, reason),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
      queryClient.invalidateQueries({ queryKey: ['completions', id] });
    },
  });
}
