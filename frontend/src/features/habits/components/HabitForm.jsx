import { useState } from 'react';
import { Button } from '../../../components/ui/Button';
import { useCreateHabit, useUpdateHabit } from '../hooks/useHabits';

const COLOR_OPTIONS = [
  '#10B981', // Green (default)
  '#3B82F6', // Blue
  '#8B5CF6', // Purple
  '#F59E0B', // Amber
  '#EF4444', // Red
  '#EC4899', // Pink
  '#06B6D4', // Cyan
  '#6366F1', // Indigo
];

export function HabitForm({ onSuccess, habit = null }) {
  const isEditing = !!habit;

  const [name, setName] = useState(habit?.name || '');
  const [description, setDescription] = useState(habit?.description || '');
  const [color, setColor] = useState(habit?.color || COLOR_OPTIONS[0]);
  const [error, setError] = useState('');

  const { mutate: createHabit, isPending: isCreating } = useCreateHabit();
  const { mutate: updateHabit, isPending: isUpdating } = useUpdateHabit();

  const isPending = isCreating || isUpdating;

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (!name.trim()) {
      setError('Name is required');
      return;
    }

    const data = {
      name: name.trim(),
      description: description.trim() || null,
      color,
    };

    if (isEditing) {
      updateHabit(
        { id: habit.id, data },
        {
          onSuccess: () => onSuccess?.(),
          onError: (err) => setError(err.message),
        }
      );
    } else {
      createHabit(data, {
        onSuccess: () => {
          setName('');
          setDescription('');
          setColor(COLOR_OPTIONS[0]);
          onSuccess?.();
        },
        onError: (err) => {
          setError(err.message);
        },
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label
          htmlFor="habit-name"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Habit Name
        </label>
        <input
          id="habit-name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g., Morning meditation"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          maxLength={100}
        />
      </div>

      <div>
        <label
          htmlFor="habit-description"
          className="block text-sm font-medium text-gray-700 mb-1"
        >
          Description (optional)
        </label>
        <textarea
          id="habit-description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="What does this habit involve?"
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
          maxLength={500}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Color
        </label>
        <div className="flex gap-2 flex-wrap">
          {COLOR_OPTIONS.map((c) => (
            <button
              key={c}
              type="button"
              onClick={() => setColor(c)}
              className={`w-8 h-8 rounded-full transition-transform ${
                color === c ? 'ring-2 ring-offset-2 ring-gray-400 scale-110' : ''
              }`}
              style={{ backgroundColor: c }}
              aria-label={`Select color ${c}`}
            />
          ))}
        </div>
      </div>

      {error && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      <Button type="submit" isLoading={isPending} className="w-full">
        {isEditing ? 'Save Changes' : 'Create Habit'}
      </Button>
    </form>
  );
}
