# -*- coding: utf-8 -*-

from flask_restful import Resource
from flask import request, jsonify


class FirstAPI(Resource):

    dict_result = {
        "Hello":"Welcome",
        "Author":"jyu"
    }

    def get(self):  # HTTP GET Action
        
        # get url argument - "title"
        get_web_arg_title = str(request.args.get("title"))

        response_result = dict()

        get_dict_result_key_list = [ key for key in self.dict_result.keys()]

        print(get_dict_result_key_list)

        if len(get_web_arg_title) != 0:

            # print(get_web_arg_title)
            # print( get_web_arg_title in get_dict_result_key_list)

            if get_web_arg_title in get_dict_result_key_list:

                # print(get_web_arg_title)
                response_result[str(get_web_arg_title)] =  self.dict_result[str(get_web_arg_title)]
        

        # print(dict_result)
        # print(response_result)

        return jsonify(response_result)


    def post(self):  # HTTP POST Action
        
        # Get JSON Data
        data = request.get_json(force=True) 

        get_web_arg_title = str(data["title"])
        get_web_arg_value = str(data["value"])

        run_status = False

        response_result = dict()

        if len(get_web_arg_title) != 0:

            self.dict_result[str(get_web_arg_title)] = str(get_web_arg_value)

            run_status = True

        if run_status:

            response_result["status"] = "OK"
            response_result["msg"] = "Done."

        else:

            response_result["status"] = "Error"
            response_result["msg"] = "Add Failed."

        return jsonify(response_result)


