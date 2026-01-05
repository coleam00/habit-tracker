import { useQuery } from '@tanstack/react-query';
import { format, startOfMonth, endOfMonth } from 'date-fns';
import { fetchCompletions } from '../../habits/api/habits';

export function useCompletions(habitId, month) {
  const monthKey = format(month, 'yyyy-MM');
  const start = format(startOfMonth(month), 'yyyy-MM-dd');
  const end = format(endOfMonth(month), 'yyyy-MM-dd');

  return useQuery({
    queryKey: ['completions', habitId, monthKey],
    queryFn: async () => {
      const data = await fetchCompletions(habitId, start, end);
      // Convert to Map for O(1) lookup by date
      const completionMap = new Map();
      data.completions.forEach((c) => {
        completionMap.set(c.date, c.status);
      });
      return completionMap;
    },
    enabled: !!habitId,
  });
}
