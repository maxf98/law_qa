import os
from datetime import datetime
import json

from fastapi import FastAPI
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware

from src.api.route_chat_only import chat_router

api_app = FastAPI(
    title="Legal Q&A",
)

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@api_app.middleware("http")
async def log_requests(request: Request, call_next):
    client_ip = request.client.host
    def build_receive(bbody: bytes):
        async def receive():
            return {"type": "http.request", "body": bbody}

        return receive
    body = await request.body()
    request_body = body.decode()
    request = Request(scope=request.scope, receive=build_receive(body))

    try:
        request_body = json.loads(request_body)
    except json.decoder.JSONDecodeError:
        pass

    if request.url.path.startswith('/chat-mode'):

        date_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        request_suburl = request.url.path.replace('/', '_')
        log_filename = f"{date_time}{request.method}{request_suburl}.txt"

        response = await call_next(request)

        response_body = b''
        async for chunk in response.body_iterator:
            response_body += chunk
        new_response = Response(response_body, status_code=response.status_code, headers=dict(response.headers))

        response_body = response_body.decode()
        try:
            response_body = json.loads(response_body)
        except json.decoder.JSONDecodeError:
            pass

        log_dir = './logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        with open(f'{log_dir}/{log_filename}', 'w', encoding='utf-8') as log_file:
            log_file.write(json.dumps({
                'client_ip': client_ip,
                'in_body': request_body,
                'out_body': response_body
            }, ensure_ascii=False, indent=2))

        return new_response
    else:
        return await call_next(request)


api_app.include_router(chat_router, prefix='/chat-mode', tags=['chat-mode'])
