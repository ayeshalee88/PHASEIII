import React from 'react';
import Head from 'next/head';
import Navigation from './Navigation';
import styles from './Layout.module.css';

type LayoutProps = {
  children: React.ReactNode;
  title?: string;
};

const Layout: React.FC<LayoutProps> = ({ children, title = 'Todo App' }) => {        
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="description" content="A full-stack todo application" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className={styles.container}>
        <Navigation />
        <main className={styles.main}>{children}</main>
        <footer className={styles.footer}>
          <p>Â© {new Date().getFullYear()} Todo App. All rights reserved.</p>        
        </footer>
      </div>
    </>
  );
};

export default Layout;