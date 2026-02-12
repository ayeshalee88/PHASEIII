import { useState, useEffect, useRef } from 'react';
import { GetServerSideProps } from 'next';
import { getServerSession } from "next-auth/next";
import { authOptions } from "../../lib/auth";
import TaskCard from '../components/TaskCard';
import TaskForm from '../components/TaskForm';
import { apiClient } from '../lib/api';
import Head from 'next/head';
import { useRouter } from 'next/router';
import styles from '../styles/Dashboard.module.css';
import Image from 'next/image';
import { useTasks } from '../contexts/TaskContext';

// Dynamic imports for next-auth functions to handle potential runtime issues in Vercel
const getSignOut = () => {
  try {
    if (typeof window !== 'undefined') {
      const { signOut } = require('next-auth/react');
      return signOut;
    }
  } catch (error) {
    console.warn('next-auth signOut not available:', error);
    return () => Promise.resolve();
  }
  return () => Promise.resolve();
};

const getUseSession = () => {
  try {
    if (typeof window !== 'undefined') {
      const { useSession } = require('next-auth/react');
      return useSession;
    }
  } catch (error) {
    console.warn('next-auth useSession not available:', error);
    return () => [null, 'loading'];
  }
  // Return a mock session hook for SSR
  return () => [null, 'loading'];
};

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
}

interface DeletedTask extends Task {
  deleted_at: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'tool';
  content: string;
  timestamp: string;
  tool_calls?: Array<{
    id: string;
    function: {
      name: string;
      arguments: string;
    };
    type: string;
  }>;
}

interface ChatResponse {
  conversation_id: string;
  message: string;
  tool_calls?: Array<{
    id: string;
    function: {
      name: string;
      arguments: string;
    };
    type: string;
  }>;
  timestamp: string;
}

interface DashboardProps {
  user: {
    id: string;
    email: string;
  };
}

