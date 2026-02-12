import React from 'react';
import Link from 'next/link';
import { useAuth } from '../contexts/AuthContext';
import styles from './Navigation.module.css';

const Navigation: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <nav className={styles.navbar}>
      <div className={styles.navContainer}>
        <Link href="/" className={styles.logo}>
          Todo App
        </Link>

        <div className={styles.navLinks}>
          {isAuthenticated ? (
            <>
              <Link href="/dashboard" className={styles.navLink}>
                Dashboard
              </Link>
              <span className={styles.welcomeText}>Welcome, {user?.email}</span>
              <button onClick={logout} className={styles.logoutButton}>
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className={styles.navLink}>
                Login
              </Link>
              <Link href="/signup" className={`${styles.navLink} ${styles.signupButton}`}>
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;