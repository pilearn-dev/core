from main.__init__ import db

class TeachGroup(db.Model):
    __tablename__ = "teach_groups"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(8), unique=True)
    name = db.Column(db.String(75))

    org_name = db.Column(db.String(150))
    org_rep_name = db.Column(db.String(150))
    org_email = db.Column(db.String(150))

    active = db.Column(db.Boolean)
    is_demo = db.Column(db.Boolean)
