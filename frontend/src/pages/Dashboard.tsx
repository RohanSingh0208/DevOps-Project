import { useEffect, useState, useCallback } from 'react'
import {
  Building2, Calendar, Wrench, AlertTriangle,
  CheckCircle, Clock, TrendingUp, Activity
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'
import { api } from '../api/client'
import type { DashboardStats } from '../types'
import { format } from 'date-fns'

const PIE_COLORS = ['#6366f1','#8b5cf6','#06b6d4','#10b981','#f59e0b','#ef4444','#ec4899']

const RESOURCE_TYPE_LABELS: Record<string, string> = {
  classroom: 'Classroom', laboratory: 'Laboratory', meeting_room: 'Meeting Room',
  projector: 'Projector', equipment: 'Equipment',
  sports_facility: 'Sports', library_room: 'Library',
}

function StatCard({ value, label, icon: Icon, colorClass }: {
  value: number; label: string; icon: React.ElementType; colorClass: string
}) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${colorClass}`}>
        <Icon size={22} />
      </div>
      <div className="stat-info">
        <div className="stat-value">{value.toLocaleString()}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  )
}

const statusBadge = (status: string) => (
  <span className={`badge badge-${status.replace('_', '')}`}>
    {status.replace('_', ' ')}
  </span>
)

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadStats = useCallback(async () => {
    try {
      setLoading(true)
      setError('')
      const data = await api.getDashboard()
      setStats(data)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadStats() }, [loadStats])

  const pieData = stats
    ? Object.entries(stats.resources_by_type).map(([key, val]) => ({
        name: RESOURCE_TYPE_LABELS[key] ?? key,
        value: val,
      }))
    : []

  const barData = stats
    ? [
        { name: 'Available', count: stats.available_resources, fill: '#10b981' },
        { name: 'Maintenance', count: stats.under_maintenance_resources, fill: '#f59e0b' },
        { name: 'Total', count: stats.total_resources, fill: '#6366f1' },
      ]
    : []

  if (loading) return (
    <div>
      <div className="page-header">
        <div className="skeleton" style={{ height: 32, width: 220, marginBottom: 8 }} />
        <div className="skeleton" style={{ height: 16, width: 320 }} />
      </div>
      <div className="stats-grid">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 100 }} />
        ))}
      </div>
    </div>
  )

  if (error) return (
    <div>
      <div className="page-header"><h1>Dashboard</h1></div>
      <div className="alert alert-error">
        <AlertTriangle size={18} />
        Failed to load dashboard: {error}. Ensure the backend is running.
      </div>
    </div>
  )

  return (
    <div>
      <div className="page-header">
        <h1>Campus Resource Hub</h1>
        <p>Monitor facility availability, reservations, and maintenance across campus</p>
      </div>

      {/* KPI Stats */}
      <div className="stats-grid">
        <StatCard value={stats!.total_resources}            label="Total Resources"         icon={Building2}     colorClass="indigo" />
        <StatCard value={stats!.available_resources}        label="Available Now"            icon={CheckCircle}   colorClass="green"  />
        <StatCard value={stats!.total_reservations}         label="Total Reservations"       icon={Calendar}      colorClass="cyan"   />
        <StatCard value={stats!.pending_reservations}       label="Pending Reservations"     icon={Clock}         colorClass="amber"  />
        <StatCard value={stats!.open_maintenance_requests}  label="Open Maintenance"         icon={Wrench}        colorClass="red"    />
        <StatCard value={stats!.critical_maintenance_requests} label="Critical Issues"       icon={AlertTriangle} colorClass="red"    />
      </div>

      {/* Charts */}
      <div className="charts-grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Resource Status Overview</span>
            <TrendingUp size={18} style={{ color: 'var(--color-text-dim)' }} />
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={barData} barSize={36}>
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ background: '#16162a', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 10 }}
                labelStyle={{ color: '#e2e8f0' }}
                cursor={{ fill: 'rgba(99,102,241,0.05)' }}
              />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {barData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Resources by Type</span>
            <Activity size={18} style={{ color: 'var(--color-text-dim)' }} />
          </div>
          {pieData.length === 0 ? (
            <div className="empty-state" style={{ padding: '40px 0' }}>
              <p>No resource data yet</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={3} dataKey="value">
                  {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip
                  contentStyle={{ background: '#16162a', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 10 }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Legend iconType="circle" iconSize={10} wrapperStyle={{ fontSize: 12, color: '#94a3b8' }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)' }}>
        {/* Recent Reservations */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Recent Reservations</span>
            <Calendar size={18} style={{ color: 'var(--color-text-dim)' }} />
          </div>
          {stats!.recent_reservations.length === 0 ? (
            <div className="empty-state" style={{ padding: '24px 0' }}>
              <p style={{ fontSize: 13 }}>No reservations yet</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {stats!.recent_reservations.map(r => (
                <div key={r.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--color-border)' }}>
                  <div>
                    <p style={{ fontSize: 13, fontWeight: 600 }}>{r.resource?.name ?? `Resource #${r.resource_id}`}</p>
                    <p style={{ fontSize: 12, color: 'var(--color-text-muted)', marginTop: 2 }}>
                      {r.requester_name} · {format(new Date(r.start_time), 'MMM d, HH:mm')}
                    </p>
                  </div>
                  {statusBadge(r.status)}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Maintenance */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Recent Maintenance</span>
            <Wrench size={18} style={{ color: 'var(--color-text-dim)' }} />
          </div>
          {stats!.recent_maintenance.length === 0 ? (
            <div className="empty-state" style={{ padding: '24px 0' }}>
              <p style={{ fontSize: 13 }}>No maintenance requests</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {stats!.recent_maintenance.map(m => (
                <div key={m.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: '1px solid var(--color-border)' }}>
                  <div style={{ flex: 1, marginRight: 12 }}>
                    <p style={{ fontSize: 13, fontWeight: 600 }}>{m.title}</p>
                    <p style={{ fontSize: 12, color: 'var(--color-text-muted)', marginTop: 2 }}>
                      {m.resource?.name ?? `Resource #${m.resource_id}`}
                    </p>
                  </div>
                  <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                    <span className={`badge badge-${m.priority}`}>{m.priority}</span>
                    {statusBadge(m.status)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
