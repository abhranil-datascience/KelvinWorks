from pdf2image import convert_from_path
import random,string,cv2,io,os
from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToDict

def CheckTemplateForPDF(InputFile):
    ############ declare constants ##################
    letters = string.ascii_lowercase
    imagedirectory="../Images/"
    client = vision.ImageAnnotatorClient()
    ############ convert pdf to image ##################
    try:
        images = convert_from_path(InputFile,dpi=500)
    except:
        return "unable to convert pdf to image"
    ImageFile=""
    try:
        for image_num in range(1):
            grayscaledimage=images[image_num].convert('LA')
            randomNumber=random.randint(10000,99999)
            randomAlphabets=''.join(random.choice(letters) for i in range(5))
            imagename="Image"+str(randomNumber)+randomAlphabets+".png"
            image_path=imagedirectory+imagename
            ImageFile=image_path
            grayscaledimage.save(image_path)
    except:
        os.remove(InputFile)
        return "unable to convert colored image to grayscaledimage"
    try:
        with io.open(ImageFile, 'rb') as gen_image_file:
            content = gen_image_file.read()
        image = vision.types.Image(content=content)
        response = client.text_detection(image=image)
        DictResponse=MessageToDict(response)
    except:
        os.remove(ImageFile)
        return "unable to invoke Google Vision API"
    try:
        WholeContentDescription=DictResponse['textAnnotations'][0]['description']
        if "Maersk" in WholeContentDescription:
            os.remove(ImageFile)
            return "maersk"
        else:
            os.remove(ImageFile)
            return "no matching template found"
    except:
        os.remove(ImageFile)
        return "unable to parse vision api response"
