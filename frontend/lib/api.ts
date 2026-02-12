const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type ApiResult<T> = {
  data?: T;
  error?: string;
};

// Helper function to get the auth token
const getAuthToken = (): string | null => {
  if (typeof window !== 'undefined') {
    // Try to get token from next-auth session storage
    const sessionStr = localStorage.getItem('next-auth.session-token') || 
                      sessionStorage.getItem('next-auth.session-token');
    
    if (sessionStr) {
      try {
        const session = JSON.parse(sessionStr);
        return session.accessToken || session.access_token;
      } catch (e) {
        console.warn('Could not parse session token from localStorage');
      }
    }
    
    // Alternative: try to get from a global auth context if available
    if ((window as any).__NEXT_AUTH__) {
      return (window as any).__NEXT_AUTH__.session?.accessToken;
    }
  }
  
  return null;
};

export const apiClient = {
  // GET TASKS
  async getTasks(userId: string, accessToken?: string): Promise<ApiResult<any[]>> {
    try {
      // Use provided access token, or fall back to stored token
      const token = accessToken || getAuthToken();
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(`${API_URL}/api/users/${userId}/tasks`, {
        headers: headers
      });

      if (!res.ok) {
        return { error: `Failed to fetch tasks: ${res.status}` };
      }

      const data = await res.json();
      return { data };
    } catch (err) {
      return { error: 'Network error while fetching tasks' };
    }
  },

  // CREATE TASK
  async createTask(userId: string, task: any, accessToken?: string): Promise<ApiResult<any>> {
    try {
      // Use provided access token, or fall back to stored token
      const token = accessToken || getAuthToken();
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(`${API_URL}/api/users/${userId}/tasks`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(task),
      });

      if (!res.ok) {
        return { error: `Failed to create task: ${res.status}` };
      }

      const data = await res.json();
      return { data };
    } catch (err) {
      return { error: 'Network error while creating task' };
    }
  },

  // UPDATE TASK
  async updateTask(
    userId: string,
    taskId: string,
    task: any,
    accessToken?: string
  ): Promise<ApiResult<any>> {
    try {
      // Use provided access token, or fall back to stored token
      const token = accessToken || getAuthToken();
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(
        `${API_URL}/api/users/${userId}/tasks/${taskId}`,
        {
          method: 'PUT',
          headers: headers,
          body: JSON.stringify(task),
        }
      );

      if (!res.ok) {
        return { error: `Failed to update task: ${res.status}` };
      }

      const data = await res.json();
      return { data };
    } catch (err) {
      return { error: 'Network error while updating task' };
    }
  },

  // DELETE TASK
  async deleteTask(
    userId: string,
    taskId: string,
    accessToken?: string
  ): Promise<ApiResult<null>> {
    try {
      // Use provided access token, or fall back to stored token
      const token = accessToken || getAuthToken();
      const headers: Record<string, string> = {};
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(
        `${API_URL}/api/users/${userId}/tasks/${taskId}`,
        { 
          method: 'DELETE',
          headers: headers
        }
      );

      if (!res.ok) {
        return { error: `Failed to delete task: ${res.status}` };
      }

      return { data: null };
    } catch (err) {
      return { error: 'Network error while deleting task' };
    }
  },

  // TOGGLE COMPLETE
  async updateTaskCompletion(
    userId: string,
    taskId: string,
    completed: boolean,
    accessToken?: string
  ): Promise<ApiResult<any>> {
    try {
      // Use provided access token, or fall back to stored token
      const token = accessToken || getAuthToken();
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(
        `${API_URL}/api/users/${userId}/tasks/${taskId}/complete`,
        {
          method: 'PATCH',
          headers: headers,
          body: JSON.stringify({ completed }),
        }
      );

      if (!res.ok) {
        return { error: `Failed to update task: ${res.status}` };
      }

      const data = await res.json();
      return { data };
    } catch (err) {
      return { error: 'Network error while updating completion' };
    }
  },
};
