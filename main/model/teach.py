from main.__init__ import db

class TeachMember(db.Model):
    __tablename__ = "teach_members"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("teach_groups.id"), primary_key=True)
    shown_name = db.Column(db.String(150))

    active = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)

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

    #members = db.relationship('User', secondary=TeachMember, lazy='subquery', backref=db.backref('user', lazy=True))
