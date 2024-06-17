FROM python:3.9-slim-buster
WORKDIR /app
ADD . /app
RUN apt-get update && apt-get install -y supervisor

RUN echo "[supervisord]" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "nodaemon=true" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "[unix_http_server]" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "file=/tmp/supervisor.sock" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "[rpcinterface:supervisor]" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface" >> /etc/supervisor/conf.d/supervisord.conf
RUN echo "[program:myapp]" >> /etc/supervisor/conf.d/myapp.conf
RUN echo "command=python main.py" >> /etc/supervisor/conf.d/myapp.conf
RUN echo "directory=/app" >> /etc/supervisor/conf.d/myapp.conf
RUN echo "autostart=true" >> /etc/supervisor/conf.d/myapp.conf
RUN echo "autorestart=true" >> /etc/supervisor/conf.d/myapp.conf

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["/usr/bin/supervisord"]

