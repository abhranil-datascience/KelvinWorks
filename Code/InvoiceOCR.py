################### Import Statements #############################
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import io,os,random,requests,string,fitz,cv2
from PIL import Image
import pandas as pd
from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToDict
from pdf2image import convert_from_path
from YongMingTemplate import ExtractDataForYongMingTemplate
from MaerskTemplate import ProcessMaerskInvoice
from EvergreenTemplate import ProcessEvergreenInvoice
####################################################################
############### Declare Constants ############################
DownloadDirectory="../Downloads/"
ExtractedImageDirectory="../Images/"
letters = string.ascii_lowercase
Templates=dict(YangMingTemplate=['yang','ming'],
               MaerskTemplate=['maersk'],
               EvergreenTemplate=['evergreen'])
############## Create Flask App ##############################
app = Flask(__name__)
api = Api(app)
#############################################################
################### Create Method API #######################
class InvoiceOCRGVA(Resource):
    def post(self):
        ############ Get Input Params ################
        data = request.get_json()
        file_url = data['file_url']
        file_type = data['file_type'].lower()
        ### Check If PDF and Image Directory Exists ###
        if not(os.path.exists(DownloadDirectory)):
            os.mkdir(DownloadDirectory)
        if not(os.path.exists(ExtractedImageDirectory)):
            os.mkdir(ExtractedImageDirectory)
        ############# Download File ##################
        file_type=file_type.lower()
        random_integer=str(random.randint(100000, 999999))
        random_letters=''.join(random.choice(letters) for i in range(5))
        random_combination=random_integer+random_letters
        FileName="File_"+random_combination
        DownloadFilePath=DownloadDirectory+FileName
        ExtractedImageFileName=ExtractedImageDirectory+FileName
        ########### Check File Type ####################
        if file_type == "png":
            FileName=FileName+".png"
        elif file_type == "pdf":
            FileName=FileName+".pdf"
        else:
            return {'msg':'Error','description':'Unsupported file extension.'}
        ########## Download File ###################
        try:
            response=requests.get(str(file_url))
        except:
            return{'msg':'Error','description':'Unable to download file. Please check the file url again.'}
        ############# Write downloaded file to local ##################
        try:
            with open(DownloadFilePath,'wb') as f:
                f.write(response.content)
        except:
            return{'msg':'Error','description':'Unable to save downloaded file.'}
        ############## Save Image from Downloaded File ###################
        ImageList=[]
        if file_type == "png":
            ExtractedImageFilePath=ExtractedImageFileName+".png"
            try:
                im = Image.open(DownloadFilePath)
            except:
                os.remove(DownloadFilePath)
                return{'msg':'Error','description':'Unable to open downloaded file.'}
            try:
                im.save(ExtractedImageFilePath)
                ImageList.append(ExtractedImageFilePath)
                os.remove(DownloadFilePath)
            except:
                os.remove(DownloadFilePath)
                return {'msg':'Error','description':'Unable to save image file.'}
        elif file_type == "pdf":
            try:
                print("--------Inside-------------------")
                images = convert_from_path(DownloadFilePath,dpi=500)
                print(len(images))
                for pagenum,image in enumerate(images):
                    image=image.convert('LA')
                    ExtractedImageFilePath=ExtractedImageFileName+"_Page"+str(pagenum+1)+".png"
                    image.save(ExtractedImageFilePath)
                    ImageList.append(ExtractedImageFilePath)
                os.remove(DownloadFilePath)
            except:
                os.remove(DownloadFilePath)
                return {'msg':'Error','description':'Unable to convert pdf to image.'}
        else:
            return {'msg':'Error','description':'Unsupported File Format.'}
        ##### Check and compress File Size #######
        for image in ImageList:
            while os.stat(image).st_size > 9437184:
                im = Image.open(image)
                im.save(image,optimize=True,quality=80)
        ########### Check For Templates ###########
        FirstImage=ImageList[0]
        try:
            with io.open(FirstImage, 'rb') as gen_image_file:
                content = gen_image_file.read()
        except:
            for image in ImageList:
                os.remove(image)
            return {'msg':'Error','description':'Unable to read extracted image for template detection.'}
        try:
            client = vision.ImageAnnotatorClient()
            image = vision.types.Image(content=content)
            response = client.text_detection(image=image)
        except:
            for image in ImageList:
                os.remove(image)
            return {'msg':'Error','description':'Unable to invoke Google vision api.'}
        ############ Create Dict for Vision API response ###########
        DictResponse=MessageToDict(response)
        WholeContentDescription=DictResponse['textAnnotations'][0]['description'].lower()
        ################# Match Template ############################
        TemplateName=""
        for templatename,keywords in Templates.items():
            matchfound=True
            for keyword in keywords:
                if keyword not in WholeContentDescription:
                    matchfound=False
            if matchfound:
                TemplateName=templatename
                break
        if TemplateName=="":
            for image in ImageList:
                os.remove(image)
            return {'msg':'Error','description':'Unable to find a matching Template.'}
        ############## Yang Ming Template #############################
        if TemplateName=="YangMingTemplate":
            try:
                response=ExtractDataForYongMingTemplate(DictResponse)
                if response == "missing keywords":
                    for image in ImageList:
                        os.remove(image)
                    return {'msg':'Error','description':'Google Vision API unable to find all the mandatory keywords for Yang Ming Invoice.'}
                else:
                    for image in ImageList:
                        os.remove(image)
                    return response
            except:
                for image in ImageList:
                    os.remove(image)
                return {'msg':'Error','description':'Unknown issue occured. Please connect with system administrator with the input file.'}
        ############## Maersk Template #############################
        if TemplateName=="MaerskTemplate":
            try:
                response=ProcessMaerskInvoice(ImageList)
                if response == "invocation error":
                    for image in ImageList:
                        os.remove(image)
                    return {'msg':'Error','description':'Unable to Invoke Google Vision API'}
                elif response == "missing keywords":
                    for image in ImageList:
                        os.remove(image)
                    return {'msg':'Error','description':'Google Vision API unable to find all the mandatory keywords for Maersk Invoice.'}
                elif response == "unable to extract data from Google Vision API":
                    for image in ImageList:
                        os.remove(image)
                    return {'msg':'Error','description':'Unable to extract data from Google Vision API.'}
                else:
                    for image in ImageList:
                        os.remove(image)
                    return response
            except:
                for image in ImageList:
                    os.remove(image)
                return {'msg':'Error','description':'Unknown issue occured. Please connect with system administrator with the input file.'}
        ############## Evergreen Template #############################
        if TemplateName=="EvergreenTemplate":
            try:
                response=ProcessEvergreenInvoice(ImageList)
                if response == "invocation error":
                    for image in ImageList:
                        os.remove(image)
                    return {'msg':'Error','description':'Unable to Invoke Google Vision API'}
                elif response == "missing keywords":
                    for image in ImageList:
                        os.remove(image)
                    return {'msg':'Error','description':'Google Vision API unable to find all the mandatory keywords for Evergreen Invoice.'}
                elif response == "unable to extract data from Google Vision API":
                    for image in ImageList:
                        os.remove(image)
                    return {'msg':'Error','description':'Unable to extract data from Google Vision API.'}
                else:
                    for image in ImageList:
                        os.remove(image)
                    return response
            except:
                for image in ImageList:
                    os.remove(image)
                return {'msg':'Error','description':'Unknown issue occured. Please connect with system administrator with the input file.'}
#############################################################
#################### Configure URLs #########################
api.add_resource(InvoiceOCRGVA,'/InvoiceOCR')
#############################################################
#################### Run App ################################
if __name__ == '__main__':
    app.run(debug = True)
#############################################################
