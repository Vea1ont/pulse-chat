import asyncio
import time

import httpx

sem = asyncio.Semaphore(3)
client = httpx.AsyncClient()

async def fetch(client):
    async with sem:
        r = await client.get("https://httpbin.org/delay/1")
        print(r)




async def main():
    async with httpx.AsyncClient() as client:
        responses = [fetch(client) for _ in range(10)]
        res = await asyncio.gather(*responses)
    print(res)


st = time.perf_counter()


asyncio.run(main())

et = time.perf_counter()
print(et- st)
