// Campus Resource Hub API Types

export type ResourceType =
  | 'classroom'
  | 'laboratory'
  | 'meeting_room'
  | 'projector'
  | 'equipment'
  | 'sports_facility'
  | 'library_room';

export type ResourceStatus = 'available' | 'under_maintenance' | 'reserved' | 'inactive';
export type ReservationStatus = 'pending' | 'confirmed' | 'cancelled' | 'completed';
export type MaintenancePriority = 'low' | 'medium' | 'high' | 'critical';
export type MaintenanceStatus = 'open' | 'in_progress' | 'resolved' | 'closed';

export interface Resource {
  id: number;
  name: string;
  resource_type: ResourceType;
  location: string;
  building?: string;
  capacity?: number;
  description?: string;
  status: ResourceStatus;
  is_active: boolean;
  amenities?: string;
  image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Reservation {
  id: number;
  resource_id: number;
  requester_name: string;
  requester_email: string;
  requester_role: string;
  purpose: string;
  start_time: string;
  end_time: string;
  attendees_count?: number;
  status: ReservationStatus;
  notes?: string;
  resource?: Resource;
  created_at: string;
  updated_at: string;
}

export interface MaintenanceRequest {
  id: number;
  resource_id: number;
  reported_by: string;
  reporter_email: string;
  title: string;
  description: string;
  priority: MaintenancePriority;
  status: MaintenanceStatus;
  resolution_notes?: string;
  resolved_at?: string;
  resource?: Resource;
  created_at: string;
  updated_at: string;
}

export interface DashboardStats {
  total_resources: number;
  available_resources: number;
  under_maintenance_resources: number;
  total_reservations: number;
  pending_reservations: number;
  confirmed_reservations: number;
  open_maintenance_requests: number;
  critical_maintenance_requests: number;
  resources_by_type: Record<string, number>;
  recent_reservations: Reservation[];
  recent_maintenance: MaintenanceRequest[];
}
