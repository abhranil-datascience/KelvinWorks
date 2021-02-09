import cv2,io
#from google.cloud import vision
#from google.cloud.vision import types
#from google.protobuf.json_format import MessageToDict
from google.cloud import vision
from google.cloud.vision import Image
#from google.cloud import vision_v1
#from google.cloud.vision import types
#from google.cloud.vision import types
from google.protobuf.json_format import MessageToDict
import pandas as pd

def ProcessOOCLInvoice(ImageList):
    keywordlist=['Booking','Number','Print','Date','Date:','Routing','Intended','Origin',"Destination",'City:','City','Quantity','Size','Weight','Trucking']
    ############ Preprocess Image ###########
    """
    for image in ImageList:
        currentImage=cv2.imread(image)
        currentImage[currentImage<25]=0
        currentImage[(currentImage!=0) & (currentImage!=255)]=255
        cv2.imwrite(image,currentImage)"""
    ################ Invoke Vision API for 2nd page ############################
    try:
        currentfile=ImageList[0]
        with io.open(currentfile, 'rb') as gen_image_file:
            content = gen_image_file.read()
        client = vision.ImageAnnotatorClient()
        #image = vision.types.Image(content=content)
        image = vision.Image(content=content)
        response = client.text_detection(image=image)
        DictResponse=MessageToDict(response._pb)
    except:
        return "invocation error"
    ############# Check for Keywords ##################
    WholeContentDescription=DictResponse['textAnnotations'][0]['description']
    match=0
    for keyword in keywordlist:
        if keyword in WholeContentDescription:
            match = match + 1
        else:
            print(keyword)
    if match < len(keywordlist)-2:
        return "missing keywords"
    ############# create Dataframes #########################
    WordsAndCoordinates=DictResponse['textAnnotations'][1:]
    word_list=[]
    llx_list=[]
    lly_list=[]
    lrx_list=[]
    lry_list=[]
    urx_list=[]
    ury_list=[]
    ulx_list=[]
    uly_list=[]
    for i in range(0,len(WordsAndCoordinates)):
        word_list.append(WordsAndCoordinates[i]['description'])
        llx_list.append(WordsAndCoordinates[i]['boundingPoly']['vertices'][0]['x'])
        lly_list.append(WordsAndCoordinates[i]['boundingPoly']['vertices'][0]['y'])
        lrx_list.append(WordsAndCoordinates[i]['boundingPoly']['vertices'][1]['x'])
        lry_list.append(WordsAndCoordinates[i]['boundingPoly']['vertices'][1]['y'])
        urx_list.append(WordsAndCoordinates[i]['boundingPoly']['vertices'][2]['x'])
        ury_list.append(WordsAndCoordinates[i]['boundingPoly']['vertices'][2]['y'])
        ulx_list.append(WordsAndCoordinates[i]['boundingPoly']['vertices'][3]['x'])
        uly_list.append(WordsAndCoordinates[i]['boundingPoly']['vertices'][3]['y'])
    ##################### Create Dictionary for the lists #####################
    WordsAndCoordinatesDict={"Word":word_list,'llx':llx_list,'lly':lly_list,'lrx':lrx_list,'lry':lry_list,'urx':urx_list,'ury':ury_list,'ulx':ulx_list,'uly':uly_list}
    ####################### Create Dataframe ######################
    WordsAndCoordinatesDF=pd.DataFrame.from_dict(WordsAndCoordinatesDict)
    ###################### Get Values ###########################
    try:
        ################## Booking Number ########################
        BookingNumber=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Booking'])]
        BookingNumber_uly=BookingNumber['uly'].values[1]
        BookingNumber_lly=BookingNumber['lly'].values[1]
        BookingNumber_urx=BookingNumber['urx'].values[1]
        PrintDate=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Print'])]
        Print_llx=PrintDate['llx'].values[0]
        BookingNumber=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>BookingNumber_uly-40) &
                                            (WordsAndCoordinatesDF['lly']<BookingNumber_lly+40) &
                                            (WordsAndCoordinatesDF['lrx']<Print_llx-40)]
        BookingNumber=BookingNumber[~BookingNumber['Word'].isin(['Booking','Number'])]
        BookingNumber=" ".join(BookingNumber['Word'].values).strip()
        #################### PrintDate ######################
        PrintDate=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Print'])]
        PrintDate_uly=PrintDate['uly'].values[0]
        PrintDate_lly=PrintDate['lly'].values[0]
        PrintDate = WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>PrintDate_uly-20) &
                                          (WordsAndCoordinatesDF['lly']<PrintDate_lly+20)]
        PrintDate = PrintDate[~PrintDate['Word'].isin(['Print','Date','Date:'])]
        PrintDate = " ".join(PrintDate['Word'].values).replace(":","").strip()
        ################### Origin City #############################
        Routing=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Routing'])]
        Routing_lly = Routing['lly'].values[0]
        Routing_lly
        Intended=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Intended'])]
        Intended_lly = Intended['uly'].values[0]
        Intended_lly
        WordsBetweenRoutingAndIntended=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>Routing_lly) &
                                                             (WordsAndCoordinatesDF['lly']<Intended_lly)]
        Origin = WordsBetweenRoutingAndIntended[WordsBetweenRoutingAndIntended['Word'].isin(['Origin'])]
        Origin_uly = Origin['uly'].values[0]
        Origin_lly = Origin['lly'].values[0]
        Destination = WordsBetweenRoutingAndIntended[WordsBetweenRoutingAndIntended['Word'].isin(['Destination'])]
        Destination_uly = Destination['uly'].values[0]
        Destination_lly = Destination['lly'].values[0]
        Destination_ulx = Destination['ulx'].values[0]
        OriginCity = WordsBetweenRoutingAndIntended[(WordsBetweenRoutingAndIntended['uly']>Origin_uly-20) &
                                                    (WordsBetweenRoutingAndIntended['lly']<Origin_lly+20) &
                                                    (WordsBetweenRoutingAndIntended['urx']<Destination_ulx-20) &
                                                    (~WordsBetweenRoutingAndIntended['Word'].isin(['Origin','City:','City']))]
        OriginCity=" ".join(OriginCity['Word'].values)
        OriginCity=OriginCity.replace(":","").strip()
        ################# Destination ##############################
        Destination_urx = Destination['urx'].values[0]
        Destination = WordsBetweenRoutingAndIntended[(WordsBetweenRoutingAndIntended['uly']>Destination_uly-20) &
                                                     (WordsBetweenRoutingAndIntended['lly']<Destination_lly+20) &
                                                     (WordsBetweenRoutingAndIntended['llx']>Destination_urx)]
        Destination=" ".join(Destination['Word'].values)
        Destination=Destination.strip()
        ################# Quantity ##############################
        Quantity = WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Quantity'])]
        Size = WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Size'])]
        CargoWeight = WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Weight'])]
        Trucking = WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Trucking'])]
        Quantity_lly=Quantity['lly'].values[0]
        Quantity_lrx=Quantity['lrx'].values[0]
        Size_lly=Size['lly'].values[0]
        Size_llx=Size['llx'].values[0]
        CargoWeight_llx=CargoWeight['llx'].values[0]
        Trucking_uly=Trucking['uly'].values[0]
        Quantity = WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>Quantity_lly+20) &
                                 (WordsAndCoordinatesDF['uly']<Trucking_uly) &
                                 (WordsAndCoordinatesDF['urx']<Size_llx-180)]
        Quantity=" ".join(Quantity['Word'].values).strip()
        ################## Size ###########################
        Size = WordsAndCoordinatesDF[(WordsAndCoordinatesDF['lly']>Size_lly+20) &
                             (WordsAndCoordinatesDF['lly']<Trucking_uly) &
                             (WordsAndCoordinatesDF['llx']>Quantity_lrx) &
                             (WordsAndCoordinatesDF['lrx']<CargoWeight_llx-180)]
        Size=" ".join(Size['Word'].values).strip()

        return dict(msg="Success",BookingReference=BookingNumber,InvoiceDate=PrintDate,POL=OriginCity,POD=Destination,
                    QtyContainer=Quantity,No_of_CNTRS=Size)
    except Exception as e:
        print(e)
        return "unable to extract data from Google Vision API."
