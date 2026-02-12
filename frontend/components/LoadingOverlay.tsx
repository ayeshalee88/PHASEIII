import React from 'react';
import styles from '../styles/Login.module.css';

interface LoadingOverlayProps {
  message?: string;
}

const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  message = 'Please wait...',
}) => {
  return (
    <div className={styles.overlay}>
      <div className={styles.loaderCard}>
        <div className={styles.spinner}></div>
        <p className={styles.text}>{message}</p>
      </div>
    </div>
  );
};

export default LoadingOverlay;
