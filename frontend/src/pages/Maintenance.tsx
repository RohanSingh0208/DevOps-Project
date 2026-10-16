import { useEffect, useState, useCallback } from 'react'
import { Wrench, Plus, X, Edit2, Trash2 } from 'lucide-react'
import { format } from 'date-fns'
import { api } from '../api/client'
import type { MaintenanceRequest, MaintenancePriority, MaintenanceStatus, Resource } from '../types'

const PRIORITY_OPTIONS: { value: MaintenancePriority; label: string }[] = [
  { value: 'low', label: 'Low' }, { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' }, { value: 'critical', label: 'Critical' },
]

const STATUS_OPTIONS: { value: MaintenanceStatus; label: string }[] = [
  { value: 'open', label: 'Open' }, { value: 'in_progress', label: 'In Progress' },
  { value: 'resolved', label: 'Resolved' }, { value: 'closed', label: 'Closed' },
]

const emptyForm = {
  resource_id: '', reported_by: '', reporter_email: '',
  title: '', description: '', priority: 'medium' as MaintenancePriority,
  status: 'open' as MaintenanceStatus, resolution_notes: '',
}

export default function Maintenance() {
  const [requests, setRequests] = useState<MaintenanceRequest[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editTarget, setEditTarget] = useState<MaintenanceRequest | null>(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [priorityFilter, setPriorityFilter] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (statusFilter) params.status = statusFilter
      if (priorityFilter) params.priority = priorityFilter
      const [maint, res] = await Promise.all([
        api.getMaintenance(params),
        api.getResources(),
      ])
      setRequests(maint)
      setResources(res)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [statusFilter, priorityFilter])

  useEffect(() => { load() }, [load])

  const openCreate = () => {
    setEditTarget(null)
    setForm(emptyForm)
    setFormError('')
    setShowModal(true)
  }

  const openEdit = (m: MaintenanceRequest) => {
    setEditTarget(m)
    setForm({
      resource_id: m.resource_id.toString(),
      reported_by: m.reported_by, reporter_email: m.reporter_email,
      title: m.title, description: m.description,
      priority: m.priority, status: m.status,
      resolution_notes: m.resolution_notes ?? '',
    })
    setFormError('')
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setFormError('')
    try {
      const payload = { ...form, resource_id: parseInt(form.resource_id) }
      if (editTarget) {
        await api.updateMaintenance(editTarget.id, payload)
        setSuccess('Maintenance request updated')
      } else {
        await api.createMaintenance(payload as never)
        setSuccess('Maintenance request submitted')
      }
      setShowModal(false)
      load()
    } catch (e) {
      setFormError((e as Error).message)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this maintenance request?')) return
    try {
      await api.deleteMaintenance(id)
      setSuccess('Request deleted')
      load()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  const getResourceName = (id: number) => resources.find(r => r.id === id)?.name ?? `#${id}`

  return (
    <div>
      <div className="page-header">
        <h1>Maintenance Requests</h1>
        <p>Report and track facility maintenance issues across campus</p>
      </div>

      {error && <div className="alert alert-error"><X size={16}/>{error}<button onClick={() => setError('')} style={{ marginLeft: 'auto' }}><X size={14}/></button></div>}
      {success && <div className="alert alert-success">{success}<button onClick={() => setSuccess('')} style={{ marginLeft: 'auto' }}><X size={14}/></button></div>}

      <div className="filter-bar">
        <select id="maint-status-filter" className="form-select" value={statusFilter} onChange={e => setStatusFilter(e.target.value)} style={{ maxWidth: 180 }}>
          <option value="">All Statuses</option>
          {STATUS_OPTIONS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
        </select>
        <select id="maint-priority-filter" className="form-select" value={priorityFilter} onChange={e => setPriorityFilter(e.target.value)} style={{ maxWidth: 180 }}>
          <option value="">All Priorities</option>
          {PRIORITY_OPTIONS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
        </select>
        <button id="add-maintenance-btn" className="btn btn-primary" onClick={openCreate}>
          <Plus size={16} /> Report Issue
        </button>
      </div>

      <div className="card">
        {loading ? (
          <div className="loading-spinner"><div className="spinner" /></div>
        ) : requests.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon"><Wrench size={28} /></div>
            <h3>No maintenance requests</h3>
            <p>Report a maintenance issue to get started.</p>
            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={openCreate}>
              <Plus size={16} /> Report Issue
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Resource</th>
                  <th>Title</th>
                  <th>Reported By</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {requests.map(m => (
                  <tr key={m.id}>
                    <td style={{ color: 'var(--color-text-dim)' }}>#{m.id}</td>
                    <td style={{ fontWeight: 600 }}>{m.resource?.name ?? getResourceName(m.resource_id)}</td>
                    <td>
                      <div style={{ fontSize: 13, fontWeight: 500 }}>{m.title}</div>
                      <div style={{ fontSize: 11, color: 'var(--color-text-muted)', marginTop: 2 }}>
                        {m.description.slice(0, 60)}{m.description.length > 60 ? '…' : ''}
                      </div>
                    </td>
                    <td>
                      <div style={{ fontSize: 13 }}>{m.reported_by}</div>
                      <div style={{ fontSize: 11, color: 'var(--color-text-muted)' }}>{m.reporter_email}</div>
                    </td>
                    <td><span className={`badge badge-${m.priority}`}>{m.priority}</span></td>
                    <td><span className={`badge badge-${m.status}`}>{m.status.replace('_', ' ')}</span></td>
                    <td style={{ whiteSpace: 'nowrap', fontSize: 12 }}>
                      {format(new Date(m.created_at), 'MMM d, yyyy')}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button id={`edit-maint-${m.id}`} className="btn btn-secondary btn-sm btn-icon" onClick={() => openEdit(m)} title="Edit"><Edit2 size={13}/></button>
                        <button id={`delete-maint-${m.id}`} className="btn btn-danger btn-sm btn-icon" onClick={() => handleDelete(m.id)} title="Delete"><Trash2 size={13}/></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2 className="modal-title">{editTarget ? 'Update Request' : 'Report Maintenance Issue'}</h2>
              <button className="btn btn-secondary btn-icon" onClick={() => setShowModal(false)}><X size={18}/></button>
            </div>
            {formError && <div className="alert alert-error"><X size={14}/>{formError}</div>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Affected Resource *</label>
                <select id="maint-resource" className="form-select" required value={form.resource_id}
                  onChange={e => setForm(f => ({ ...f, resource_id: e.target.value }))}>
                  <option value="">Select resource…</option>
                  {resources.map(r => <option key={r.id} value={r.id}>{r.name} — {r.location}</option>)}
                </select>
              </div>
              <div className="form-grid-2">
                <div className="form-group">
                  <label className="form-label">Your Name *</label>
                  <input id="maint-name" className="form-input" required value={form.reported_by}
                    onChange={e => setForm(f => ({ ...f, reported_by: e.target.value }))} placeholder="Full name" />
                </div>
                <div className="form-group">
                  <label className="form-label">Email *</label>
                  <input className="form-input" type="email" required value={form.reporter_email}
                    onChange={e => setForm(f => ({ ...f, reporter_email: e.target.value }))} placeholder="you@university.edu" />
                </div>
                <div className="form-group">
                  <label className="form-label">Priority *</label>
                  <select id="maint-priority" className="form-select" value={form.priority}
                    onChange={e => setForm(f => ({ ...f, priority: e.target.value as MaintenancePriority }))}>
                    {PRIORITY_OPTIONS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
                  </select>
                </div>
                {editTarget && (
                  <div className="form-group">
                    <label className="form-label">Status</label>
                    <select className="form-select" value={form.status}
                      onChange={e => setForm(f => ({ ...f, status: e.target.value as MaintenanceStatus }))}>
                      {STATUS_OPTIONS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                    </select>
                  </div>
                )}
              </div>
              <div className="form-group">
                <label className="form-label">Title *</label>
                <input id="maint-title" className="form-input" required value={form.title}
                  onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
                  placeholder="Brief description of the issue" />
              </div>
              <div className="form-group">
                <label className="form-label">Description *</label>
                <textarea className="form-textarea" required value={form.description}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  placeholder="Provide detailed information about the issue…" />
              </div>
              {editTarget && (
                <div className="form-group">
                  <label className="form-label">Resolution Notes</label>
                  <textarea className="form-textarea" value={form.resolution_notes}
                    onChange={e => setForm(f => ({ ...f, resolution_notes: e.target.value }))}
                    placeholder="Describe the resolution actions taken…" style={{ minHeight: 70 }} />
                </div>
              )}
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button id="save-maint-btn" type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Saving…' : (editTarget ? 'Update Request' : 'Submit Report')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
