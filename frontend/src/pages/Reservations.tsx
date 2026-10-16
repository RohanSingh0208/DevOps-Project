import { useEffect, useState, useCallback } from 'react'
import { Calendar, Plus, X, Edit2, Trash2 } from 'lucide-react'
import { format } from 'date-fns'
import { api } from '../api/client'
import type { Reservation, ReservationStatus, Resource } from '../types'

const STATUS_OPTIONS: { value: ReservationStatus; label: string }[] = [
  { value: 'pending', label: 'Pending' },
  { value: 'confirmed', label: 'Confirmed' },
  { value: 'cancelled', label: 'Cancelled' },
  { value: 'completed', label: 'Completed' },
]

const emptyForm = {
  resource_id: '', requester_name: '', requester_email: '',
  requester_role: 'student', purpose: '',
  start_time: '', end_time: '', attendees_count: '', notes: '',
}

export default function Reservations() {
  const [reservations, setReservations] = useState<Reservation[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editTarget, setEditTarget] = useState<Reservation | null>(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params: Record<string, string> = {}
      if (statusFilter) params.status = statusFilter
      const [rsv, res] = await Promise.all([
        api.getReservations(params),
        api.getResources(),
      ])
      setReservations(rsv)
      setResources(res)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [statusFilter])

  useEffect(() => { load() }, [load])

  const openCreate = () => {
    setEditTarget(null)
    setForm(emptyForm)
    setFormError('')
    setShowModal(true)
  }

  const openEdit = (r: Reservation) => {
    setEditTarget(r)
    setForm({
      resource_id: r.resource_id.toString(),
      requester_name: r.requester_name,
      requester_email: r.requester_email,
      requester_role: r.requester_role,
      purpose: r.purpose,
      start_time: r.start_time.slice(0, 16),
      end_time: r.end_time.slice(0, 16),
      attendees_count: r.attendees_count?.toString() ?? '',
      notes: r.notes ?? '',
    })
    setFormError('')
    setShowModal(true)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setFormError('')
    try {
      const payload = {
        ...form,
        resource_id: parseInt(form.resource_id),
        attendees_count: form.attendees_count ? parseInt(form.attendees_count) : undefined,
        start_time: new Date(form.start_time).toISOString(),
        end_time: new Date(form.end_time).toISOString(),
      }
      if (editTarget) {
        await api.updateReservation(editTarget.id, payload)
        setSuccess('Reservation updated')
      } else {
        await api.createReservation(payload as never)
        setSuccess('Reservation created')
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
    if (!confirm('Delete this reservation?')) return
    try {
      await api.deleteReservation(id)
      setSuccess('Reservation deleted')
      load()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  const getResourceName = (id: number) => resources.find(r => r.id === id)?.name ?? `#${id}`

  return (
    <div>
      <div className="page-header">
        <h1>Reservations</h1>
        <p>Manage campus resource bookings and scheduling</p>
      </div>

      {error && <div className="alert alert-error"><X size={16}/>{error}<button onClick={() => setError('')} style={{ marginLeft: 'auto' }}><X size={14}/></button></div>}
      {success && <div className="alert alert-success">{success}<button onClick={() => setSuccess('')} style={{ marginLeft: 'auto' }}><X size={14}/></button></div>}

      <div className="filter-bar">
        <select id="reservation-status-filter" className="form-select" value={statusFilter} onChange={e => setStatusFilter(e.target.value)} style={{ maxWidth: 200 }}>
          <option value="">All Statuses</option>
          {STATUS_OPTIONS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
        </select>
        <button id="add-reservation-btn" className="btn btn-primary" onClick={openCreate}>
          <Plus size={16} /> New Reservation
        </button>
      </div>

      <div className="card">
        {loading ? (
          <div className="loading-spinner"><div className="spinner" /></div>
        ) : reservations.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon"><Calendar size={28} /></div>
            <h3>No reservations found</h3>
            <p>Create a reservation to book a campus resource.</p>
            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={openCreate}>
              <Plus size={16} /> New Reservation
            </button>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Resource</th>
                  <th>Requester</th>
                  <th>Purpose</th>
                  <th>Start</th>
                  <th>End</th>
                  <th>Attendees</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reservations.map(r => (
                  <tr key={r.id}>
                    <td style={{ color: 'var(--color-text-dim)' }}>#{r.id}</td>
                    <td>
                      <span style={{ fontWeight: 600 }}>{r.resource?.name ?? getResourceName(r.resource_id)}</span>
                    </td>
                    <td>
                      <div style={{ fontSize: 13, fontWeight: 500 }}>{r.requester_name}</div>
                      <div style={{ fontSize: 11, color: 'var(--color-text-muted)' }}>{r.requester_email}</div>
                    </td>
                    <td style={{ maxWidth: 180 }}>
                      <span style={{ fontSize: 12, color: 'var(--color-text-muted)' }}>
                        {r.purpose.slice(0, 60)}{r.purpose.length > 60 ? '…' : ''}
                      </span>
                    </td>
                    <td style={{ whiteSpace: 'nowrap', fontSize: 12 }}>
                      {format(new Date(r.start_time), 'MMM d, HH:mm')}
                    </td>
                    <td style={{ whiteSpace: 'nowrap', fontSize: 12 }}>
                      {format(new Date(r.end_time), 'MMM d, HH:mm')}
                    </td>
                    <td style={{ textAlign: 'center' }}>{r.attendees_count ?? '—'}</td>
                    <td><span className={`badge badge-${r.status}`}>{r.status}</span></td>
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button id={`edit-reservation-${r.id}`} className="btn btn-secondary btn-sm btn-icon" onClick={() => openEdit(r)} title="Edit"><Edit2 size={13}/></button>
                        <button id={`delete-reservation-${r.id}`} className="btn btn-danger btn-sm btn-icon" onClick={() => handleDelete(r.id)} title="Delete"><Trash2 size={13}/></button>
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
              <h2 className="modal-title">{editTarget ? 'Edit Reservation' : 'New Reservation'}</h2>
              <button className="btn btn-secondary btn-icon" onClick={() => setShowModal(false)}><X size={18}/></button>
            </div>
            {formError && <div className="alert alert-error"><X size={14}/>{formError}</div>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Resource *</label>
                <select id="reservation-resource" className="form-select" required value={form.resource_id}
                  onChange={e => setForm(f => ({ ...f, resource_id: e.target.value }))}>
                  <option value="">Select a resource…</option>
                  {resources.filter(r => r.status === 'available' || (editTarget && r.id === editTarget.resource_id))
                    .map(r => <option key={r.id} value={r.id}>{r.name} — {r.location}</option>)}
                </select>
              </div>
              <div className="form-grid-2">
                <div className="form-group">
                  <label className="form-label">Your Name *</label>
                  <input id="reservation-name" className="form-input" required value={form.requester_name}
                    onChange={e => setForm(f => ({ ...f, requester_name: e.target.value }))} placeholder="Full name" />
                </div>
                <div className="form-group">
                  <label className="form-label">Email *</label>
                  <input className="form-input" type="email" required value={form.requester_email}
                    onChange={e => setForm(f => ({ ...f, requester_email: e.target.value }))} placeholder="you@university.edu" />
                </div>
                <div className="form-group">
                  <label className="form-label">Role</label>
                  <select className="form-select" value={form.requester_role}
                    onChange={e => setForm(f => ({ ...f, requester_role: e.target.value }))}>
                    <option value="student">Student</option>
                    <option value="faculty">Faculty</option>
                    <option value="staff">Staff</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Attendees</label>
                  <input className="form-input" type="number" min={1} value={form.attendees_count}
                    onChange={e => setForm(f => ({ ...f, attendees_count: e.target.value }))} placeholder="e.g. 10" />
                </div>
                <div className="form-group">
                  <label className="form-label">Start Time *</label>
                  <input id="reservation-start" className="form-input" type="datetime-local" required value={form.start_time}
                    onChange={e => setForm(f => ({ ...f, start_time: e.target.value }))} />
                </div>
                <div className="form-group">
                  <label className="form-label">End Time *</label>
                  <input id="reservation-end" className="form-input" type="datetime-local" required value={form.end_time}
                    onChange={e => setForm(f => ({ ...f, end_time: e.target.value }))} />
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Purpose *</label>
                <textarea className="form-textarea" required value={form.purpose}
                  onChange={e => setForm(f => ({ ...f, purpose: e.target.value }))}
                  placeholder="Describe the purpose of the reservation…" style={{ minHeight: 80 }} />
              </div>
              <div className="form-group">
                <label className="form-label">Notes</label>
                <input className="form-input" value={form.notes}
                  onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} placeholder="Any additional notes" />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button id="save-reservation-btn" type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Saving…' : (editTarget ? 'Update Reservation' : 'Create Reservation')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
