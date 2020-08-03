# -*- coding: utf-8 -*-

from Startup import app


@app.errorhandler(404)
def page_not_found(e):

    return 'Bed Request', 404


@app.route("/", methods=['GET'])
def index():

    return "Restful API."
