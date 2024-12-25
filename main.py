from fastapi import FastAPI, Query, HTTPException, Response
import aiohttp

app = FastAPI()

url_test = "http://localhost:8000/?url=https%3A%2F%2Fk7rzspb5flu6zayatfe4mh.my%2Fdata%2F79904691%2F1%2F47d9bece58b5fa30fb00557a547f4775%2FQgtOzAlSMLtJtsEkklErtCJb5FY7NWCmcV0GoUnX.jpg"

# Global session
session: aiohttp.ClientSession | None = None

# Startup event untuk membuat session
@app.on_event("startup")
async def create_session():
    global session
    session = aiohttp.ClientSession()

# Shutdown event untuk menutup session
@app.on_event("shutdown")
async def close_session():
    global session
    if session:
        await session.close()


@app.get("/")
async def proxy_url(url: str = Query(..., description="Target URL to forward the request")):
    """
    Proxy API to fetch content from the target URL specified in the query parameter.
    """
    # Pastikan parameter query `url` diberikan
    if not url:
        raise HTTPException(status_code=400, detail="Query parameter 'url' is required")

    if not session:
        raise HTTPException(status_code=500, detail="Session not initialized")

    try:
        print(f"Fetching URL: {url}")
        # Menggunakan session global
        async with session.get(url) as resp:
            # Membaca konten dari response
            content = await resp.read()
            
            # Mengembalikan response ke client
            return Response(
                content=content,
                status_code=resp.status,
                headers={"Content-Type": resp.content_type}
            )
    except aiohttp.ClientError as e:
        # Tangani error dari aiohttp
        raise HTTPException(status_code=500, detail=f"Error fetching the target URL: {e}")