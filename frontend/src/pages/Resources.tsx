import { useEffect, useState, useCallback } from 'react'
import {
  Building2, Plus, Search, Edit2, Trash2, X, Cpu,
  Monitor, BookOpen, Dumbbell, Users, Projector, Package
} from 'lucide-react'
import { api } from '../api/client'
import type { Resource, ResourceType, ResourceStatus } from '../types'

const TYPE_ICONS: Record<string, React.ElementType> = {
  classroom: Users, laboratory: Cpu, meeting_room: Monitor,
  projector: Projector, equipment: Package, sports_facility: Dumbbell,
  library_room: BookOpen,
}

const RESOURCE_TYPES: { value: ResourceType; label: string }[] = [
  { value: 'classroom', label: 'Classroom' },
  { value: 'laboratory', label: 'Laboratory' },
  { value: 'meeting_room', label: 'Meeting Room' },
  { value: 'projector', label: 'Projector' },
  { value: 'equipment', label: 'Equipment' },
  { value: 'sports_facility', label: 'Sports Facility' },
  { value: 'library_room', label: 'Library Room' },
]

const STATUS_OPTIONS: { value: ResourceStatus; label: string }[] = [
  { value: 'available', label: 'Available' },
  { value: 'under_maintenance', label: 'Under Maintenance' },
  { value: 'reserved', label: 'Reserved' },
  { value: 'inactive', label: 'Inactive' },
]

const emptyForm = {
  name: '', resource_type: 'classroom' as ResourceType, location: '',
  building: '', capacity: '', description: '', status: 'available' as ResourceStatus,
  is_active: true, amenities: '',
}

