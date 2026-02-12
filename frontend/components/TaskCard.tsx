import React from 'react';
import styles from './TaskCard.module.css';

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

interface TaskCardProps {
  task: Task;
  colorIndex: number;
  onToggleComplete: (id: string, completed: boolean) => void;
  onDelete: (id: string) => void;
  onEdit: (task: Task) => void;
}

const TaskCard: React.FC<TaskCardProps> = ({ task, colorIndex, onToggleComplete, onDelete, onEdit }) => {
  const colorClasses = [
    styles.cardYellow,
    styles.cardBlue,
    styles.cardPink,
    styles.cardOrange,
  ];

  const rotation = Math.random() * 4 - 2; // Random rotation between -2 and 2 degrees

  return (
    <div
      className={`${styles.card} ${colorClasses[colorIndex]}`}
      style={{ transform: `rotate(${rotation}deg)` }}
    >
      {/* Tape Effect */}
      <div className={styles.tape}></div>

      {/* Header with Checkbox and Title */}
      <div className={styles.header}>
        <input
          type="checkbox"
          checked={task.completed}
          onChange={() => onToggleComplete(task.id, !task.completed)}
          className={styles.checkbox}
          onClick={(e) => e.stopPropagation()}
        />
        <h3 className={`${styles.title} ${task.completed ? styles.titleCompleted : ''}`}>
          {task.title}
        </h3>
      </div>

      {/* Description */}
      {task.description && (
        <p className={`${styles.description} ${task.completed ? styles.descriptionCompleted : ''}`}>
          {task.description}
        </p>
      )}

      {/* Action Buttons */}
      <div className={styles.actions}>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onEdit(task);
          }}
          className={styles.actionButton}
          title="Edit"
        >
          ✏️
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(task.id);
          }}
          className={styles.actionButton}
          title="Delete"
        >
          🗑️
        </button>
      </div>

      {/* Date Stamp */}
      <div className={styles.date}>
        {new Date(task.created_at).toLocaleDateString()}
      </div>
    </div>
  );
};

export default TaskCard;