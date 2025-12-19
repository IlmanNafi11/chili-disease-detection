from app import app
from app.config import get_config
from urllib.parse import urlparse

if __name__ == "__main__":
    import uvicorn
    config = get_config()
    
    parsed_url = urlparse(config.base_url)
    host = parsed_url.hostname or "0.0.0.0"
    port = parsed_url.port or 8000
    
    uvicorn.run(app, host=host, port=port)