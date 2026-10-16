#!/usr/bin/env python3
"""
Seed Data Script for Campus Resource Hub
Populates the database with realistic sample resources, reservations, and maintenance requests.
Supports seeding via direct HTTP API (default) or direct database connection.

Usage:
    python scripts/seed_data.py [--api-url http://localhost:8000]
"""

import sys
import argparse
from datetime import datetime, timedelta, timezone
import requests

DEFAULT_API_URL = "http://localhost:8000"

SAMPLE_RESOURCES = [
    {
        "name": "Alan Turing Computer Lab",
        "resource_type": "laboratory",
        "building": "Ada Lovelace Hall",
        "floor": 2,
        "room_number": "L-204",
        "capacity": 45,
        "description": "High-performance workstations with GPU acceleration, dual-boot Linux/Windows, and digital whiteboard.",
        "amenities": ["GPU Workstations", "Projector", "Smart Board", "Air Conditioning", "Gigabit Ethernet"],
        "status": "available",
        "is_active": True,
    },
    {
        "name": "Quantum Lecture Hall",
        "resource_type": "classroom",
        "building": "Science & Tech Complex",
        "floor": 1,
        "room_number": "ST-101",
        "capacity": 150,
        "description": "Tiered auditorium with dual laser projectors, surround sound, and integrated lecture recording system.",
        "amenities": ["Dual 4K Laser Projectors", "Lapel Microphones", "Lecture Capture", "Wi-Fi 6E"],
        "status": "available",
        "is_active": True,
    },
    {
        "name": "Robotics & Embedded Systems Lab",
        "resource_type": "laboratory",
        "building": "Engineering Building B",
        "floor": 3,
        "room_number": "E-312",
        "capacity": 30,
        "description": "Specialized lab equipped with oscilloscopes, soldering stations, 3D printers, and robotic arm testbeds.",
        "amenities": ["Soldering Stations", "Digital Oscilloscopes", "3D Printers", "Exhaust Ventilation"],
        "status": "available",
        "is_active": True,
    },
    {
        "name": "Executive Boardroom",
        "resource_type": "meeting_room",
        "building": "Administration Center",
        "floor": 4,
        "room_number": "ADM-401",
        "capacity": 20,
        "description": "Premium conference room with 85-inch video conferencing display, motorized blackout shades, and executive seating.",
        "amenities": ["85-inch Display", "Video Conference Camera", "Conference Speakerphone", "Coffee Station"],
        "status": "available",
        "is_active": True,
    },
    {
        "name": "4K Ultra-Short-Throw Portable Projector A",
        "resource_type": "projector",
        "building": "Central Media Depot",
        "floor": 1,
        "room_number": "CMD-04",
        "capacity": 1,
        "description": "5000-lumen portable laser projector with HDMI, USB-C, and wireless casting support.",
        "amenities": ["4K Resolution", "Wireless Casting", "Protective Flight Case", "HDMI/USB-C Cables"],
        "status": "available",
        "is_active": True,
    },
    {
        "name": "Indoor Badminton Court 1",
        "resource_type": "sports_facility",
        "building": "University Recreation & Sports Complex",
        "floor": 1,
        "room_number": "GYM-B1",
        "capacity": 4,
        "description": "Competition-standard wooden sprung court with LED court illumination and electronic scorekeeper.",
        "amenities": ["Sprung Wooden Floor", "Tournament Net", "Electronic Scoreboard", "Locker Access"],
        "status": "available",
        "is_active": True,
    },
    {
        "name": "Graduate Study Pod Alpha",
        "resource_type": "library_room",
        "building": "Central Memorial Library",
        "floor": 3,
        "room_number": "LIB-308",
        "capacity": 6,
        "description": "Acoustically insulated collaborative study pod with interactive screen and power at every desk.",
        "amenities": ["Acoustic Soundproofing", "Screen Sharing Display", "Ergonomic Chairs", "Whiteboard"],
        "status": "under_maintenance",
        "is_active": True,
    },
]

