// Centralized API client — all requests go through /api prefix
// which the Vite proxy (dev) and Nginx (prod) forward to the backend

const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail));
  }
  if (res.status === 204) return undefined as unknown as T;
  return res.json();
}

// ── Resources ─────────────────────────────────────────────────────────────────
import type { Resource, Reservation, MaintenanceRequest, DashboardStats } from '@/types';

export const api = {
  // Dashboard
  getDashboard: (): Promise<DashboardStats> => request('/dashboard/stats'),

  // Resources
  getResources: (params?: Record<string, string>) => {
    const q = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<Resource[]>(`/resources${q}`);
  },
  getResource: (id: number) => request<Resource>(`/resources/${id}`),
  createResource: (data: Omit<Resource, 'id' | 'created_at' | 'updated_at'>) =>
    request<Resource>('/resources', { method: 'POST', body: JSON.stringify(data) }),
  updateResource: (id: number, data: Partial<Resource>) =>
    request<Resource>(`/resources/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteResource: (id: number) =>
    request<void>(`/resources/${id}`, { method: 'DELETE' }),

  // Reservations
  getReservations: (params?: Record<string, string>) => {
    const q = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<Reservation[]>(`/reservations${q}`);
  },
  getReservation: (id: number) => request<Reservation>(`/reservations/${id}`),
  createReservation: (data: Omit<Reservation, 'id' | 'status' | 'created_at' | 'updated_at' | 'resource'>) =>
    request<Reservation>('/reservations', { method: 'POST', body: JSON.stringify(data) }),
  updateReservation: (id: number, data: Partial<Reservation>) =>
    request<Reservation>(`/reservations/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteReservation: (id: number) =>
    request<void>(`/reservations/${id}`, { method: 'DELETE' }),

  // Maintenance
  getMaintenance: (params?: Record<string, string>) => {
    const q = params ? '?' + new URLSearchParams(params).toString() : '';
    return request<MaintenanceRequest[]>(`/maintenance${q}`);
  },
  getMaintenanceById: (id: number) => request<MaintenanceRequest>(`/maintenance/${id}`),
  createMaintenance: (data: Omit<MaintenanceRequest, 'id' | 'status' | 'resolved_at' | 'resolution_notes' | 'created_at' | 'updated_at' | 'resource'>) =>
    request<MaintenanceRequest>('/maintenance', { method: 'POST', body: JSON.stringify(data) }),
  updateMaintenance: (id: number, data: Partial<MaintenanceRequest>) =>
    request<MaintenanceRequest>(`/maintenance/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteMaintenance: (id: number) =>
    request<void>(`/maintenance/${id}`, { method: 'DELETE' }),
};
