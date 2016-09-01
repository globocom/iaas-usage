from flask import request
from app import app
from app.auditing.event_reader import CloudstackEventReader


@app.route('/consume_audit_queue')
def consume_audit_queue():
    region = request.args.get('region')
    if region is None:
        return "Parameter 'region' should be informed"
    CloudstackEventReader(region).read_events()
    return "Execution ended for region %s" % region