export default function Dashboard({ user }: DashboardProps) {
  const router = useRouter();
  const { tasks, loading: contextLoading, error: contextError, fetchTasks, createTask, updateTask, deleteTask, toggleTaskCompletion } = useTasks();
  const [loading, setLoading] = useState(false); // Local loading state for form operations
  const [deletedTasks, setDeletedTasks] = useState<DeletedTask[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'important' | 'completed'>('all');
  const [view, setView] = useState<'grid' | 'calendar'>('grid');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { data: session } = getUseSession()();
  const [showDeletedModal, setShowDeletedModal] = useState(false);
  const [currentMonth, setCurrentMonth] = useState(new Date());

  // AI Chat State
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  // Fetch tasks when user and session are ready
  useEffect(() => {
    if (session?.user?.id) {
      console.log('Session ready, fetching tasks for user:', session.user.id);
      fetchTasks(session.user.id, session.accessToken);
    }
  }, [session?.user?.id]); // Only re-run when session user ID changes

  const handleCreateTask = async (taskData: Partial<Task>) => {
    if (!session?.user?.id) return;
    try {
      setLoading(true);
      console.log('Creating task:', taskData);
      await createTask(session.user.id, taskData, session.accessToken);
      setShowForm(false);
    } catch (err: any) {
      console.error('Create task error:', err);
      setError(`Failed to create task: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateTask = async (taskData: Task) => {
    if (!session?.user?.id) return;
    try {
      setLoading(true);
      await updateTask(session.user.id, taskData.id, taskData, session.accessToken);
      setEditingTask(null);
      setShowForm(false);
    } catch (err: any) {
      console.error('Update task error:', err);
      setError(`Failed to update task: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!window.confirm('Delete this task?')) return;
    if (!session?.user?.id) return;

    try {
      setLoading(true);
      const taskToDelete = tasks.find(t => t.id === taskId);
      if (taskToDelete) {
        setDeletedTasks([...deletedTasks, {
          ...taskToDelete,
          deleted_at: new Date().toISOString()
        }]);
      }

      await deleteTask(session.user.id, taskId, session.accessToken);
    } catch (err: any) {
      console.error('Delete task error:', err);
      setError(`Failed to delete task: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleComplete = async (taskId: string, completed: boolean) => {
    if (!session?.user?.id) return;
    try {
      setLoading(true);
      await toggleTaskCompletion(session.user.id, taskId, completed, session.accessToken);
    } catch (err: any) {
      console.error('Error updating task:', err);
      setError(`Failed to update task: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    const signOutFunc = getSignOut();
    await signOutFunc({ callbackUrl: '/' });
  };

  const handleRestoreTask = async (taskId: string) => {
    const taskToRestore = deletedTasks.find(t => t.id === taskId);
    if (taskToRestore) {
      const { deleted_at, ...taskWithoutDeletedAt } = taskToRestore;
      // Re-create the task
      await handleCreateTask(taskWithoutDeletedAt);
      setDeletedTasks(deletedTasks.filter(t => t.id !== taskId));
    }
  };

  const handlePermanentDelete = (taskId: string) => {
    if (!window.confirm('Permanently delete this task? This cannot be undone.')) return;
    setDeletedTasks(deletedTasks.filter(t => t.id !== taskId));
  };

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    return { daysInMonth, startingDayOfWeek };
  };

  const getTasksForDate = (date: Date) => {
    return tasks.filter(task => {
      const taskDate = new Date(task.created_at);
      return taskDate.toDateString() === date.toDateString();
    });
  };

  const getColorGradient = (index: number) => {
    const colors = [
      'linear-gradient(135deg, #fef3c7, #fde68a)',
      'linear-gradient(135deg, #dbeafe, #93c5fd)',
      'linear-gradient(135deg, #fce7f3, #f9a8d4)',
      'linear-gradient(135deg, #d1fae5, #6ee7b7)',
    ];
    return colors[index % 4];
  };

  // Filter tasks based on current filter
  const filteredTasks = tasks.filter(task => {
    if (filter === 'completed') return task.completed;
    if (filter === 'important') return !task.completed;
    return true; // 'all'
  });

  const { daysInMonth, startingDayOfWeek } = getDaysInMonth(currentMonth);

  const previousMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  // AI Chat Functions
  const handleSendMessage = async () => {
    // Debug logging
    console.log('Session object:', session);
    console.log('Session access token:', session?.accessToken);
    console.log('Session user:', session?.user);
    console.log('Session user ID:', session?.user?.id);

    if (!inputMessage.trim() || chatLoading) {
      console.log('Message validation failed:', {
        hasInput: !!inputMessage.trim(),
        isLoading: chatLoading,
        hasSession: !!session,
        hasUserId: !!session?.user?.id
      });
      return;
    }

    // Validate that we have the required session data
    if (!session?.user?.id) {
      console.error('No user ID in session');
      setChatError('Authentication error: No user ID found');
      return;
    }

    if (!session?.accessToken) {
      console.error('No access token in session');
      alert('Authentication error: Access token not found. Please log out and log back in.');
      setChatError('Authentication error: Access token not found');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setChatLoading(true);
    setChatError(null);

    try {
      // Get the actual user ID from the session
      const userId = session.user.id;

      // Use the same API_URL as defined in api.ts
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      // Function to make the API call
      const makeChatRequest = async (token: string) => {
        console.log('Making chat API call to:', `${API_URL}/api/${userId}/chat`);
        console.log('Using access token:', token.substring(0, 10) + '...'); // Log only first 10 chars for security

        return await fetch(`${API_URL}/api/${userId}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ message: inputMessage })
        });
      };

      let response = await makeChatRequest(session.accessToken);

      // If we get a 401, the token is likely expired, so we need to re-authenticate
      if (response.status === 401) {
        console.log('Received 401, token likely expired. Redirecting to login...');

        // Show a user-friendly message
        alert('Your session has expired. Please log in again to continue using the AI assistant.');

        // Redirect to login
        const signOutFunc = getSignOut();
        await signOutFunc({ callbackUrl: '/login' });
        return; // Exit early since we're redirecting
      }

      console.log('Chat API response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text(); // Get raw text first
        console.error('Chat API error response text:', errorText);

        let errorData = {};
        try {
          // Try to parse as JSON
          errorData = JSON.parse(errorText);
        } catch (e) {
          // If it's not JSON, use the raw text
          errorData = { detail: errorText };
        }

        console.error('Chat API error response:', errorData);
        throw new Error((errorData as any).detail || `HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      console.log('Chat API success response:', data);

      // Set conversation ID if not already set
      if (!conversationId) {
        setConversationId(data.conversation_id);
      }

      // Add assistant response
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.message,
        timestamp: data.timestamp || new Date().toISOString(),
        tool_calls: data.tool_calls
      };

      setChatMessages(prev => [...prev, assistantMessage]);

      // Parse the response to determine if any task operations were performed
      if (data.tool_calls && Array.isArray(data.tool_calls)) {
        console.log('Tool calls detected, refreshing tasks to sync with backend...');
      }
      
      // Operations are handled by the backend, so just refresh the task list after any AI interaction
      // This ensures the frontend is always in sync with the backend state
      setLoading(true); // Show loading state during refresh
      try {
        // Small delay to allow backend operations to complete
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Refresh tasks to sync with backend operations (whether tool calls happened or not)
        await fetchTasks(session.user.id, session.accessToken);
      } catch (error) {
        console.error('Error refreshing tasks after AI interaction:', error);
      } finally {
        setLoading(false); // Hide loading state after refresh
      }
    } catch (err: any) {
      console.error('Error sending message:', err);
      setChatError(err.message || 'Failed to send message');

      // Add error message to chat
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Error: ${err.message || 'Failed to process your request'}`,
        timestamp: new Date().toISOString()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Prevent rendering if session is not ready to avoid hydration errors
  if (!session) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading...</div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Dashboard - Todoify</title>
      </Head>
      <div className={styles.container}>
        {/* Mobile Menu Button */}
        <button 
          className={styles.mobileMenuButton}
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle menu"
        >
          ☰
        </button>

        {/* Sidebar */}
        <aside className={`${styles.sidebar} ${sidebarOpen ? styles.open : ''}`}>
          <div className={styles.sidebarHeader}>
            <h2 className={styles.sidebarTitle}>
              <Image src="/icons/ayismm.png" 
                                alt="Smart Reminders" 
                                width={20} 
                                height={20} /> Todoify</h2>
            <p className={styles.sidebarEmail}>{user?.email}</p>
          </div>

          <nav className={styles.nav}>
            <button 
              onClick={() => { setFilter('all'); setSidebarOpen(false); }}
              className={`${styles.navLink} ${filter === 'all' ? styles.navLinkActive : ''}`}
            >
              <span className={styles.navIcon}>📋</span>
              <span>All Tasks</span>
              <span className={styles.badge}>{tasks.length}</span>
            </button>
            <button 
              onClick={() => { setFilter('important'); setSidebarOpen(false); }}
              className={`${styles.navLink} ${filter === 'important' ? styles.navLinkActive : ''}`}
            >
              <span className={styles.navIcon}>⭐</span>
              <span>Active</span>
              <span className={styles.badge}>{tasks.filter(t => !t.completed).length}</span>
            </button>
            <button 
              onClick={() => { setFilter('completed'); setSidebarOpen(false); }}
              className={`${styles.navLink} ${filter === 'completed' ? styles.navLinkActive : ''}`}
            >
              <span className={styles.navIcon}>✅</span>
              <span>Completed</span>
              <span className={styles.badge}>{tasks.filter(t => t.completed).length}</span>
            </button>
            <button 
              onClick={() => { setShowDeletedModal(true); setSidebarOpen(false); }}
              className={styles.navLink}
            >
              <span className={styles.navIcon}>🗑️</span>
              <span>Deleted</span>
              <span className={styles.badge}>{deletedTasks.length}</span>
            </button>
            <button 
              onClick={() => { setShowChat(true); setSidebarOpen(false); }}
              className={styles.navLink}
            >
              <span className={styles.navIcon}>👨🏻‍💻</span>
              <span>Talk to AI</span>
            </button>
          </nav>

          <div className={styles.viewToggle}>
            <button 
              onClick={() => setView('grid')}
              className={view === 'grid' ? styles.viewToggleActive : ''}
            >
              Grid
            </button>
            <button 
              onClick={() => setView('calendar')}
              className={view === 'calendar' ? styles.viewToggleActive : ''}
            >
              Calendar
            </button>
          </div>

          <button onClick={handleLogout} className={styles.logoutButton}>
            Sign Out
          </button>
        </aside>

        {/* Main Content */}
        <main className={styles.mainContent}>
          <div className={styles.contentWrapper}>
            <div className={styles.header}>
              <h1 className={styles.pageTitle}>
                {view === 'calendar' ? 'Calendar View' : 'My Tasks'}
              </h1>
              <button
                onClick={() => {
                  setEditingTask(null);
                  setShowForm(true);
                }}
                className={styles.addButton}
              >
                + New Task
              </button>
            </div>

            {(error || contextError) && (
              <div className={styles.error}>
                <span>{error || contextError}</span>
                <button onClick={() => {setError(null);}} className={styles.errorButton}>×</button>
              </div>
            )}

            {/* Grid View */}
            {view === 'grid' && (
              <div className={styles.taskGrid}>
                {/* Add New Card */}
                <button
                  onClick={() => {
                    setEditingTask(null);
                    setShowForm(true);
                  }}
                  className={styles.addCard}
                >
                  <div className={styles.addCardIcon}>+</div>
                  <p className={styles.addCardText}>Add New Task</p>
                </button>

                {/* Task Cards */}
                {(loading || contextLoading) ? (
                  <div className={styles.loading}>Loading tasks...</div>
                ) : filteredTasks.length === 0 ? (
                  <div className={styles.emptyState}>
                    <p className={styles.emptyStateText}>
                      {filter === 'completed' ? 'No completed tasks yet!' :
                       filter === 'important' ? 'No active tasks!' :
                       'No tasks yet. Create your first task!'}
                    </p>
                  </div>
                ) : (
                  filteredTasks.map((task, index) => (
                    <TaskCard
                      key={task.id}
                      task={task}
                      colorIndex={index % 4}
                      onToggleComplete={handleToggleComplete}
                      onDelete={handleDeleteTask}
                      onEdit={(t:any) => {
                        setEditingTask(t);
                        setShowForm(true);
                      }}
                    />
                  ))
                )}
              </div>
            )}

            {/* Calendar View */}
            {view === 'calendar' && (
              <div className={styles.calendar}>
                <div className={styles.calendarHeader}>
                  <button onClick={previousMonth} className={styles.calendarNav}>‹</button>
                  <h2 className={styles.calendarMonth}>
                    {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                  </h2>
                  <button onClick={nextMonth} className={styles.calendarNav}>›</button>
                </div>

                <div className={styles.calendarGrid}>
                  {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                    <div key={day} className={styles.calendarDayHeader}>{day}</div>
                  ))}
                  
                  {Array.from({ length: startingDayOfWeek }, (_, i) => (
                    <div key={`empty-${i}`} className={`${styles.calendarCell} ${styles.empty}`}></div>
                  ))}
                  
                  {Array.from({ length: daysInMonth }, (_, i) => {
                    const dayNumber = i + 1;
                    const currentDate = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), dayNumber);
                    const dayTasks = getTasksForDate(currentDate);
                    const isToday = currentDate.toDateString() === new Date().toDateString();
                    
                    return (
                      <div key={dayNumber} className={`${styles.calendarCell} ${isToday ? styles.today : ''}`}>
                        <div className={styles.calendarDate}>{dayNumber}</div>
                        <div className={styles.calendarTasks}>
                          {dayTasks.slice(0, 3).map((task, idx) => (
                            <div 
                              key={task.id} 
                              className={styles.calendarTask}
                              style={{ background: getColorGradient(idx) }}
                            >
                              {task.title}
                            </div>
                          ))}
                          {dayTasks.length > 3 && (
                            <div className={styles.calendarMore}>+{dayTasks.length - 3} more</div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </main>

        {/* Modal Form */}
        {showForm && (
          <div className={styles.modalOverlay}>
            <div className={styles.modalContent}>
              <h2 className={styles.modalTitle}>
                {editingTask ? 'Edit Task' : 'New Task'}
              </h2>
              <TaskForm
                task={editingTask || undefined}
                onSubmit={editingTask ? handleUpdateTask as any : handleCreateTask}
                onCancel={() => {
                  setShowForm(false);
                  setEditingTask(null);
                }}
              />
            </div>
          </div>
        )}

        {/* Deleted Tasks Modal */}
        {showDeletedModal && (
          <div className={styles.modalOverlay} onClick={() => setShowDeletedModal(false)}>
            <div className={styles.deletedModal} onClick={(e) => e.stopPropagation()}>
              <div className={styles.deletedModalHeader}>
                <h2>Deleted Tasks</h2>
                <button onClick={() => setShowDeletedModal(false)} className={styles.modalClose}>×</button>
              </div>
              <div className={styles.deletedList}>
                {deletedTasks.length === 0 ? (
                  <p className={styles.emptyStateText}>No deleted tasks</p>
                ) : (
                  deletedTasks.map(task => (
                    <div key={task.id} className={styles.deletedItem}>
                      <div>
                        <h3>{task.title}</h3>
                        <p>{task.description}</p>
                        <small>Deleted: {new Date(task.deleted_at).toLocaleDateString()}</small>
                      </div>
                      <div className={styles.deletedActions}>
                        <button onClick={() => handleRestoreTask(task.id)} className={styles.restoreButton}>
                          Restore
                        </button>
                        <button onClick={() => handlePermanentDelete(task.id)} className={styles.permanentDeleteButton}>
                          Delete Forever
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* AI Chat Modal */}
        {showChat && (
          <div className={styles.chatModalOverlay} onClick={() => setShowChat(false)}>
            <div className={styles.chatModal} onClick={(e) => e.stopPropagation()}>
              <div className={styles.chatModalHeader}>
                <div className={styles.headerLeft}>
                  <Image src="/icons/ayismm.png"
                    alt="Todo Assistant"
                    width={24}
                    height={24} />
                  <h2>AI Todo Assistant</h2>
                </div>
                <button 
                  onClick={() => setShowChat(false)} 
                  className={styles.modalClose}
                >
                  ×
                </button>
              </div>

              <div className={styles.chatMessages}>
                {chatMessages.length === 0 ? (
                  <div className={styles.welcomeMessage}>
                    <h3>Hello {user?.email}!</h3>
                    <p>How can I help you with your tasks today?</p>
                    <div className={styles.suggestions}>
                      <div>Add a task called "Buy groceries"</div>
                      <div>Show me my tasks</div>
                      <div>Mark task #1 as complete</div>
                      <div>Delete task #2</div>
                    </div>
                  </div>
                ) : (
                  chatMessages.map((message) => (
                    <div
                      key={message.id}
                      className={`${styles.message} ${styles[`${message.role}Message`]}`}
                    >
                      <div className={styles.messageContent}>
                        <div className={styles.messageText}>{message.content}</div>
                        {message.tool_calls && message.tool_calls.length > 0 && (
                          <div className={styles.toolCalls}>
                            {message.tool_calls.map((call, index) => (
                              <div key={index} className={styles.toolCall}>
                                <strong>Tool:</strong> {call.function.name}
                                <br />
                                <strong>Args:</strong> {call.function.arguments}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className={styles.messageTimestamp}>
                        {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  ))
                )}
                {chatLoading && (
                  <div className={`${styles.message} ${styles.assistantMessage}`}>
                    <div className={styles.messageContent}>
                      <div className={styles.typingIndicator}>
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {chatError && (
                <div className={styles.error}>
                  <span>{chatError}</span>
                  <button onClick={() => setChatError(null)} className={styles.errorButton}>×</button>
                </div>
              )}

              <div className={styles.chatInputArea}>
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Message the AI assistant..."
                  className={styles.chatInput}
                  rows={1}
                  disabled={chatLoading}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={chatLoading || !inputMessage.trim()}
                  className={`${styles.sendButton} ${chatLoading ? styles.disabledButton : ''}`}
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

// Server-side authentication check
export const getServerSideProps: GetServerSideProps = async (context) => {
  const session = await getServerSession(context.req, context.res, authOptions);

  // If no session, redirect to login
  if (!session || !session.user) {
    return {
      redirect: {
        destination: '/login',
        permanent: false,
      },
    };
  }

  // Return user data to the page
  return {
    props: {
      user: {
        id: session.user.id,
        email: session.user.email || '',
      },
    },
  };
};