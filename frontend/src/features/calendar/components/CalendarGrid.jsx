import {
  eachDayOfInterval,
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  format,
} from 'date-fns';
import { CalendarDay } from './CalendarDay';

const WEEKDAY_LABELS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export function CalendarGrid({ month, completions, onToggle }) {
  // Generate calendar days including padding from adjacent months
  const monthStart = startOfMonth(month);
  const monthEnd = endOfMonth(month);
  const calendarStart = startOfWeek(monthStart); // Sunday before month start
  const calendarEnd = endOfWeek(monthEnd); // Saturday after month end

  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

  return (
    <div>
      {/* Weekday headers */}
      <div className="grid grid-cols-7 gap-1 mb-2">
        {WEEKDAY_LABELS.map((label) => (
          <div
            key={label}
            className="text-center text-xs font-medium text-gray-500 py-1"
          >
            {label}
          </div>
        ))}
      </div>

      {/* Day grid */}
      <div className="grid grid-cols-7 gap-1">
        {days.map((day) => {
          const dateKey = format(day, 'yyyy-MM-dd');
          return (
            <CalendarDay
              key={dateKey}
              date={day}
              month={month}
              status={completions?.get(dateKey)}
              onToggle={onToggle}
            />
          );
        })}
      </div>
    </div>
  );
}
