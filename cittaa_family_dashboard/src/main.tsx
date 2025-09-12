import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

function initializeApp() {
  console.log('Initializing React app...')
  const rootElement = document.getElementById('root')
  
  if (!rootElement) {
    console.error('Root element not found!')
    return
  }
  
  console.log('Root element found, creating React root...')
  const root = createRoot(rootElement)
  
  root.render(
    <StrictMode>
      <App />
    </StrictMode>
  )
  
  console.log('React app rendered successfully')
}

if (document.readyState === 'loading') {
  console.log('DOM still loading, waiting for DOMContentLoaded...')
  document.addEventListener('DOMContentLoaded', initializeApp)
} else {
  console.log('DOM already loaded, initializing React immediately...')
  initializeApp()
}
