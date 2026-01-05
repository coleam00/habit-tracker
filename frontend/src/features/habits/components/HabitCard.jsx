import { useState } from 'react';
import { format } from 'date-fns';
import { Check, Flame, TrendingUp, ChevronDown, ChevronUp, Pencil, Trash2, X } from 'lucide-react';
import clsx from 'clsx';
import { Card } from '../../../components/ui/Card';
import { useCompleteHabit, useUncompleteHabit, useDeleteHabit } from '../hooks/useHabits';
import { Calendar } from '../../calendar';
import { HabitForm } from './HabitForm';
import { ConfirmDialog } from '../../../components/ui/ConfirmDialog';

export function HabitCard({ habit }) {
  const [showCalendar, setShowCalendar] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  const { mutate: complete, isPending: isCompleting } = useCompleteHabit();
  const { mutate: uncomplete, isPending: isUncompleting } = useUncompleteHabit();
  const { mutate: deleteHabit, isPending: isDeleting } = useDeleteHabit();

  const today = format(new Date(), 'yyyy-MM-dd');
  const isPending = isCompleting || isUncompleting;

  const handleToggle = () => {
    if (habit.completed_today) {
      uncomplete({ id: habit.id, date: today });
    } else {
      complete({ id: habit.id, date: today });
    }
  };

  return (
    <Card className="overflow-hidden">
      <div className="flex items-stretch">
        {/* Color bar */}
        <div
          className="w-2 flex-shrink-0"
          style={{ backgroundColor: habit.color }}
        />

        <div className="flex-1 p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-gray-900 truncate">
                {habit.name}
              </h3>
              {habit.description && (
                <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                  {habit.description}
                </p>
              )}
            </div>

            {/* Edit/Delete buttons */}
            <div className="flex items-center gap-1 ml-2">
              <button
                onClick={() => setShowEditModal(true)}
                className="p-1.5 text-gray-400 hover:text-gray-600 rounded hover:bg-gray-100"
                aria-label="Edit habit"
              >
                <Pencil className="w-4 h-4" />
              </button>
              <button
                onClick={() => setShowDeleteDialog(true)}
                className="p-1.5 text-gray-400 hover:text-red-600 rounded hover:bg-gray-100"
                aria-label="Delete habit"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>

            {/* Completion toggle */}
            <button
              onClick={handleToggle}
              disabled={isPending}
              className={clsx(
                'ml-4 flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center transition-all',
                'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary',
                habit.completed_today
                  ? 'bg-primary text-white'
                  : 'border-2 border-gray-300 text-gray-400 hover:border-primary hover:text-primary',
                isPending && 'opacity-50 cursor-wait'
              )}
              aria-label={
                habit.completed_today ? 'Mark as incomplete' : 'Mark as complete'
              }
            >
              <Check className="w-5 h-5" />
            </button>
          </div>

          {/* Stats */}
          <div className="mt-4 flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1 text-orange-500">
              <Flame className="w-4 h-4" />
              <span className="font-medium">{habit.current_streak}</span>
              <span className="text-gray-500">day streak</span>
            </div>

            <div className="flex items-center gap-1 text-blue-500">
              <TrendingUp className="w-4 h-4" />
              <span className="font-medium">{habit.completion_rate}%</span>
            </div>
          </div>

          {/* Calendar toggle */}
          <button
            onClick={() => setShowCalendar(!showCalendar)}
            className="mt-3 w-full flex items-center justify-center gap-1 text-sm text-gray-500 hover:text-gray-700 py-1"
            aria-expanded={showCalendar}
            aria-label={showCalendar ? 'Hide calendar' : 'Show calendar'}
          >
            {showCalendar ? (
              <>
                <ChevronUp className="w-4 h-4" />
                Hide Calendar
              </>
            ) : (
              <>
                <ChevronDown className="w-4 h-4" />
                Show Calendar
              </>
            )}
          </button>

          {/* Calendar view */}
          {showCalendar && (
            <div className="mt-4 -mx-4 -mb-4">
              <Calendar habitId={habit.id} />
            </div>
          )}
        </div>
      </div>

      {/* Edit Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-md">
            <Card.Header className="flex items-center justify-between">
              <h2 className="font-semibold text-lg">Edit Habit</h2>
              <button
                onClick={() => setShowEditModal(false)}
                className="text-gray-400 hover:text-gray-600"
                aria-label="Close"
              >
                <X className="w-5 h-5" />
              </button>
            </Card.Header>
            <Card.Body>
              <HabitForm
                habit={habit}
                onSuccess={() => setShowEditModal(false)}
              />
            </Card.Body>
          </Card>
        </div>
      )}

      {/* Delete Confirmation */}
      <ConfirmDialog
        isOpen={showDeleteDialog}
        onClose={() => setShowDeleteDialog(false)}
        onConfirm={() => {
          deleteHabit(habit.id, {
            onSuccess: () => setShowDeleteDialog(false),
          });
        }}
        title="Delete Habit"
        message={`Are you sure you want to delete "${habit.name}"? This will permanently remove the habit and all its completion history.`}
        confirmText={isDeleting ? 'Deleting...' : 'Delete'}
        variant="danger"
      />
    </Card>
  );
}
