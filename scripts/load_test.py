#!/usr/bin/env python3
"""
Load Generator Script for Campus Resource Hub
Simulates concurrent traffic to test Prometheus metrics collection and trigger
Kubernetes Horizontal Pod Autoscaler (HPA) scale-out.

Usage:
    python scripts/load_test.py --url http://localhost:8000 --concurrency 10 --duration 60
"""

import argparse
import concurrent.futures
import time
import sys
import requests

def send_request(url: str, session: requests.Session):
    start = time.time()
    try:
        r = session.get(f"{url}/api/resources", timeout=5)
        duration = (time.time() - start) * 1000
        return r.status_code, duration
    except Exception as e:
        return 0, 0

def run_load(url: str, concurrency: int, duration_sec: int):
    print(f"============================================================")
    print(f" CAMPUS RESOURCE HUB — HPA LOAD GENERATOR")
    print(f" Target URL:   {url}")
    print(f" Concurrency:  {concurrency} workers")
    print(f" Duration:     {duration_sec} seconds")
    print(f"============================================================")

    # Initial probe
    try:
        probe = requests.get(f"{url}/health", timeout=3)
        print(f"[+] Health check status: {probe.status_code}")
    except Exception as ex:
        print(f"[-] Target unreachable at {url}: {ex}")
        sys.exit(1)

    stop_time = time.time() + duration_sec
    total_requests = 0
    successful_requests = 0
    failed_requests = 0
    total_latency_ms = 0.0

    session = requests.Session()

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        while time.time() < stop_time:
            futures = [executor.submit(send_request, url, session) for _ in range(concurrency)]
            for future in concurrent.futures.as_completed(futures):
                status, latency = future.result()
                total_requests += 1
                if 200 <= status < 300:
                    successful_requests += 1
                    total_latency_ms += latency
                else:
                    failed_requests += 1

            elapsed = int(time.time() - (stop_time - duration_sec))
            rps = total_requests / max(elapsed, 1)
            sys.stdout.write(
                f"\r[Progress: {elapsed}s/{duration_sec}s] "
                f"Total: {total_requests} | Success: {successful_requests} | "
                f"Fail: {failed_requests} | Rate: {rps:.1f} req/s"
            )
            sys.stdout.flush()
            time.sleep(0.05)

    avg_latency = (total_latency_ms / successful_requests) if successful_requests > 0 else 0
    print("\n\n============================================================")
    print(" LOAD TEST RESULTS SUMMARY")
    print("============================================================")
    print(f" Total Requests Sent:  {total_requests}")
    print(f" Successful Requests:  {successful_requests}")
    print(f" Failed Requests:      {failed_requests}")
    print(f" Average Latency:      {avg_latency:.2f} ms")
    print(" Observe HPA scaling with:")
    print("   kubectl get hpa -n campus-resource-hub -w")
    print("============================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate load against Campus Resource Hub.")
    parser.add_argument("--url", default="http://localhost:8000", help="Base target URL")
    parser.add_argument("--concurrency", type=int, default=8, help="Number of concurrent worker threads")
    parser.add_argument("--duration", type=int, default=30, help="Duration of load test in seconds")
    args = parser.parse_args()
    run_load(args.url, args.concurrency, args.duration)
