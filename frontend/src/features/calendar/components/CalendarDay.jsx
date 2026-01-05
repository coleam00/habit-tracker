import clsx from 'clsx';
import { format, isToday, isSameMonth, isFuture } from 'date-fns';

export function CalendarDay({ date, month, status, onToggle }) {
  const dateStr = format(date, 'yyyy-MM-dd');
  const dayNumber = format(date, 'd');
  const isCurrentMonth = isSameMonth(date, month);
  const isDateToday = isToday(date);
  const isFutureDate = isFuture(date);

  const handleClick = (event) => {
    if (!isFutureDate && isCurrentMonth) {
      onToggle(dateStr, status, event);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={isFutureDate || !isCurrentMonth}
      className={clsx(
        'aspect-square flex items-center justify-center text-sm rounded-md transition-colors',
        // Base states
        !isCurrentMonth && 'text-gray-300 cursor-default',
        isCurrentMonth && !isFutureDate && 'cursor-pointer hover:ring-2 hover:ring-gray-300',
        isFutureDate && isCurrentMonth && 'text-gray-400 cursor-default',
        // Status colors (only for current month, non-future)
        isCurrentMonth && !isFutureDate && status === 'completed' && 'bg-green-500 text-white',
        isCurrentMonth && !isFutureDate && status === 'skipped' && 'bg-gray-400 text-white',
        isCurrentMonth && !isFutureDate && !status && 'bg-red-100 text-red-700',
        // Today highlight
        isDateToday && 'ring-2 ring-primary ring-offset-1'
      )}
      aria-label={`${format(date, 'MMMM d, yyyy')}${status ? `, ${status}` : ''}`}
    >
      {dayNumber}
    </button>
  );
}
