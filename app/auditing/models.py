from datetime import datetime
from flask import json
from marshmallow import Schema, fields
from app import db


class Event(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(30))
    resource_type  = db.Column(db.String(30))
    resource_id = db.Column(db.String(50))
    resource_name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    username = db.Column(db.String(80))
    account = db.Column(db.String(80))
    date = db.Column(db.DateTime)
    region = db.Column(db.String(5))
    original_event = db.Column(db.String(3000))

    def __init__(self, action, resource_id, description, username, account, date, region, original_event):
        self.action = action
        self.resource_id = resource_id
        self.description = description
        self.username = username
        self.account = account
        self.date = date
        self.region = region
        self.original_event = original_event

    @property
    def details(self):
        return json.loads(self.original_event)

    @property
    def date_time(self):
        return self.date.strftime('%d/%m/%Y %H:%M:%S')

    @staticmethod
    def find_all_by(parameters, page, page_size):
        page = 1 if page is None else page
        page_size = max(page_size, 10)

        query = Event.query.filter(Event.region == parameters.get('region'))
        if parameters['start_date'] and  parameters['end_date']:
            query = query.filter(Event.date >= parameters.get('start_date'))
            query = query.filter(Event.date <= parameters.get('end_date'))
        return query.order_by(Event.date.desc()).paginate(page, page_size)

class EventSchema(Schema):

    details = fields.Dict()

    class Meta:
        fields = ("id", "action", "resource_id", "description", "username", "account", "date_time", "region", "details")
