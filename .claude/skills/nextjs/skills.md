# Next.js Skills Guide

## Overview
Next.js is a React-based framework that enables functionality such as server-side rendering and generating static websites for React-based web applications. This guide covers essential Next.js concepts, patterns, and best practices.

## Key Concepts

### 1. Project Structure
- `pages/` directory contains route-based pages
- `components/` directory contains reusable React components
- `public/` directory for static assets
- `styles/` directory for global styles
- `api/` directory for API routes (Node.js edge runtime)

### 2. Routing
- File-based routing system using the `pages` directory
- Dynamic routes using `[param].js` convention
- Nested routes using folder structure
- Catch-all routes using `[...param].js`

### 3. Rendering Patterns
- Server-Side Rendering (SSR) with `getServerSideProps`
- Static Site Generation (SSG) with `getStaticProps` and `getStaticPaths`
- Client-Side Rendering (CSR) with React hooks
- Incremental Static Regeneration (ISR) for dynamic content

### 4. Data Fetching
- `getStaticProps`: Pre-render at build time
- `getStaticPaths`: Define dynamic static routes
- `getServerSideProps`: Server-render at request time
- SWR and React Query for client-side data fetching

### 5. Performance Optimization
- Automatic code splitting
- Built-in image optimization with `next/image`
- Font optimization
- Bundle analyzer for performance insights
- Lazy loading with `next/dynamic`

## Best Practices

### Component Development
- Use functional components with hooks
- Leverage React Context for state management
- Implement proper TypeScript interfaces
- Follow accessibility guidelines (ARIA attributes)

### Styling
- Use CSS Modules for scoped styles
- Leverage Tailwind CSS for utility-first styling
- Implement responsive design patterns
- Use `styled-jsx` for component-scoped CSS

### API Routes
- Place API endpoints in `pages/api/`
- Handle different HTTP methods in single files
- Implement proper error handling
- Use TypeScript for API handlers

### Deployment
- Optimize for Vercel deployment
- Configure custom server if needed
- Implement proper environment variable handling
- Set up proper caching headers

## Common Patterns

### Layouts
```jsx
export default function Layout({ children }) {
  return (
    <>
      <nav>...</nav>
      <main>{children}</main>
      <footer>...</footer>
    </>
  )
}
```

### Custom App
```jsx
import '../styles/globals.css'

function MyApp({ Component, pageProps }) {
  return <Component {...pageProps} />
}

export default MyApp
```

### Environment Variables
```javascript
// .env.local
NEXT_PUBLIC_BASE_URL=...
DB_HOST=...
```

## Error Handling
- Implement custom error pages (`pages/_error.js`)
- Use Error Boundary components
- Handle 404 and 500 errors appropriately
- Log errors properly for debugging

## Security Considerations
- Sanitize user inputs
- Prevent XSS attacks
- Implement proper CORS policies
- Secure API routes with authentication