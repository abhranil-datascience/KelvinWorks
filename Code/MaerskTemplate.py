from pdf2image import convert_from_path
import cv2,io
from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToDict
import pandas as pd

def ProcessMaerskInvoice(ImageList):
    keywordlist=['no.:','maersk','from:','to:','description:','quantity','itinerary',"size",'sub.','collapsible','gross','equip','pack.','weight','volume','qty/kind','type','release','vessel','voy','etd','eta']
    ############ Preprocess Image ###########

    for image in ImageList:
        currentImage=cv2.imread(image)
        currentImage[currentImage<10]=0
        currentImage[(currentImage!=0) & (currentImage!=255)]=255
        cv2.imwrite(image,currentImage)
    ################ Invoke Vision API for 2nd page ############################
    try:
        for count,image in enumerate(ImageList):
            if count < 2:
                currentfile=ImageList[count]
                with io.open(currentfile, 'rb') as gen_image_file:
                    content = gen_image_file.read()
                client = vision.ImageAnnotatorClient()
                image = vision.types.Image(content=content)
                response = client.text_detection(image=image)
                DictResponse=MessageToDict(response)
                if count == 0:
                    FirstPageDictResponse=DictResponse
                else:
                    SecondPageDictResponse=DictResponse
    except:
        return "invocation error"
    ############# Create Message To Dict For 2nd Page ###############
    SecondPageDictResponse=MessageToDict(response)
    ############# Check for Keywords ##################
    WholeContentDescription=FirstPageDictResponse['textAnnotations'][0]['description'].lower()+" "+SecondPageDictResponse['textAnnotations'][0]['description'].lower()
    match=0
    for keyword in keywordlist:
        if keyword in WholeContentDescription:
            match = match + 1
        else:
            print(keyword)
    if match != len(keywordlist):
        return "missing keywords"
    ############# create Dataframes #########################
    WordsAndCoordinatesPage1=FirstPageDictResponse['textAnnotations'][1:]
    WordsAndCoordinatesPage2=SecondPageDictResponse['textAnnotations'][1:]
    WordsAndCoordinates=[WordsAndCoordinatesPage1,WordsAndCoordinatesPage2]
    for num in range(0,len(WordsAndCoordinates)):
        currentWordandCoordinate=WordsAndCoordinates[num]
        word_list=[]
        llx_list=[]
        lly_list=[]
        lrx_list=[]
        lry_list=[]
        urx_list=[]
        ury_list=[]
        ulx_list=[]
        uly_list=[]
        for i in range(0,len(currentWordandCoordinate)):
            word_list.append(currentWordandCoordinate[i]['description'])
            llx_list.append(currentWordandCoordinate[i]['boundingPoly']['vertices'][0]['x'])
            lly_list.append(currentWordandCoordinate[i]['boundingPoly']['vertices'][0]['y'])
            lrx_list.append(currentWordandCoordinate[i]['boundingPoly']['vertices'][1]['x'])
            lry_list.append(currentWordandCoordinate[i]['boundingPoly']['vertices'][1]['y'])
            urx_list.append(currentWordandCoordinate[i]['boundingPoly']['vertices'][2]['x'])
            ury_list.append(currentWordandCoordinate[i]['boundingPoly']['vertices'][2]['y'])
            ulx_list.append(currentWordandCoordinate[i]['boundingPoly']['vertices'][3]['x'])
            uly_list.append(currentWordandCoordinate[i]['boundingPoly']['vertices'][3]['y'])
        ##################### Create Dictionary for the lists #####################
        WordsAndCoordinatesDict={"Word":word_list,'llx':llx_list,'lly':lly_list,'lrx':lrx_list,'lry':lry_list,'urx':urx_list,'ury':ury_list,'ulx':ulx_list,'uly':uly_list}
        ####################### Create Dataframe ######################
        if num==0:
            WordsAndCoordinatesDF_Page1 = pd.DataFrame.from_dict(WordsAndCoordinatesDict)
        elif num==1:
            WordsAndCoordinatesDF_Page2 = pd.DataFrame.from_dict(WordsAndCoordinatesDict)
    ###################### Get Values ###########################
    try:
        ############## Booking Number ############################
        BookingNumber_uly=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['No.:'])]['uly'].values[0]-20
        BookingNumber_lly=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['No.:'])]['lly'].values[0]+20
        BookingNumber_urx=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['No.:'])]['urx'].values[0]
        MeraskSpot_llx=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Maersk'])].sort_values(by='lly').head(1)['llx'].values[0]
        BookingNumber=WordsAndCoordinatesDF_Page1[(WordsAndCoordinatesDF_Page1['uly'] > BookingNumber_uly) &
                                                  (WordsAndCoordinatesDF_Page1['lly'] < BookingNumber_lly) &
                                                  (WordsAndCoordinatesDF_Page1['ulx'] > BookingNumber_urx) &
                                                  (WordsAndCoordinatesDF_Page1['urx'] < MeraskSpot_llx)]
        BookingNumber=" ".join(BookingNumber['Word'].values).strip()
        print(BookingNumber)
        ############## From #############################
        From_uly=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['From:'])]['uly'].values[0]-30
        From_lly=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['From:'])]['lly'].values[0]+30
        From_urx=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['From:'])]['urx'].values[0]
        From=WordsAndCoordinatesDF_Page1[(WordsAndCoordinatesDF_Page1['uly']>From_uly) &
                                         (WordsAndCoordinatesDF_Page1['lly']<From_lly) &
                                         (WordsAndCoordinatesDF_Page1['ulx']>From_urx)]
        From=" ".join(From['Word'].values).strip()
        print(From)
        ################# To #############################
        To_uly=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['To:'])]['uly'].values[0]-20
        To_lly=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['To:'])]['lly'].values[0]+20
        To_urx=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['To:'])]['urx'].values[0]
        To=WordsAndCoordinatesDF_Page1[(WordsAndCoordinatesDF_Page1['uly']>To_uly) &
                                       (WordsAndCoordinatesDF_Page1['lly']<To_lly) &
                                       (WordsAndCoordinatesDF_Page1['ulx']>To_urx)]
        To=" ".join(To['Word'].values).strip()
        print(To)
        ############# Commodity Description ###################
        Description_uly=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Description:'])]['uly'].values[0]-20
        Description_lly=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Description:'])]['lly'].values[0]+20
        Description_urx=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Description:'])]['urx'].values[0]
        Commodity=WordsAndCoordinatesDF_Page1[(WordsAndCoordinatesDF_Page1['uly']>Description_uly) &
                                              (WordsAndCoordinatesDF_Page1['lly']<Description_lly) &
                                              (WordsAndCoordinatesDF_Page1['ulx']>Description_urx)]
        CommodityDescription=" ".join(Commodity['Word'].values).strip()
        ################ Quantity #########################
        Quantity_LLY=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Quantity'])]['lly'].values[0]+20
        Itinerary_ULY=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Itinerary'])]['uly'].values[0]-20
        Size_LLX=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Size/Type/Height'])]['llx'].values[0]
        Quantity=WordsAndCoordinatesDF_Page1[(WordsAndCoordinatesDF_Page1['lly']>Quantity_LLY) &
                                             (WordsAndCoordinatesDF_Page1['uly']<Itinerary_ULY) &
                                             (WordsAndCoordinatesDF_Page1['lrx']<Size_LLX)]
        Quantity=" ".join(Quantity['Word'].values).strip()
        print(Quantity)
        ################ Size ##############################
        Quantity_LLY=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Quantity'])]['lly'].values[0]+20
        Itinerary_ULY=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Itinerary'])]['uly'].values[0]-20
        Quatity_LRX=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Quantity'])]['lrx'].values[0]
        Sub_LLX=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Sub.'])]['llx'].values[0]
        Size=WordsAndCoordinatesDF_Page1[(WordsAndCoordinatesDF_Page1['lly']>Quantity_LLY) &
                                         (WordsAndCoordinatesDF_Page1['uly']<Itinerary_ULY) &
                                         (WordsAndCoordinatesDF_Page1['llx']>Quatity_LRX) &
                                         (WordsAndCoordinatesDF_Page1['lrx']<Sub_LLX)].sort_values(by=['llx'])
        Size=" ".join(Size['Word'].values).strip()
        print(Size)
        ################ Sub Equipment #####################
        Quantity_LLY=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Quantity'])]['lly'].values[0]+20
        Itinerary_ULY=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Itinerary'])]['uly'].values[0]-20
        Collapsible_LRX=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Collapsible'])]['lrx'].values[0]
        Gross_LLX=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Gross'])]['llx'].values[0]
        SubEquipment=WordsAndCoordinatesDF_Page1[(WordsAndCoordinatesDF_Page1['lly']>Quantity_LLY) &
                                                 (WordsAndCoordinatesDF_Page1['uly']<Itinerary_ULY) &
                                                 (WordsAndCoordinatesDF_Page1['llx']>Collapsible_LRX) &
                                                 (WordsAndCoordinatesDF_Page1['lrx']<Gross_LLX)]
        SubEquipment=" ".join(SubEquipment['Word'].values).strip()
        ############### Gross Weight #####################
        Quantity_LLY=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Quantity'])]['lly'].values[0]+20
        Itinerary_ULY=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Itinerary'])]['uly'].values[0]-20
        Equip_LRX=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Equip'])]['lrx'].values[0]
        Pack_LLX=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Pack.'])]['llx'].values[0]
        GrossWeight=WordsAndCoordinatesDF_Page1[(WordsAndCoordinatesDF_Page1['lly']>Quantity_LLY) &
                                                (WordsAndCoordinatesDF_Page1['uly']<Itinerary_ULY) &
                                                (WordsAndCoordinatesDF_Page1['llx']>Equip_LRX) &
                                                (WordsAndCoordinatesDF_Page1['lrx']<Pack_LLX)]
        GrossWeight=" ".join(GrossWeight['Word'].values).strip()
        ############### Pack Quantity ######################
        Quantity_LLY=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Quantity'])]['lly'].values[0]+20
        Itinerary_ULY=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Itinerary'])]['uly'].values[0]-20
        Weight_LRX=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Weight'])]['lrx'].values[0]+40
        Cargo_LLX=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Volume'])]['llx'].values[0]
        PackQuantity=WordsAndCoordinatesDF_Page1[(WordsAndCoordinatesDF_Page1['lly']>Quantity_LLY) &
                                                 (WordsAndCoordinatesDF_Page1['uly']<Itinerary_ULY) &
                                                 (WordsAndCoordinatesDF_Page1['llx']>Weight_LRX) &
                                                 (WordsAndCoordinatesDF_Page1['lrx']<Cargo_LLX)]
        PackQuantity=" ".join(PackQuantity['Word'].values).strip()
        ############## Cargo Volume ##########################
        Quantity_LLY=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Quantity'])]['lly'].values[0]+20
        Itinerary_ULY=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Itinerary'])]['uly'].values[0]-20
        Weight_LRX=WordsAndCoordinatesDF_Page1[WordsAndCoordinatesDF_Page1['Word'].isin(['Qty/Kind'])]['lrx'].values[0]+20
        CargoVolume=WordsAndCoordinatesDF_Page1[(WordsAndCoordinatesDF_Page1['lly']>Quantity_LLY) &
                                                (WordsAndCoordinatesDF_Page1['uly']<Itinerary_ULY) &
                                                (WordsAndCoordinatesDF_Page1['llx']>Weight_LRX)]
        CargoVolume=" ".join(CargoVolume['Word'].values).strip()
        ######## Load Itinerary Type and Location ###############
        Type_lly=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['Туре'])]['lly'].values[0]
        MaxLowerLimit = Type_lly+160
        Type_urx=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['Туре'])]['urx'].values[0]
        MaxURX=Type_urx+160
        LoadItineraryType=WordsAndCoordinatesDF_Page2[(WordsAndCoordinatesDF_Page2['lly']>Type_lly) &
                                                      (WordsAndCoordinatesDF_Page2['lly']<MaxLowerLimit) &
                                                      (WordsAndCoordinatesDF_Page2['lrx']<MaxURX)]
        LoadItineraryType=" ".join(LoadItineraryType['Word'].values)
        Location_lly=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['Location'])]['lly'].values[0]
        MaxLowerLimit = Location_lly+160
        Type_urx=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['Туре'])]['urx'].values[0]
        MaxURX=Type_urx+160
        Release_llx=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['Release'])]['ulx'].values[0]
        LoadItineraryLocation=WordsAndCoordinatesDF_Page2[(WordsAndCoordinatesDF_Page2['lly']>Location_lly) &
                                                          (WordsAndCoordinatesDF_Page2['lly']<MaxLowerLimit) &
                                                          (WordsAndCoordinatesDF_Page2['lrx']<Release_llx) &
                                                          (WordsAndCoordinatesDF_Page2['llx']>MaxURX)]
        LoadItineraryLocation=" ".join(LoadItineraryLocation['Word'].values)
        ############### TransportPlanVessel ##########################
        Vessel_lly=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['Vessel'])]['lly'].values[0]+20
        max_lly=Vessel_lly+80
        Vessel_llx=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['Vessel'])]['llx'].values[0]
        Voy_llx=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['Voy'])]['llx'].values[0]
        TransportPlanVessel=WordsAndCoordinatesDF_Page2[(WordsAndCoordinatesDF_Page2['lly']>Vessel_lly) &
                                                        (WordsAndCoordinatesDF_Page2['lly']<max_lly) &
                                                        (WordsAndCoordinatesDF_Page2['llx']>=Vessel_llx) &
                                                        (WordsAndCoordinatesDF_Page2['lrx']<Voy_llx)]
        TransportPlanVessel=" ".join(TransportPlanVessel['Word'].values)
        ############ TransportVoyNumber #############################
        Voy_lly=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['Voy'])]['lly'].values[0]+20
        max_lly=Voy_lly+80
        Voy_llx=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['Voy'])]['llx'].values[0]
        ETD_llx=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['ETD'])]['llx'].values[0]
        TransportVoyNumber=WordsAndCoordinatesDF_Page2[(WordsAndCoordinatesDF_Page2['lly']>Voy_lly) &
                                                       (WordsAndCoordinatesDF_Page2['lly']<max_lly) &
                                                       (WordsAndCoordinatesDF_Page2['llx']>=Voy_llx) &
                                                       (WordsAndCoordinatesDF_Page2['lrx']<ETD_llx)]
        TransportVoyNumber=" ".join(TransportVoyNumber['Word'].values)
        ############## TransportPlanETD ###############################
        ETD_lly=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['ETD'])]['lly'].values[0]
        max_lly=Voy_lly+80
        ETD_llx=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['ETD'])]['llx'].values[0]-20
        ETA_llx=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['ЕТА'])]['llx'].values[0]
        TransportPlanETD=WordsAndCoordinatesDF_Page2[(WordsAndCoordinatesDF_Page2['lly']>ETD_lly) &
                                                     (WordsAndCoordinatesDF_Page2['lly']<max_lly) &
                                                     (WordsAndCoordinatesDF_Page2['llx']>=ETD_llx) &
                                                     (WordsAndCoordinatesDF_Page2['lrx']<ETA_llx)]
        TransportPlanETD=" ".join(TransportPlanETD['Word'].values)
        ################## TransportPlanETA #############################
        ETA_lly=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['ЕТА'])]['lly'].values[0]
        max_lly=ETA_lly+80
        ETA_llx=WordsAndCoordinatesDF_Page2[WordsAndCoordinatesDF_Page2['Word'].isin(['ЕТА'])]['llx'].values[0]-20
        TransportPlanETA=WordsAndCoordinatesDF_Page2[(WordsAndCoordinatesDF_Page2['lly']>ETA_lly) &
                                                     (WordsAndCoordinatesDF_Page2['lly']<max_lly) &
                                                     (WordsAndCoordinatesDF_Page2['llx']>=ETA_llx)]
        TransportPlanETA=" ".join(TransportPlanETA['Word'].values)
        print(TransportPlanETA)
        return dict(msg="Success",BookingNumber=BookingNumber,From=From,To=To,CommodityDescription=CommodityDescription,Quantity=Quantity,Size=Size,
                    SubEquipment=SubEquipment,GrossWeight=GrossWeight,PackQuantity=PackQuantity,CargoVolume=CargoVolume,LoadItineraryType=LoadItineraryType,
                    LoadItineraryLocation=LoadItineraryLocation,TransportPlanVessel=TransportPlanVessel,TransportVoyNumber=TransportVoyNumber,
                    TransportPlanETD=TransportPlanETD,TransportPlanETA=TransportPlanETA)
    except:
        return "unable to extract data from Google Vision API."
