from infrastructure import db


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True)

    agent_token = db.Column(db.String(255), nullable=True)
    doctor_agent_token = db.Column(db.String(255), nullable=True)
    patient_agent_token = db.Column(db.String(255), nullable=True)

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
