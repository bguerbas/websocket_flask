import uuid
import qrcode


class Pix:
    def __init__(self):
        pass

    def create_payment(self, base_dir=""):
        """ Create the payment in the bank """
        # Integration with the bank
        bank_payment_id = str(uuid.uuid4())

        # qrcode
        hash_payment = f'hash_payment_{bank_payment_id}'
        img = qrcode.make(hash_payment)
        name_img = f'qr_code_payment_{bank_payment_id}'
        img.save(f'{base_dir}static/img/{name_img}.png')

        return {"bank_payment_id": bank_payment_id,
                "qrcode": name_img}