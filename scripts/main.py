
import sys
from fastapi import FastAPI
import uvicorn
from multiprocessing import Process

app=FastAPI()
@app.get("/")
async def read_root():
    return {"Hello": "World"}

def run():
    print("Start uvicorn")
    uvicorn.run("main:app")
    print("End of run")

if __name__=='__main__':
    print("Hello world!")
    print(sys.path)
    # proc = Process(target=run, args=(), daemon=True)
    # proc.start()
    uvicorn.run("main:app", loop='asyncio', host='0.0.0.0', port=12341)
