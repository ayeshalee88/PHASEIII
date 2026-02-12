import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../contexts/AuthContext';
import Head from 'next/head';
import styles from '../styles/HomePage.module.css';
import Image from 'next/image';
import Script from 'next/script';

// Dynamic import for useSession to handle potential runtime issues in Vercel
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

export default function Home() {
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const { data: session, status } = getUseSession()();
  return (
    <>
      <Head>
        <title>Todoify - Professional Task Management</title>
        <meta name="description" content="Organize your life with beautiful sticky notes" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </Head>

      {/* Navigation */}
      <nav className={styles.navbar}>
        <div className={styles.navContainer}>
          <div className={styles.logo}>
            <Image src="/icons/ayismm.png"
                  alt="Smart Reminders"
                  width={50}
                  height={50} />

            <div className={styles.bookLogo}>
            </div>

            <span className={styles.logoText}>
              Todoify</span>
          </div>

          {/* Desktop Navigation */}
          <div className={styles.navLinks}>
            <a href="/signup" className={styles.navLogin}>Sign In</a>
            <a href="/login" className={styles.navSignup}>Dashboard</a>
          </div>

          {/* Mobile Menu Button */}
          <button
            className={styles.mobileMenuButton}
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? '✕' : '☰'}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className={styles.mobileMenu}>
            <a href="#features" className={styles.mobileMenuItem}>Features</a>
            <a href="/login" className={styles.mobileMenuLink}>Login</a>
            <a href="/signup" className={styles.mobileMenuSignup}>Get Started</a>
          </div>
        )}

      </nav>


      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroBackground}>
          <div className={styles.orb} style={{ top: '10%', left: '10%' }}></div>
          <div className={styles.orb} style={{ top: '60%', right: '15%' }}></div>
          <div className={styles.orb} style={{ bottom: '20%', left: '50%' }}></div>
        </div>

        <div className={styles.heroContent}>
          <div className={styles.badge}>
            <span className={styles.badgeDot}></span>
            Your Personal Task Manager
          </div>

          <h1 className={styles.heroTitle}>
            <span className={styles.typingText}>Organize Your Life with</span>
            <br />
            <span className={`${styles.typingText} ${styles.heroTitleGradient}`}>Beautiful Sticky Notes</span>
          </h1>
          <p className={styles.heroSubtitle}>
            Transform your tasks into colorful, organized sticky notes.
            Simple, visual, and delightfully effective task management.
          </p>

          <div className={styles.heroCta}>
            <a href="/signup" className={styles.ctaPrimary}>
              <span>Get Started Free</span>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </a>
            <a href="/login" className={styles.ctaSecondary}>
              Login
            </a>
          </div>

          <div className={styles.heroFeatures}>
            <div className={styles.heroFeatureItem}>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M7 10L9 12L13 8M19 10C19 14.9706 14.9706 19 10 19C5.02944 19 1 14.9706 1 10C1 5.02944 5.02944 1 10 1C14.9706 1 19 5.02944 19 10Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>No credit card</span>
            </div>
            <div className={styles.heroFeatureItem}>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M7 10L9 12L13 8M19 10C19 14.9706 14.9706 19 10 19C5.02944 19 1 14.9706 1 10C1 5.02944 5.02944 1 10 1C14.9706 1 19 5.02944 19 10Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>Free forever</span>
            </div>
          </div>
        </div>

        {/* Floating Sticky Notes Preview */}
        <div className={styles.heroPreview}>
          <div
            className={styles.stickyNote}
            style={{
              background: 'linear-gradient(135deg, #fef3c7, #fde68a)',
              top: '5%',
              left: '0%',
              zIndex: 3,
              transform: 'rotate(-6deg)',
              animationDelay: '0s'
            }}
          >
            <div className={styles.noteTape}></div>
            <div className={styles.noteCheck}>✓</div>
            <h4>Social Media Post</h4>
            <p>Create engaging content for Instagram and Twitter campaigns</p>
          </div>

          <div
            className={styles.stickyNote}
            style={{
              background: 'linear-gradient(135deg, #dbeafe, #93c5fd)',
              top: '30%',
              right: '5%',
              zIndex: 2,
              transform: 'rotate(5deg)',
              animationDelay: '2s'
            }}
          >
            <div className={styles.noteTape}></div>
            <div className={styles.noteCheck}>✓</div>
            <h4>Content Strategy</h4>
            <p>Outline Q1 content calendar and themes for the year</p>
          </div>

          <div
            className={styles.stickyNote}
            style={{
              background: 'linear-gradient(135deg, #fce7f3, #f9a8d4)',
              bottom: '8%',
              left: '10%',
              zIndex: 1,
              transform: 'rotate(-4deg)',
              animationDelay: '4s'
            }}
          >
            <div className={styles.noteTape}></div>
            <h4>Email & Texts</h4>
            <p>Follow up with clients about new proposals and updates</p>
          </div>
        </div>
      </section>



      {/* Visual Showcase Section */}
      <section className={styles.showcase}>
        <div className={styles.showcaseContainer}>
          <div className={styles.showcaseHeader}>
            <span className={styles.showcaseLabel}>Evaluation Of Todo</span>
            <h2 className={styles.showcaseTitle}>Your tasks, beautifully organized</h2>
            <p className={styles.showcaseSubtitle}>Experience the joy of visual task management with colorful sticky notes</p>
          </div>

          <div className={styles.showcaseGrid}>
            {/* Sticky Notes Demo */}
            <div className={styles.showcaseCard}>
              <div className={styles.showcaseImageWrapper}>
                <div className={styles.demoNote} style={{ background: 'linear-gradient(135deg, #fef3c7, #fde68a)', transform: 'rotate(-3deg)', top: '10%', left: '10%' }}>
                  <div className={styles.demoNoteTape}></div>
                  <div className={styles.demoNoteCheck}>✓</div>
                  <h4 className={styles.demoNoteTitle}>Meeting Notes</h4>
                  <p className={styles.demoNoteText}>Discuss Q4 strategy with team</p>
                  <span className={styles.demoNoteDate}>Today</span>
                </div>
                <div className={styles.demoNote} style={{ background: 'linear-gradient(135deg, #dbeafe, #93c5fd)', transform: 'rotate(2deg)', top: '25%', right: '15%' }}>
                  <div className={styles.demoNoteTape}></div>
                  <h4 className={styles.demoNoteTitle}>Design Review</h4>
                  <p className={styles.demoNoteText}>Review mockups for new feature</p>
                  <span className={styles.demoNoteDate}>Tomorrow</span>
                </div>
                <div className={styles.demoNote} style={{ background: 'linear-gradient(135deg, #fce7f3, #f9a8d4)', transform: 'rotate(-2deg)', bottom: '15%', left: '20%' }}>
                  <div className={styles.demoNoteTape}></div>
                  <div className={styles.demoNoteCheck}>✓</div>
                  <h4 className={styles.demoNoteTitle}>Email Campaign</h4>
                  <p className={styles.demoNoteText}>Send newsletter to subscribers</p>
                  <span className={styles.demoNoteDate}>Completed</span>
                </div>
                <div className={styles.demoNote} style={{ background: 'linear-gradient(135deg, #fed7aa, #fb923c)', transform: 'rotate(1deg)', bottom: '10%', right: '10%' }}>
                  <div className={styles.demoNoteTape}></div>
                  <h4 className={styles.demoNoteTitle}>Budget Report</h4>
                  <p className={styles.demoNoteText}>Finalize monthly expenses</p>
                  <span className={styles.demoNoteDate}>This Week</span>
                </div>
              </div>
            </div>

            {/* Feature Highlights */}
            <div className={styles.showcaseFeatures}>
              <div className={styles.showcaseFeatureItem}>
                <div className={styles.showcaseFeatureIcon}>
                  <Image src="/icons/bada.png"
                  alt="Quick Add"
                  width={180}
                  height={150} />
                </div>
                <div>
                  <h4>Calender</h4>
                  <p>Plan your task with our integrated calendar view</p>
                </div>
              </div>
              <div className={styles.showcaseFeatureItem}>
                <div className={styles.showcaseFeatureIcon}>
                  <Image src="/icons/unnamed.png"
                  alt="Quick Add"
                  width={180}
                  height={170} />
                </div>
                <div>
                  <h4>Quick Add,View,Update and Delete</h4>
                  <p>Create new tasks instantly while taking with AI</p>
                </div>
              </div>
              <div className={styles.showcaseFeatureItem}>
                <div className={styles.showcaseFeatureIcon}>
                  <Image src="/icons/ayis.png"
                  alt="Smart Reminders"
                  width={150}
                  height={150} />
                </div>
                <div>
                  <h4>Important Reminders</h4>
                  <p>Never miss important deadlines with intelligent notifications</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className={styles.ctaSection}>
        <div className={styles.ctaSectionContent}>
          <h2>Ready to get organized?</h2>
          <p>Join thousands using Todoify to manage their daily tasks</p>
          <a href="/signup" className={styles.ctaSectionButton}>
            <span>Start Using Todoify</span>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <div className={styles.footerBrand}>
            <div className={styles.bookSpine}></div>
            <div className={styles.bookPages}>
                <span className={styles.bookLine}></span>
                <span className={styles.bookLine}></span>
                <span className={styles.bookLine}></span>
            </div>
            <div className={styles.logo}>
            <span className={styles.logoText}>Todoify</span>
            </div>
          </div>
          <p className={styles.footerCopy}>© 2026 Todoify. All rights reserved.Powered by ayisha 💙✔️.</p>
        </div>
      </footer>
    </>
  );
}