export default function Resources() {
  const [resources, setResources] = useState<Resource[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editTarget, setEditTarget] = useState<Resource | null>(null)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [search, setSearch] = useState('')

  const load = useCallback(async () => {
    try {
      setLoading(true)
      const params: Record<string, string> = {}
      if (typeFilter) params.resource_type = typeFilter
      if (statusFilter) params.status = statusFilter
      const data = await api.getResources(params)
      setResources(data)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [typeFilter, statusFilter])

  useEffect(() => { load() }, [load])

  const openCreate = () => {
    setEditTarget(null)
    setForm(emptyForm)
    setFormError('')
    setShowModal(true)
  }

  const openEdit = (r: Resource) => {
    setEditTarget(r)
    setForm({
      name: r.name, resource_type: r.resource_type, location: r.location,
      building: r.building ?? '', capacity: r.capacity?.toString() ?? '',
      description: r.description ?? '', status: r.status,
      is_active: r.is_active, amenities: r.amenities ?? '',
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
        capacity: form.capacity ? parseInt(form.capacity) : undefined,
      }
      if (editTarget) {
        await api.updateResource(editTarget.id, payload)
        setSuccess('Resource updated successfully')
      } else {
        await api.createResource(payload as never)
        setSuccess('Resource created successfully')
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
    if (!confirm('Delete this resource? All associated reservations and maintenance requests will also be deleted.')) return
    try {
      await api.deleteResource(id)
      setSuccess('Resource deleted')
      load()
    } catch (e) {
      setError((e as Error).message)
    }
  }

  const filtered = resources.filter(r =>
    !search || r.name.toLowerCase().includes(search.toLowerCase()) ||
    r.location.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div>
      <div className="page-header">
        <h1>Campus Resources</h1>
        <p>Manage classrooms, laboratories, equipment, and other campus facilities</p>
      </div>

      {error && <div className="alert alert-error"><X size={16} />{error}<button onClick={() => setError('')} style={{ marginLeft: 'auto' }}><X size={14} /></button></div>}
      {success && <div className="alert alert-success">{success}<button onClick={() => setSuccess('')} style={{ marginLeft: 'auto' }}><X size={14} /></button></div>}

      {/* Filter Bar */}
      <div className="filter-bar">
        <div style={{ position: 'relative', flex: 1, maxWidth: 280 }}>
          <Search size={16} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-dim)' }} />
          <input
            id="resource-search"
            className="form-input"
            placeholder="Search resources..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ paddingLeft: 38 }}
          />
        </div>
        <select id="type-filter" className="form-select" value={typeFilter} onChange={e => setTypeFilter(e.target.value)} style={{ maxWidth: 180 }}>
          <option value="">All Types</option>
          {RESOURCE_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>
        <select id="status-filter" className="form-select" value={statusFilter} onChange={e => setStatusFilter(e.target.value)} style={{ maxWidth: 180 }}>
          <option value="">All Statuses</option>
          {STATUS_OPTIONS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
        </select>
        <button id="add-resource-btn" className="btn btn-primary" onClick={openCreate}>
          <Plus size={16} /> Add Resource
        </button>
      </div>

      {/* Resource Grid */}
      {loading ? (
        <div className="resource-grid">
          {[...Array(6)].map((_, i) => <div key={i} className="skeleton" style={{ height: 180 }} />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <div className="empty-state-icon"><Building2 size={28} /></div>
            <h3>No resources found</h3>
            <p>Create your first campus resource to get started.</p>
            <button className="btn btn-primary" style={{ marginTop: 16 }} onClick={openCreate}>
              <Plus size={16} /> Add Resource
            </button>
          </div>
        </div>
      ) : (
        <div className="resource-grid">
          {filtered.map(r => {
            const Icon = TYPE_ICONS[r.resource_type] ?? Package
            return (
              <div key={r.id} className="resource-card">
                <div className="resource-card-header">
                  <div className="resource-icon-wrap"><Icon size={20} /></div>
                  <span className={`badge badge-${r.status === 'under_maintenance' ? 'maintenance' : r.status}`}>
                    {r.status.replace('_', ' ')}
                  </span>
                </div>
                <div>
                  <div className="resource-name">{r.name}</div>
                  <div className="resource-meta">
                    <span>📍 {r.location}</span>
                    {r.building && <span>🏢 {r.building}</span>}
                    {r.capacity && <span>👥 Capacity: {r.capacity}</span>}
                    <span style={{ textTransform: 'capitalize' }}>
                      🏷️ {r.resource_type.replace('_', ' ')}
                    </span>
                  </div>
                  {r.description && (
                    <p style={{ fontSize: 12, color: 'var(--color-text-dim)', marginTop: 8, lineHeight: 1.5 }}>
                      {r.description.slice(0, 100)}{r.description.length > 100 ? '…' : ''}
                    </p>
                  )}
                </div>
                <div className="resource-actions">
                  <button id={`edit-resource-${r.id}`} className="btn btn-secondary btn-sm" onClick={() => openEdit(r)}>
                    <Edit2 size={13} /> Edit
                  </button>
                  <button id={`delete-resource-${r.id}`} className="btn btn-danger btn-sm" onClick={() => handleDelete(r.id)}>
                    <Trash2 size={13} /> Delete
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2 className="modal-title">{editTarget ? 'Edit Resource' : 'Add New Resource'}</h2>
              <button className="btn btn-secondary btn-icon" onClick={() => setShowModal(false)}><X size={18} /></button>
            </div>
            {formError && <div className="alert alert-error"><X size={14} />{formError}</div>}
            <form onSubmit={handleSubmit}>
              <div className="form-grid-2">
                <div className="form-group">
                  <label className="form-label">Name *</label>
                  <input id="resource-name-input" className="form-input" required value={form.name}
                    onChange={e => setForm(f => ({ ...f, name: e.target.value }))} placeholder="e.g. Computer Lab A" />
                </div>
                <div className="form-group">
                  <label className="form-label">Type *</label>
                  <select id="resource-type-input" className="form-select" value={form.resource_type}
                    onChange={e => setForm(f => ({ ...f, resource_type: e.target.value as ResourceType }))}>
                    {RESOURCE_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Location *</label>
                  <input className="form-input" required value={form.location}
                    onChange={e => setForm(f => ({ ...f, location: e.target.value }))} placeholder="Block A, Room 101" />
                </div>
                <div className="form-group">
                  <label className="form-label">Building</label>
                  <input className="form-input" value={form.building}
                    onChange={e => setForm(f => ({ ...f, building: e.target.value }))} placeholder="Block A" />
                </div>
                <div className="form-group">
                  <label className="form-label">Capacity</label>
                  <input className="form-input" type="number" min={1} value={form.capacity}
                    onChange={e => setForm(f => ({ ...f, capacity: e.target.value }))} placeholder="40" />
                </div>
                <div className="form-group">
                  <label className="form-label">Status</label>
                  <select className="form-select" value={form.status}
                    onChange={e => setForm(f => ({ ...f, status: e.target.value as ResourceStatus }))}>
                    {STATUS_OPTIONS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea className="form-textarea" value={form.description}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  placeholder="Describe the resource, equipment available, etc." />
              </div>
              <div className="form-group">
                <label className="form-label">Amenities</label>
                <input className="form-input" value={form.amenities}
                  onChange={e => setForm(f => ({ ...f, amenities: e.target.value }))}
                  placeholder="Projector, AC, Whiteboard, WiFi..." />
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button id="save-resource-btn" type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Saving…' : (editTarget ? 'Update Resource' : 'Create Resource')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
