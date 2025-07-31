import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

// Simple error boundary for the entire app
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    console.error('React error caught:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h1>eHealth Platform</h1>
          <p>Sorry, we're experiencing technical difficulties. Please try again later.</p>
          <button onClick={() => window.location.reload()}>Reload Page</button>
        </div>
      )
    }

    return this.props.children
  }
}

try {
  const root = ReactDOM.createRoot(document.getElementById('root'))
  root.render(
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  )
} catch (error) {
  console.error('Failed to render React app:', error)
  // Load the static landing page as a fallback
  fetch('/static-landing.html')
    .then(response => response.text())
    .then(html => {
      document.open()
      document.write(html)
      document.close()
    })
    .catch(fetchError => {
      console.error('Failed to load static landing page:', fetchError)
      document.body.innerHTML = `
        <div style="padding: 20px; text-align: center;">
          <h1>eHealth Platform</h1>
          <p>Sorry, we're experiencing technical difficulties. Please try again later.</p>
          <button onclick="window.location.reload()">Reload Page</button>
        </div>
      `
    })
}