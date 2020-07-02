################### Import Statements #############################
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
import io,os,random,requests,string,fitz
from PIL import Image
import pandas as pd
from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToDict
from YongMingTemplate import ExtractDataForYongMingTemplate
from CheckTemplateForPDFWithImages import CheckTemplateForPDF
from MaerskTemplate import ProcessMaerskInvoice
####################################################################
############### Declare Constants ############################
DownloadDirectory="../Downloads/"
ExtractedImageDirectory="../Images/"
letters = string.ascii_lowercase
Templates=dict(Template1=['booking ref','nama kapal','etd','eta dest','si no','est.open stack','est.closing time','no.of cntrs','commodity','pol',
                          'transit port','pod','transit terminal','final dest','kontainer dapat diambil di','approved'])
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
        if file_type == "png":
            ExtractedImageFilePath=ExtractedImageFileName+".png"
            try:
                im = Image.open(DownloadFilePath)
            except:
                os.remove(DownloadFilePath)
                return{'msg':'Error','description':'Unable to open downloaded file.'}
            try:
                im.save(ExtractedImageFilePath)
                os.remove(DownloadFilePath)
            except:
                os.remove(DownloadFilePath)
                return {'msg':'Error','description':'Unable to save image file.'}
        elif file_type == "pdf":
            ############ Check For Maersk Invoice ####################
            template=None
            doc = fitz.open(DownloadFilePath)
            page = doc[0]
            text = page.getText().lower()
            if len(text)!=0 :
                if "maersk" in text:
                    template="maersk"
            else:
                template=CheckTemplateForPDF(DownloadFilePath)
            if template=="maersk":
                try:
                    MaerskInvoiceResponse = ProcessMaerskInvoice(DownloadFilePath)
                    if type(MaerskInvoiceResponse) is dict:
                        return  MaerskInvoiceResponse
                    else:
                        return {'msg':'Error','description':MaerskInvoiceResponse}
                except:
                    return {'msg':'Error','description':'Unable to perform OCR.'}
            else:
                os.remove(DownloadFilePath)
                return {'msg':'Error','description':'No Matching Template Found for the given PDF'}
        ##### Check and compress File Size #######
        while os.stat(ExtractedImageFilePath).st_size > 9437184:
            im = Image.open(ExtractedImageFilePath)
            im.save(ExtractedImageFilePath,optimize=True,quality=80)
        ########## Call Google Vision API ########
        with io.open(ExtractedImageFilePath, 'rb') as gen_image_file:
            content = gen_image_file.read()
        try:
            client = vision.ImageAnnotatorClient()
            image = vision.types.Image(content=content)
            response = client.text_detection(image=image)
            os.remove(ExtractedImageFilePath)
        except:
            os.remove(ExtractedImageFilePath)
            return {'msg':'Error','description':'Unable to invoke Google vision api.'}
        ############ Create Dict for Vision API response ###########
        DictResponse=MessageToDict(response)
        ########## Check If all words found or not ##################
        WholeContentDescription=DictResponse['textAnnotations'][0]['description'].lower()
        count=0
        IdentifiedTemplate=""
        for template,list_of_words in Templates.items():
            for unique_words in list_of_words:
                if unique_words in WholeContentDescription:
                    count=count+1
            if count==len(list_of_words):
                IdentifiedTemplate=template
                break
        if IdentifiedTemplate=="":
            return {'msg':'Error','description':'Unable to find a matching Template.'}
        if IdentifiedTemplate == "Template1":
            try:
                WordsAndCoordinates=DictResponse['textAnnotations'][1:]
                ResponseDict=ExtractDataForYongMingTemplate(WordsAndCoordinates)
            except:
                return {'msg':'Error','description':'Unable to process Google Vision API response.'}
            return ResponseDict
        else:
            return {'msg':'Error','description':'Unknown issue occured. Please connect with system administrator'}
#############################################################
#################### Configure URLs #########################
api.add_resource(InvoiceOCRGVA,'/InvoiceOCR')
#############################################################
#################### Run App ################################
if __name__ == '__main__':
    app.run(debug = True)
#############################################################
