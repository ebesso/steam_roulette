from flask import Blueprint

web = Blueprint('web bp', __name__, template_folder='templates')

from . import routes, events, others