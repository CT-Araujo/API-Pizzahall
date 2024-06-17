from django.http import HttpResponse
from pixqrcode import PixQrCode
import base64

def PagamentoPix(nome, chave, cidade, valor):
    pix = PixQrCode(str(nome), str(chave), str(cidade), str(valor))
    payload = pix.generate_code()
        
    import qrcode
    import qrcode.image.svg

    factory = qrcode.image.svg.SvgPathImage

    img = qrcode.make(str(payload), image_factory=factory)
    stringImage = img.to_string(encoding='unicode')
    encoded_svg = base64.b64encode(stringImage.encode('utf-8')).decode('utf-8')
    
    return {'payload': payload, 'svg': encoded_svg}
    
    

