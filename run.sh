#!/bin/sh

# 启动 cron
crond

# 启动 Flask
export FLASK_APP=app.py
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=8080
flask run