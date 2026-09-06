import asyncio

import httpx

AUTH = "http://auth:8000/api/v1"
CHAT = "http://chat:8000/api/v1"

async def main():
    async with httpx.AsyncClient() as client:
        count_iter = 10
        
        
        count_logs = 0
        
        for i in range(count_iter):
            response = await client.post(
                f"{AUTH}/auth/register",
                json={
                    "email": f"{i}e2el@test.com",
                    "username": f"{i}e2euser1",
                    "password": f"{i}secret123",
                },
            )
            print(response.status_code, response.json())
            
            response = await client.post(
                f"{AUTH}/auth/login",
                json={
                    "email": f"{i}e2el@test.com",
                    "username": f"{i}e2euser1",
                    "password": f"{i}secret123",
                },
            )
            print(response.status_code, response.json())
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                
                response = await client.post(
                    f"{CHAT}/chats/",
                    headers={"Authorization": f"Bearer {token}"}
,
                    json={
                        "name": f"{i} test chat",
                        "member_ids": [],
                    }
                )
                print(response.status_code, response.json())
                
                response = await client.get(
                    f"{CHAT}/chats/",
                    headers={"Authorization": f"Bearer {token}"}
,
                )
                
                print(response.status_code, response.json())
                
                response = await client.delete(
                    f"{AUTH}/users/me",
                    headers={"Authorization": f"Bearer {token}"}
,
                )
                
                print(response.status_code, response.json())
            count_logs += 1
            if count_logs == 5:
                await asyncio.sleep(60)
                count_logs = 0
                        
            

asyncio.run(main())
