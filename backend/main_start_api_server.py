import uvicorn
from src.api.route_root import api_app

if __name__ == '__main__':
    uvicorn.run(app=api_app,
                host="0.0.0.0",
                port=5000,
                log_level="info")