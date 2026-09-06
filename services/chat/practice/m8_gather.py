import asyncio
import time

import httpx


async def task():
    async with httpx.AsyncClient() as client:
        r1 = await client.get("https://httpbin.org/delay/1")
        r2 = await client.get("https://httpbin.org/delay/1")
        r3 = await client.get("https://httpbin.org/delay/1")
        
        print(r1, r2, r3)

start_time = time.perf_counter()

asyncio.run(task())

end_time = time.perf_counter()

elapsed = end_time - start_time
print(f"Execution time {elapsed:.6f} seconds")

start_time = time.perf_counter()


async def main():

    tasks = [task() for _ in range(3)]

    all_results = await asyncio.gather(*tasks)
    print(all_results)


asyncio.run(main())

end_time = time.perf_counter()

elapsed = end_time - start_time
print(f"Execution time {elapsed:.6f} seconds")
