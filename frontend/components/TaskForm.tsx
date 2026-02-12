import React, { useState } from 'react';
import styles from './TaskForm.module.css';

interface Task {
  id?: string;
  title: string;
  description?: string;
  completed?: boolean;
}

interface TaskFormProps {
  task?: Task;
  onSubmit: (task: Task) => void;
  onCancel: () => void;
}

const TaskForm: React.FC<TaskFormProps> = ({
  task,
  onSubmit,
  onCancel,
}) => {
  const [formData, setFormData] = useState<Pick<Task, 'title' | 'description'>>({
    title: task?.title ?? '',
    description: task?.description ?? '',
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const trimmedTitle = formData.title.trim();
    if (!trimmedTitle) return;

    onSubmit({
      ...task,
      title: trimmedTitle,
      description: formData.description?.trim(),
    });
  };

  return (
    <div className={styles.formContainer}>
      <form onSubmit={handleSubmit} className={styles.form}>
        {/* Title */}
        <div className={styles.inputGroup}>
          <label htmlFor="title" className={styles.label}>
            Title *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            className={styles.input}
            placeholder="Enter task title"
            autoFocus
          />
        </div>

        {/* Description */}
        <div className={styles.inputGroup}>
          <label htmlFor="description" className={styles.label}>
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            className={styles.textarea}
            placeholder="Enter task description (optional)"
            rows={3}
          />
        </div>

        {/* Buttons */}
        <div className={styles.buttonGroup}>
          <button
            type="submit"
            className={styles.submitButton}
            disabled={!formData.title.trim()}
          >
            {task?.id ? 'Update Task' : 'Create Task'}
          </button>

          <button
            type="button"
            onClick={onCancel}
            className={styles.cancelButton}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default TaskForm;
