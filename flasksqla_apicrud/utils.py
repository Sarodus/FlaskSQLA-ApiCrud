import json
import datetime
from flask import make_response


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        return super(CustomEncoder, self).default(obj)


def custom_json_output(data, code, headers=None):
    dumped = json.dumps(data, cls=CustomEncoder)
    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    return resp
