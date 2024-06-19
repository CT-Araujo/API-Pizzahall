from django.http import HttpResponse
from pixqrcode import PixQrCode
import base64
import io

def PagamentoPix(nome, chave, cidade, valor):
    pix = PixQrCode(str(nome), str(chave), str(cidade), str(valor))
    payload = pix.generate_code()
        
    import qrcode
    import qrcode.image.svg

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()

    encoded_img = base64.b64encode(img_bytes).decode('utf-8')
    decoded_img_bytes = base64.b64decode(encoded_img)

    img_bytes = io.BytesIO(decoded_img_bytes)



    
    return {'payload': payload, 'png': encoded_img,"nome": nome}
    
    

