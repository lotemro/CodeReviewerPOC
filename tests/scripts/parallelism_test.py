import asyncio
import httpx
import uuid

BASE_URL = "http://localhost:8000"

async def submit_unique_scan(client, index):
    # We add a unique ID to the code to ensure it's a cache miss
    unique_id = str(uuid.uuid4())
    code = f"# Unique scan {index}\n# ID: {unique_id}\ndef test():\n    return {index}"
    
    files = {"file": (f"parallel_test_{index}.py", code.encode(), "text/x-python")}
    
    try:
        response = await client.post(f"{BASE_URL}/scans", files=files)
        return response.status_code
    except Exception as e:
        return str(e)

async def main():
    print("Starting parallelism test: Sending 10 simultaneous requests...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Launch all 10 requests at the same time
        tasks = [submit_unique_scan(client, i) for i in range(10)]
        results = await asyncio.gather(*tasks)

    # Count the outcomes
    accepted = results.count(202)
    rejected = results.count(503)
    others = [r for r in results if r not in [202, 503]]

    print("\n" + "="*50)
    print("PARALLELISM TEST SUMMARY")
    print("="*50)
    print(f"Total Requests: {len(results)}")
    print(f"Accepted (202): {accepted}")
    print(f"Rejected (503): {rejected}")
    
    if others:
        print(f"Other responses: {others}")

    # Success criteria: 
    # Since the limit is 5, we expect exactly 5 accepted and 5 rejected.
    # Note: If a background task finished extremely fast, 'accepted' could be higher,
    # but with local LLM this is unlikely.
    if accepted == 5 and rejected == 5:
        print("\n✅ TEST PASSED: Concurrency limit strictly enforced.")
    else:
        print("\n❌ TEST FAILED: Concurrency limit not behaving as expected.")
        print(f"Expected: 5 Accepted, 5 Rejected. Actual: {accepted} Accepted, {rejected} Rejected.")

if __name__ == "__main__":
    asyncio.run(main())
