import { useHabits } from '../hooks/useHabits';
import { HabitCard } from './HabitCard';
import { Spinner } from '../../../components/ui/Spinner';

export function HabitList() {
  const { data: habits, isLoading, error } = useHabits();

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-2">Failed to load habits</p>
        <p className="text-sm text-gray-500">{error.message}</p>
      </div>
    );
  }

  if (!habits || habits.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No habits yet.</p>
        <p className="text-sm text-gray-400 mt-1">
          Create your first habit to get started!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4" data-testid="habit-list">
      {habits.map((habit) => (
        <HabitCard key={habit.id} habit={habit} />
      ))}
    </div>
  );
}
