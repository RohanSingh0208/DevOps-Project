import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Building2, Calendar, Wrench, Menu, X
} from 'lucide-react'
import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Resources from './pages/Resources'
import Reservations from './pages/Reservations'
import Maintenance from './pages/Maintenance'

const navItems = [
  { to: '/',              label: 'Dashboard',    icon: LayoutDashboard },
  { to: '/resources',    label: 'Resources',    icon: Building2       },
  { to: '/reservations', label: 'Reservations', icon: Calendar        },
  { to: '/maintenance',  label: 'Maintenance',  icon: Wrench          },
]

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  return (
    <div className="app-layout">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="modal-overlay"
          style={{ zIndex: 99 }}
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-logo">
          <div className="sidebar-logo-icon">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M3 16V9l7-5 7 5v7h-4v-4H7v4H3z" fill="white"/>
            </svg>
          </div>
          <div className="sidebar-logo-text">
            <h1>Campus Hub</h1>
            <p>Resource Manager</p>
          </div>
        </div>

        <nav className="sidebar-nav">
          <span className="sidebar-section-label">Navigation</span>
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div style={{ padding: '12px 24px', borderTop: '1px solid var(--color-border)', marginTop: 'auto' }}>
          <p style={{ fontSize: '11px', color: 'var(--color-text-dim)' }}>
            Campus Resource Hub v1.0
          </p>
          <p style={{ fontSize: '10px', color: 'var(--color-text-dim)', marginTop: '2px' }}>
            DevSecOps Capstone
          </p>
        </div>
      </aside>

      {/* Mobile menu toggle */}
      <button
        className="btn btn-secondary btn-icon"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        style={{
          position: 'fixed', top: 16, left: 16, zIndex: 150,
          display: 'none',
        }}
        id="mobile-menu-btn"
        aria-label="Toggle menu"
      >
        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Main content */}
      <main className="main-content">
        <Routes>
          <Route path="/"              element={<Dashboard />}    />
          <Route path="/resources"     element={<Resources />}    />
          <Route path="/reservations"  element={<Reservations />} />
          <Route path="/maintenance"   element={<Maintenance />}  />
          <Route path="*"              element={<Dashboard />}    />
        </Routes>
      </main>
    </div>
  )
}
