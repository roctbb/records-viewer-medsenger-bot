from infrastructure import db


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
            "optional_categories": self.optional_categories,
            "categories": self.required_categories + (self.optional_categories if self.optional_categories else []),
            'options': self.options
        }

        return serialized
