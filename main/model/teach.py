import enum
from main.__init__ import db

class TeachMember(db.Model):
    __tablename__ = "teach_members"
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("teach_groups.id"), primary_key=True)
    shown_name = db.Column(db.String(150))

    active = db.Column(db.Boolean)
    is_admin = db.Column(db.Boolean)

class TeachGroup(db.Model):
    __tablename__ = "teach_groups"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(8), unique=True)
    name = db.Column(db.String(75))

    org_name = db.Column(db.String(150))
    org_rep_name = db.Column(db.String(150))
    org_email = db.Column(db.String(150))

    active = db.Column(db.Boolean)
    is_demo = db.Column(db.Boolean)

    #members = db.relationship('User', secondary=TeachMember, lazy='subquery', backref=db.backref('user', lazy=True))

class TeachInvitations(db.Model):
    __tablename__ = "teach_invitations"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("teach_groups.id"))
    token = db.Column(db.String(8), primary_key=True)
    expires_after = db.Column(db.DateTime, nullable=True)
    left_uses_count = db.Column(db.Integer, nullable=True)

class TeachAssignmentTypes(enum.Enum):
    CLICK_TO_RESOLVE = 1
    COURSE = 2
    ASSIGNMENT_WITH_SUBMISSION = 3

class TeachAssignments(db.Model):
    __tablename__ = "teach_assignments"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teach_groups.id"))
    token = db.Column(db.String(16), unique=True)
    associated_course = db.Column(db.Integer, db.ForeignKey("courses.id"))

    type = db.Column(db.Enum(TeachAssignmentTypes))
    title = db.Column(db.String(100))
    comment = db.Column(db.Text)

    max_points_for_completion = db.Column(db.SmallInteger)

    active = db.Column(db.Boolean)

    available_after = db.Column(db.DateTime, nullable=True)
    to_be_completed_before = db.Column(db.DateTime, nullable=True)

class TeachAssignmentCompletions(db.Model):
    __tablename__ = "teach_assignment_completions"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teach_groups.id"))
    assignment_id = db.Column(db.Integer, db.ForeignKey("teach_assignments.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    token = db.Column(db.String(16), unique=True)

    submission_comment = db.Column(db.Text)
    submission_file_name = db.Column(db.String(250))
    submission_at = db.Column(db.DateTime, nullable=True)
    is_submission_late = db.Column(db.Boolean)

    points_for_submission = db.Column(db.SmallInteger)
    points_graded_by_teacher = db.Column(db.SmallInteger)
    
    comment_by_teacher = db.Column(db.TEXT)
