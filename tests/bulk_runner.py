import asyncio
import httpx
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"
SAMPLES_DIR = Path(__file__).parent / "sample_files"

async def run_single_scan(client, file_path):
    print(f"Submitting {file_path.name}...")
    
    with open(file_path, "rb") as f:
        files = {"file": (file_path.name, f, "text/x-python")}
        response = await client.post(f"{BASE_URL}/scans", files=files)
    
    if response.status_code not in [200, 202]:
        print(f"Failed to submit {file_path.name}: {response.text}")
        return file_path.name, "SUBMISSION_FAILED", None

    data = response.json()
    scan_id = data["id"]
    status = data["status"]

    # If it was a cache hit (200 OK), we might already have results
    if status == "COMPLETED":
        return file_path.name, status, data.get("results")

    # Poll for results
    while status in ["PENDING", "RUNNING"]:
        await asyncio.sleep(2)
        resp = await client.get(f"{BASE_URL}/scans/{scan_id}")
        data = resp.json()
        status = data["status"]
        print(f"  {file_path.name}: {status}...")

    return file_path.name, status, data.get("results")

async def main():
    files = sorted(list(SAMPLES_DIR.glob("*.py")))
    if not files:
        print(f"No .py files found in {SAMPLES_DIR}")
        return

    print(f"Starting bulk scan for {len(files)} files...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        tasks = [run_single_scan(client, f) for f in files]
        results = await asyncio.gather(*tasks)

    print("\n" + "="*50)
    print("FINAL BULK SCAN RESULTS")
    print("="*50)
    for filename, status, review in results:
        print(f"File: {filename}")
        print(f"  Status: {status}")
        if review:
            print(f"  Results: {review}")
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main())
