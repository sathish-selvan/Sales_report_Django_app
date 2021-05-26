import base64 , uuid
from django.core.files.base import ContentFile

def get_report_image(data):
    _,str_image = data.split(';base64')
    decode_imag = base64.b64decode(str_image)
    imag_name = str(uuid.uuid4())[:10] + ".png"
    data = ContentFile(decode_imag, name=imag_name)
    return data