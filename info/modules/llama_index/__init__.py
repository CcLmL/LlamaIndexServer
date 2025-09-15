from flask import Blueprint

llama_index_blu = Blueprint("llama_index", __name__, url_prefix='')

from .views import *
