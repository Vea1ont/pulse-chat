import asyncio
from sqlalchemy import text
from database import SessionLocal

async def seed_users(n=500000):
    sql = text(
        "INSERT INTO users (email, hashed_password, username,created_at) "
        "SELECT 'seeduser' ||i|| '@test.com', 'x', 'seeduser' ||i, now() "
        "FROM generate_series(1, :n) AS i"
    )
    
    async with SessionLocal() as db:
        await db.execute(sql, {"n": n})
        await db.commit()
        
        
if __name__ == "__main__":
    asyncio.run(seed_users())