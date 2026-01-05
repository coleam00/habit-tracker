import { useState } from 'react';
import { addMonths, subMonths, format } from 'date-fns';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { CalendarGrid } from './CalendarGrid';
import { useCompletions } from '../hooks/useCompletions';
import { useCompleteHabit, useUncompleteHabit, useSkipHabit } from '../../habits';
import { Card } from '../../../components/ui/Card';
import { Spinner } from '../../../components/ui/Spinner';

export function Calendar({ habitId }) {
  const [month, setMonth] = useState(new Date());

  const { data: completions, isLoading, error } = useCompletions(habitId, month);
  const { mutate: complete } = useCompleteHabit();
  const { mutate: uncomplete } = useUncompleteHabit();
  const { mutate: skip } = useSkipHabit();

  const handlePrevMonth = () => setMonth((m) => subMonths(m, 1));
  const handleNextMonth = () => setMonth((m) => addMonths(m, 1));

  const handleToggle = (dateStr, currentStatus, event) => {
    const isShiftClick = event?.shiftKey;

    if (currentStatus === 'completed' || currentStatus === 'skipped') {
      // Any existing status → Clear
      uncomplete({ id: habitId, date: dateStr });
    } else if (isShiftClick) {
      // Shift+Click on empty → Skip
      skip({ id: habitId, date: dateStr });
    } else {
      // Normal click on empty → Complete
      complete({ id: habitId, date: dateStr });
    }
  };

  if (error) {
    return (
      <Card className="p-4">
        <p className="text-red-600 text-center">Failed to load calendar</p>
      </Card>
    );
  }

  return (
    <Card>
      <Card.Header className="flex items-center justify-between">
        <button
          onClick={handlePrevMonth}
          className="p-1 rounded hover:bg-gray-100 transition-colors"
          aria-label="Previous month"
        >
          <ChevronLeft className="w-5 h-5 text-gray-600" />
        </button>

        <h3 className="font-semibold text-gray-900">
          {format(month, 'MMMM yyyy')}
        </h3>

        <button
          onClick={handleNextMonth}
          className="p-1 rounded hover:bg-gray-100 transition-colors"
          aria-label="Next month"
        >
          <ChevronRight className="w-5 h-5 text-gray-600" />
        </button>
      </Card.Header>

      <Card.Body>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : (
          <CalendarGrid
            month={month}
            completions={completions}
            onToggle={handleToggle}
          />
        )}
      </Card.Body>
    </Card>
  );
}
