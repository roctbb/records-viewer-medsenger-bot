from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# models
class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True)
    agent_token = db.Column(db.String(255), nullable=True)

    is_admin = db.Column(db.Boolean, default=False)
    params = db.Column(db.JSON, default=None)

    def as_dict(self, native=False):
        serialized = {
            "id": self.id,
            "is_active": self.is_active
        }

        if native:
            serialized['agent_token'] = self.agent_token

        return serialized


class CategoryGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    type = db.Column(db.String(255), nullable=True)
    required_categories = db.Column(db.JSON, nullable=True)
    optional_categories = db.Column(db.JSON, nullable=True)
    options = db.Column(db.JSON, nullable=True)

    def as_dict(self):
        serialized = {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "required_categories": self.required_categories,
            "categories": self.required_categories + (self.optional_categories if self.optional_categories else []),
            'options': self.options
        }

        return serialized