def seed(api_url: str):
    print(f"[*] Starting seed process targeting API at: {api_url}")
    
    # Check health
    try:
        r = requests.get(f"{api_url}/health", timeout=5)
        r.raise_for_status()
        print(f"[+] API is alive: {r.json()}")
    except Exception as e:
        print(f"[-] Could not connect to API at {api_url}/health: {e}")
        print("    Ensure the backend service is running before seeding.")
        sys.exit(1)

    # 1. Create Resources
    created_resources = []
    print("\n--- Seeding Resources ---")
    for res_data in SAMPLE_RESOURCES:
        try:
            resp = requests.post(f"{api_url}/api/resources", json=res_data, timeout=5)
            if resp.status_code == 201:
                resource = resp.json()
                created_resources.append(resource)
                print(f"  [+] Created Resource: {resource['name']} (ID: {resource['id']})")
            elif resp.status_code == 409 or "already exists" in resp.text:
                print(f"  [~] Resource '{res_data['name']}' already exists.")
            else:
                print(f"  [-] Failed creating {res_data['name']}: {resp.status_code} {resp.text}")
        except Exception as ex:
            print(f"  [-] Error creating {res_data['name']}: {ex}")

    # Fetch all resources if some were already present
    if not created_resources:
        resp = requests.get(f"{api_url}/api/resources", timeout=5)
        if resp.status_code == 200:
            created_resources = resp.json()

    if not created_resources:
        print("[-] No resources available to create reservations or maintenance for.")
        return

    # 2. Create Reservations
    print("\n--- Seeding Reservations ---")
    now = datetime.now(timezone.utc)
    res_id_1 = created_resources[0]["id"]
    res_id_2 = created_resources[1]["id"] if len(created_resources) > 1 else res_id_1

    sample_reservations = [
        {
            "resource_id": res_id_1,
            "title": "CS401 Distributed Systems Lecture",
            "reserved_by": "Prof. Elena Rostova",
            "user_email": "e.rostova@university.edu",
            "start_time": (now + timedelta(hours=2)).isoformat(),
            "end_time": (now + timedelta(hours=4)).isoformat(),
            "purpose": "Undergraduate lecture on Raft consensus and Kubernetes architectures",
            "attendees_count": 40,
        },
        {
            "resource_id": res_id_2,
            "title": "DevSecOps Student Workshop",
            "reserved_by": "Rohan Singh",
            "user_email": "rohan.singh@campus.edu",
            "start_time": (now + timedelta(days=1, hours=3)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=6)).isoformat(),
            "purpose": "Hands-on CI/CD and Container Security hands-on lab demonstration",
            "attendees_count": 85,
        },
        {
            "resource_id": res_id_1,
            "title": "AI Research Group Weekly Sync",
            "reserved_by": "Dr. Marcus Vance",
            "user_email": "m.vance@university.edu",
            "start_time": (now + timedelta(days=2, hours=1)).isoformat(),
            "end_time": (now + timedelta(days=2, hours=3)).isoformat(),
            "purpose": "Discussion of recent transformer model fine-tuning benchmarks",
            "attendees_count": 15,
        },
    ]

    for reservation_data in sample_reservations:
        try:
            resp = requests.post(f"{api_url}/api/reservations", json=reservation_data, timeout=5)
            if resp.status_code == 201:
                item = resp.json()
                print(f"  [+] Created Reservation: '{item['title']}' for {item['reserved_by']} (ID: {item['id']})")
            else:
                print(f"  [~] Reservation note: {resp.status_code} - {resp.text}")
        except Exception as ex:
            print(f"  [-] Error creating reservation: {ex}")

    # 3. Create Maintenance Requests
    print("\n--- Seeding Maintenance Requests ---")
    pod_resource = next((r for r in created_resources if r.get("resource_type") == "library_room"), created_resources[-1])
    lab_resource = created_resources[0]

    sample_maintenance = [
        {
            "resource_id": pod_resource["id"],
            "title": "Acoustic Door Seal Replacement",
            "description": "Magnetic gasket on soundproof door is worn out, causing sound leakage into adjacent quiet study zones.",
            "priority": "medium",
            "reported_by": "Library Supervisor Davis",
            "status": "in_progress",
        },
        {
            "resource_id": lab_resource["id"],
            "title": "HDMI Port 2 Signal Dropout on Main Projector",
            "description": "Intermittent video blinking when connecting via external auxiliary HDMI wall patch panel.",
            "priority": "high",
            "reported_by": "Lab Assistant Maya Lin",
            "status": "pending",
        },
    ]

    for maint_data in sample_maintenance:
        try:
            resp = requests.post(f"{api_url}/api/maintenance", json=maint_data, timeout=5)
            if resp.status_code == 201:
                item = resp.json()
                print(f"  [+] Created Maintenance Request: '{item['title']}' [Priority: {item['priority']}] (ID: {item['id']})")
            else:
                print(f"  [~] Maintenance note: {resp.status_code} - {resp.text}")
        except Exception as ex:
            print(f"  [-] Error creating maintenance: {ex}")

    print("\n[✔] Database seeding complete! You can now verify in the frontend UI or via API.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Campus Resource Hub with sample data.")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="Base URL of backend API")
    args = parser.parse_args()
    seed(args.api_url)
