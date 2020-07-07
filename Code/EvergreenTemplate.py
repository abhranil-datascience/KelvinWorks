import cv2,io
from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToDict
import pandas as pd

def ProcessEvergreenInvoice(ImageList):
    keywordlist=['BOOKING','VESSEL','VOYAGE','CARRIER','OF','RECEIPT','LOADING','TIME',"DATE",'DISCHARGING','DESTINATION','CUSTOMER','SHIPPER','TYPE','MODE','PRE-CARRIAGE','COMMODITY','UP','TO','GWT+TARE','LIMIT']
    ############ Preprocess Image ###########
    for image in ImageList:
        currentImage=cv2.imread(image)
        currentImage[currentImage<25]=0
        currentImage[(currentImage!=0) & (currentImage!=255)]=255
        cv2.imwrite(image,currentImage)
    ################ Invoke Vision API for 2nd page ############################
    try:
        currentfile=ImageList[0]
        with io.open(currentfile, 'rb') as gen_image_file:
            content = gen_image_file.read()
        client = vision.ImageAnnotatorClient()
        image = vision.types.Image(content=content)
        response = client.text_detection(image=image)
        DictResponse=MessageToDict(response)
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
    if match != len(keywordlist):
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
        no=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['BOOKING'])]
        No_uly=no['uly'].values[2]
        No_lly=no['lly'].values[2]
        No_urx=no['urx'].values[2]
        BookingNumber=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>No_uly-20) &
                                            (WordsAndCoordinatesDF['lly']<No_lly+20) &
                                            (WordsAndCoordinatesDF['llx']>No_urx+70)]
        BookingNumber="".join(BookingNumber['Word'].values).replace(":","")
        #################### Vessel/Voyage ######################
        Vessel=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['VESSEL/VOYAGE'])]
        Vessel_uly=Vessel['uly'].values[0]
        Vessel_lly=Vessel['lly'].values[0]
        Vessel_urx=Vessel['urx'].values[0]
        Vessel=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>Vessel_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<Vessel_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>Vessel_urx)]
        Vessel=" ".join(Vessel['Word'].values).replace(":","").strip()
        ################### Carrier #############################
        CARRIER=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['CARRIER'])]
        CARRIER_uly=CARRIER['uly'].values[0]
        CARRIER_lly=CARRIER['lly'].values[0]
        CARRIER_urx=CARRIER['urx'].values[0]
        CARRIER=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>CARRIER_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<CARRIER_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>CARRIER_urx)]
        CARRIER=" ".join(CARRIER['Word'].values).replace(":","").strip()
        ################# OnBehalfOf ##############################
        OnBehalfOf=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['OF'])]
        OnBehalfOf_uly=OnBehalfOf['uly'].values[0]
        OnBehalfOf_lly=OnBehalfOf['lly'].values[0]
        OnBehalfOf_urx=OnBehalfOf['urx'].values[0]
        OnBehalfOf=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>OnBehalfOf_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<OnBehalfOf_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>OnBehalfOf_urx)]
        OnBehalfOf=" ".join(OnBehalfOf['Word'].values).replace(":","").strip()
        ################# PlaceOfReceipt ##############################
        PlaceOfReceipt=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['RECEIPT'])]
        PlaceOfReceipt_uly=PlaceOfReceipt['uly'].values[0]
        PlaceOfReceipt_lly=PlaceOfReceipt['lly'].values[0]
        PlaceOfReceipt_urx=PlaceOfReceipt['urx'].values[0]
        PlaceOfReceipt=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>PlaceOfReceipt_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<PlaceOfReceipt_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>PlaceOfReceipt_urx)]
        PlaceOfReceipt=" ".join(PlaceOfReceipt['Word'].values).replace(":","").strip()
        ################### PlaceOfLoading #############################
        PlaceOfLoading=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['LOADING'])]
        PlaceOfLoading_uly=PlaceOfLoading['uly'].values[0]
        PlaceOfLoading_lly=PlaceOfLoading['lly'].values[0]
        PlaceOfLoading_urx=PlaceOfLoading['urx'].values[0]
        PlaceOfLoading=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>PlaceOfLoading_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<PlaceOfLoading_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>PlaceOfLoading_urx)]
        PlaceOfLoading=" ".join(PlaceOfLoading['Word'].values).replace(":","").strip()
        ################## ClosingTime ###########################
        ClosingTime=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['TIME'])]
        ClosingTime_uly=ClosingTime['uly'].values[0]
        ClosingTime_lly=ClosingTime['lly'].values[0]
        ClosingTime_urx=ClosingTime['urx'].values[0]
        ClosingTime=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>ClosingTime_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<ClosingTime_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>ClosingTime_urx)]
        ClosingTime=" ".join(ClosingTime['Word'].values).strip()[1:]
        ################# CutOffDate ##############################
        CutOffDate=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['DATE'])]
        CutOffDate_uly=CutOffDate['uly'].values[0]
        CutOffDate_lly=CutOffDate['lly'].values[0]
        CutOffDate_urx=CutOffDate['urx'].values[0]
        CutOffDate=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>CutOffDate_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<CutOffDate_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>CutOffDate_urx)]
        CutOffDate=" ".join(CutOffDate['Word'].values).strip()[1:]
        ################### Loading ETA ############################
        LoadingEtaDate=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['DATE'])]
        LoadingEtaDate_uly=LoadingEtaDate['uly'].values[1]
        LoadingEtaDate_lly=LoadingEtaDate['lly'].values[1]
        LoadingEtaDate_urx=LoadingEtaDate['urx'].values[1]
        LoadingEtaDate=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>LoadingEtaDate_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<LoadingEtaDate_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>LoadingEtaDate_urx)]
        LoadingEtaDate=" ".join(LoadingEtaDate['Word'].values).strip()[1:]
        ################# PortOfDischarging #######################
        PortOfDischarging=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['DISCHARGING'])]
        PortOfDischarging_uly=PortOfDischarging['uly'].values[0]
        PortOfDischarging_lly=PortOfDischarging['lly'].values[0]
        PortOfDischarging_urx=PortOfDischarging['urx'].values[0]
        PortOfDischarging=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>PortOfDischarging_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<PortOfDischarging_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>PortOfDischarging_urx)]
        PortOfDischarging=" ".join(PortOfDischarging['Word'].values).strip()[1:]
        ################ FinalDestination ##########################
        FinalDestination=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['DESTINATION'])]
        FinalDestination_uly=FinalDestination['uly'].values[0]
        FinalDestination_lly=FinalDestination['lly'].values[0]
        FinalDestination_urx=FinalDestination['urx'].values[0]
        FinalDestination=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>FinalDestination_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<FinalDestination_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>FinalDestination_urx)]
        FinalDestination=" ".join(FinalDestination['Word'].values).strip()[1:]
        ############### DestinationEtaDate #########################
        DestinationEtaDate=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['DATE'])]
        DestinationEtaDate_uly=DestinationEtaDate['uly'].values[2]
        DestinationEtaDate_lly=DestinationEtaDate['lly'].values[2]
        DestinationEtaDate_urx=DestinationEtaDate['urx'].values[2]
        DestinationEtaDate=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>DestinationEtaDate_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<DestinationEtaDate_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>DestinationEtaDate_urx)]
        DestinationEtaDate=" ".join(DestinationEtaDate['Word'].values).strip()[1:]
        ################ Customer ###########################
        Customer=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['CUSTOMER'])]
        Customer_uly=Customer['uly'].values[0]
        Customer_lly=Customer['lly'].values[0]
        Customer_urx=Customer['urx'].values[0]
        Customer=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>Customer_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<Customer_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>Customer_urx)]
        Customer=" ".join(Customer['Word'].values).strip()[1:].strip()
        ################### Shipper ############################
        Shipper=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['SHIPPER'])]
        Shipper_uly=Shipper['uly'].values[0]
        Shipper_lly=Shipper['lly'].values[0]
        Shipper_urx=Shipper['urx'].values[0]
        Shipper=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>Shipper_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<Shipper_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>Shipper_urx)]
        Shipper=" ".join(Shipper['Word'].values).strip()[1:].strip()
        ################### Service Mode ############################
        ServiceMode=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['TYPE/MODE'])]
        ServiceMode_uly=ServiceMode['uly'].values[0]
        ServiceMode_lly=ServiceMode['lly'].values[0]
        ServiceMode_urx=ServiceMode['urx'].values[0]
        ServiceMode=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>ServiceMode_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<ServiceMode_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>ServiceMode_urx)]
        ServiceMode=" ".join(ServiceMode['Word'].values).strip()[1:].strip()
        ################# PRE_CARRIAGE #############################
        PRE_CARRIAGE=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['PRE-CARRIAGE'])]
        PRE_CARRIAGE_uly=PRE_CARRIAGE['uly'].values[0]
        PRE_CARRIAGE_lly=PRE_CARRIAGE['lly'].values[0]
        PRE_CARRIAGE_urx=PRE_CARRIAGE['urx'].values[0]
        PRE_CARRIAGE=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>PRE_CARRIAGE_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<PRE_CARRIAGE_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>PRE_CARRIAGE_urx)]
        PRE_CARRIAGE=" ".join(PRE_CARRIAGE['Word'].values).strip()[1:].strip()
        ###################### Commodity ############################
        Commodity=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['COMMODITY'])]
        Commodity_uly=Commodity['uly'].values[0]
        Commodity_lly=Commodity['lly'].values[0]
        Commodity_urx=Commodity['urx'].values[0]
        Commodity=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>Commodity_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<Commodity_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>Commodity_urx)]
        Commodity=" ".join(Commodity['Word'].values).strip()[1:].strip()
        ###################### EmptyPickUpAt ###############################
        EmptyPickUpAt=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['UP'])]
        EmptyPickUpAt_uly=EmptyPickUpAt['uly'].values[0]
        EmptyPickUpAt_lly=EmptyPickUpAt['lly'].values[0]
        EmptyPickUpAt_urx=EmptyPickUpAt['urx'].values[0]
        EmptyPickUpAt=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>EmptyPickUpAt_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<EmptyPickUpAt_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>EmptyPickUpAt_urx)]
        EmptyPickUpAt=" ".join(EmptyPickUpAt['Word'].values).strip().strip()
        desired_index=EmptyPickUpAt.index(":")
        EmptyPickUpAt=EmptyPickUpAt[desired_index+1:]
        ####################### QuantityandType ########################
        GWT=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['GWT+TARE'])]
        Limit=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['LIMIT'])]
        GWT_LLX=GWT['llx'].values[0]
        Limit_LLX=Limit['llx'].values[0]
        GWT_LLY=GWT['lly'].values[0]
        QuantityandType=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['lly']>GWT_LLY+20) &
                                              (WordsAndCoordinatesDF['uly']<EmptyPickUpAt_uly-20) &
                                              (WordsAndCoordinatesDF['urx']<GWT_LLX)]
        QuantityandType=" ".join(QuantityandType['Word'].values).strip()
        ###################### Weight ####################################
        GWTandWeight =WordsAndCoordinatesDF[(WordsAndCoordinatesDF['lly']>GWT_LLY+20) &
                                      (WordsAndCoordinatesDF['uly']<EmptyPickUpAt_uly-20) &
                                      (WordsAndCoordinatesDF['llx']>=GWT_LLX) &
                                    (WordsAndCoordinatesDF['urx']<=Limit_LLX)]
        GWTandWeight=" ".join(GWTandWeight['Word'].values).strip()
        desired_index=GWTandWeight.index('+')
        Weight=GWTandWeight[desired_index:]
        ####################### FullReturnTo #################################
        FullReturnTo=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['TO'])]
        FullReturnTo_uly=FullReturnTo['uly'].values[1]
        FullReturnTo_lly=FullReturnTo['lly'].values[1]
        FullReturnTo_urx=FullReturnTo['urx'].values[1]
        FullReturnTo=WordsAndCoordinatesDF[(WordsAndCoordinatesDF['uly']>FullReturnTo_uly-40) &
                                     (WordsAndCoordinatesDF['lly']<FullReturnTo_lly+40) &
                                     (WordsAndCoordinatesDF['llx']>FullReturnTo_urx)]
        FullReturnTo=" ".join(FullReturnTo['Word'].values).strip()[1:].strip()
        return dict(msg="Success",BookingNumber=BookingNumber,VESSELorVOYAGE=Vessel,Carrier=CARRIER,OnBehalfOf=OnBehalfOf,PlaceOfReceipt=PlaceOfReceipt,
                    PlaceOfLoading=PlaceOfLoading,ClosingTime=ClosingTime,CutOffDate=CutOffDate,LoadingEtaDate=LoadingEtaDate,
                    PortOfDischarging=PortOfDischarging,FinalDestination=FinalDestination,DestinationEtaDate=DestinationEtaDate,Customer=Customer,
                    Shipper=Shipper,ServiceMode=ServiceMode,PRE_CARRIAGE=PRE_CARRIAGE,Commodity=Commodity,QuantityandType=QuantityandType,
                    Weight=Weight,EmptyPickUpAt=EmptyPickUpAt,FullReturnTo=FullReturnTo)
    except Exception as e:
        print(e)
        return "unable to extract data from Google Vision API."
