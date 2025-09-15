##! usr/bin/python3
# -*- coding:utf-8 -*-
# llama_index_server api端
# @Time: 2025/9/15 15:51
# @Author: chengchao
# @Email: chengchao@topgenebio.com
# @File: app.py
import sys
from info import create_app

# from info import socketio

sys.path.append('./info/projects')
app = create_app("dev")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
