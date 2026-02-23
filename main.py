from fastapi import FastAPI
import docker

app = FastAPI()
client = docker.from_env()

@app.get("/status")
def get_status():
    try:
        container = client.containers.get("minecraft-server")
        return {"status": container.status}
    except Exception as e:
        return {"status": "not found", "error": str(e)}

@app.post("/start")
def start_server():
    try:
        container = client.containers.get("minecraft-server")
        container.start()
        return {"message": "서버 시작됨"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/stop")
def stop_server():
    try:
        container = client.containers.get("minecraft-server")
        container.stop()
        return {"message": "서버 중지됨"}
    except Exception as e:
        return {"error": str(e)}