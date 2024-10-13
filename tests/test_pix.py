import sys
import pytest
import os
from payments.pix import Pix

sys.path.append('../')


def test_pix_create_payment():
    pix = Pix()
    data_payment_pix = pix.create_payment(base_dir="../")

    assert "bank_payment_id" in data_payment_pix
    assert "qrcode" in data_payment_pix

    qrcode_path = data_payment_pix['qrcode']
    assert os.path.isfile(f'../static/img/{qrcode_path}.png')

