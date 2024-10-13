from repository.database import db


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    bank_payment_id = db.Column(db.String(200), nullable=True)
    qrcode = db.Column(db.String(100), nullable=True)
    expiration_date = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "is_paid": self.is_paid,
            "bank_payment_id": self.bank_payment_id,
            "qrcode": self.qrcode,
            "expiration_date": self.expiration_date
        }
