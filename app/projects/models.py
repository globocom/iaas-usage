from app import db


class Project(db.Model):

    __tablename__ = 'project'
    __table_args__ = {'useexisting': True}

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    process_id = db.Column(db.String(100), nullable=False)
    business_service_id = db.Column(db.String(100), nullable=True)
    client_id = db.Column(db.String(100), nullable=True)
    component_id = db.Column(db.String(100), nullable=True)
    sub_component_id = db.Column(db.String(100), nullable=True)
    product_id = db.Column(db.String(100), nullable=True)
    detailed_usage = db.Column(db.Boolean, nullable=True)

    def __init__(self, **kwargs):
        super(Project, self).__init__(**kwargs)

    @staticmethod
    def find_by_uuid(id):
        return Project.query.filter_by(uuid=id).first()
