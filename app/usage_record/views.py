import datetime
from flask import request
from app import UsageRecordReader, app


@app.route('/index_usage')
def index_usage():
    try:
        date_str = request.args.get('date', None)
        if(date_str):
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
        region = request.args.get('region')
        if region is None:
            return "Parameter 'region' should be informed"

        UsageRecordReader(region).index_usage(date_str)
        return "Execution ended for region %s" % region
    except ValueError:
        return "Incorrect date format, should be YYYY-MM-DD"

