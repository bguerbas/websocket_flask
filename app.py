from flask import Flask, request, jsonify, send_file, render_template
from repository.database import db
from models.payment import Payment
from datetime import datetime, timedelta
from payments.pix import Pix
from flask_socketio import SocketIO


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret_key'

db.init_app(app)
socketio = SocketIO(app)


# Create the register in the database
@app.route('/payments/pix', methods=['POST'])
def create_pix_payment():
    data = request.get_json()
    if 'amount' not in data:
        return jsonify({"message": "Amount is required"}), 400

    expiration_date = datetime.now() + timedelta(minutes=5)

    new_payment = Payment(amount=data['amount'], expiration_date=expiration_date)

    # Create the payment in the bank
    pix_obj = Pix()
    data_payment_pix = pix_obj.create_payment()

    # Save the bank_payment_id and qrcode in the database
    new_payment.bank_payment_id = data_payment_pix['bank_payment_id']
    new_payment.qrcode = data_payment_pix['qrcode']

    db.session.add(new_payment)
    db.session.commit()

    return jsonify({"message": "Pix payment created", "payment": new_payment.to_dict()})


# Get qrcode
@app.route('/payments/pix/qrcode/<file_name>', methods=['GET'])
def get_qrcode(file_name):
    return send_file(f'static/img/{file_name}.png', mimetype='image/png')


# Confirm the payment (webhook)
@app.route('/payments/pix/confirmation', methods=['POST'])
def confirm_pix_payment():
    data = request.get_json()

    # validate the payment in the bank
    if "bank_payment_id" not in data and "amount" not in data:
        return jsonify({"message": "Invalid payment data"}), 400

    payment = Payment.query.filter_by(bank_payment_id=data['bank_payment_id']).first()

    if not payment or payment.is_paid:
        return jsonify({"message": "Payment not found"}), 404

    if data.get('amount') != payment.amount:
        return jsonify({"message": "Invalid payment data"}), 400

    payment.is_paid = True
    db.session.commit()

    # Send the confirmation to the client
    socketio.emit(f'payment-confirmed-{payment.id}')

    return jsonify({"message": "Pix payment confirmed"})


@app.route('/payments/pix/<int:payment_id>', methods=['GET'])
def get_pix_payment(payment_id):
    # Get the payment in the database
    payment = Payment.query.get(payment_id)

    if not payment:
        return render_template('404.html')

    # Check if the payment is paid
    if payment.is_paid:
        return render_template('confirmed_payment.html',
                               payment_id=payment.id,
                               amount=payment.amount)

    return render_template('payment.html',
                           payment_id=payment.id,
                           amount=payment.amount,
                           host="http://127.0.0.1:5000",
                           qrcode=payment.qrcode)


# websocket
@socketio.on('connect')
def handle_connect():
    print('Client connected to the server')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from the server')


if __name__ == '__main__':
    socketio.run(app, debug=True)


"""
# Create the db in terminal
flask shell
>>> db.create_all()
>>> exit()
# Create the db with models
flask shell
>>> db.drop_all()
>>> db.create_all()
>>> exit()
"""