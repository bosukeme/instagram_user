"""
This extracts used to get instragram users
"""
from flask import request
from flask_restful import Resource
import instagram_user
import pandas as pd
from ast import literal_eval
#from schema import DataSchema
import json

#data_schema = DataSchema()

class Instagram(Resource):   

    def post(self):
        #data=instagram_user.entities
        
        result=instagram_user.call_all_func()
        #result=instagram_user.call_all_func()

        return {
            'Entity data': literal_eval(result)
        }

