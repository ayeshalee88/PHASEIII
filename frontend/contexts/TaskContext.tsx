import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { apiClient } from '../lib/api';

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
}

interface TaskContextType {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  fetchTasks: (userId: string, accessToken?: string) => Promise<void>;
  createTask: (userId: string, taskData: Partial<Task>, accessToken?: string) => Promise<Task | null>;
  updateTask: (userId: string, taskId: string, taskData: Partial<Task>, accessToken?: string) => Promise<Task | null>;
  deleteTask: (userId: string, taskId: string, accessToken?: string) => Promise<void>;
  toggleTaskCompletion: (userId: string, taskId: string, completed: boolean, accessToken?: string) => Promise<Task | null>;
}

const TaskContext = createContext<TaskContextType | undefined>(undefined);

interface TaskProviderProps {
  children: ReactNode;
}

export const TaskProvider: React.FC<TaskProviderProps> = ({ children }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async (userId: string, accessToken?: string) => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiClient.getTasks(userId, accessToken);

      if (result.error) {
        throw new Error(result.error);
      }

      setTasks(result.data || []);
    } catch (err: any) {
      setError(err.message);
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (userId: string, taskData: Partial<Task>, accessToken?: string): Promise<Task | null> => {
    try {
      setLoading(true);
      const result = await apiClient.createTask(userId, taskData, accessToken);

      if (result.error) {
        throw new Error(result.error);
      }

      if (result.data) {
        setTasks(prev => [...prev, result.data as Task]);
        return result.data as Task;
      }
      return null;
    } catch (err: any) {
      setError(err.message);
      console.error('Error creating task:', err);
      // Re-fetch to ensure state consistency
      await fetchTasks(userId, accessToken);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const updateTask = async (userId: string, taskId: string, taskData: Partial<Task>, accessToken?: string): Promise<Task | null> => {
    try {
      setLoading(true);
      const result = await apiClient.updateTask(userId, taskId, taskData, accessToken);

      if (result.error) {
        throw new Error(result.error);
      }

      if (result.data) {
        setTasks(prev => prev.map(task =>
          task.id === taskId ? result.data as Task : task
        ));
        return result.data as Task;
      }
      return null;
    } catch (err: any) {
      setError(err.message);
      console.error('Error updating task:', err);
      // Re-fetch to ensure state consistency
      await fetchTasks(userId, accessToken);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const deleteTask = async (userId: string, taskId: string, accessToken?: string) => {
    try {
      setLoading(true);
      await apiClient.deleteTask(userId, taskId, accessToken);
      setTasks(prev => prev.filter(task => task.id !== taskId));
    } catch (err: any) {
      setError(err.message);
      console.error('Error deleting task:', err);
      // Re-fetch to ensure state consistency
      await fetchTasks(userId, accessToken);
    } finally {
      setLoading(false);
    }
  };

  const toggleTaskCompletion = async (userId: string, taskId: string, completed: boolean, accessToken?: string): Promise<Task | null> => {
    try {
      setLoading(true);
      const result = await apiClient.updateTaskCompletion(userId, taskId, completed, accessToken);

      if (result.data) {
        setTasks(prev => prev.map(task =>
          task.id === taskId ? { ...task, completed, updated_at: new Date().toISOString() } : task
        ));
        return result.data as Task;
      }
      return null;
    } catch (err: any) {
      setError(err.message);
      console.error('Error toggling task completion:', err);
      // Re-fetch to ensure state consistency
      await fetchTasks(userId, accessToken);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return (
    <TaskContext.Provider value={{
      tasks,
      loading,
      error,
      fetchTasks,
      createTask,
      updateTask,
      deleteTask,
      toggleTaskCompletion
    }}>
      {children}
    </TaskContext.Provider>
  );
};

export const useTasks = () => {
  const context = useContext(TaskContext);
  if (context === undefined) {
    throw new Error('useTasks must be used within a TaskProvider');
  }
  return context;
};