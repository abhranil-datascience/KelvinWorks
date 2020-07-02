import pandas as pd
############### Extract Data For Template Yong Ming #################
def ExtractDataForYongMingTemplate(WordsAndCoordinates):
    ################ Create Dataframe #######################
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
        Vertices=WordsAndCoordinates[i]['boundingPoly']['vertices']
        valid=True
        for coor in range(0,4):
            if len(list(Vertices[coor].keys()))!=2:
                valid=False
                break
        if valid:
            word_list.append(WordsAndCoordinates[i]['description'])
            llx_list.append(Vertices[0]['x'])
            lly_list.append(Vertices[0]['y'])
            lrx_list.append(Vertices[1]['x'])
            lry_list.append(Vertices[1]['y'])
            urx_list.append(Vertices[2]['x'])
            ury_list.append(Vertices[2]['y'])
            ulx_list.append(Vertices[3]['x'])
            uly_list.append(Vertices[3]['y'])
    ########## Create Dictionary for the lists ###########
    WordsAndCoordinatesDict={"Word":word_list,'llx':llx_list,'lly':lly_list,'lrx':lrx_list,'lry':lry_list,'urx':urx_list,'ury':ury_list,'ulx':ulx_list,'uly':uly_list}
    ####################### Create Dataframe ######################
    WordsAndCoordinatesDF = pd.DataFrame.from_dict(WordsAndCoordinatesDict)
    ##################### Get Date ############################
    uly_date=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Date:'])]['uly'].values[0]
    lly_Date=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Date:'])]['lly'].values[0]
    urx_Date=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Date:'])]['urx'].values[0]
    InvoiceDate=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>=uly_date-20) &
                                       (WordsAndCoordinatesDF['lly']<=lly_Date+20) &
                                       (WordsAndCoordinatesDF['ulx']>=urx_Date))]['Word'].values[0]
    InvoiceDate="".join(InvoiceDate)
    ################# Get Booking Reference ##################
    uly_Ref=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Ref:'])]['uly'].values[0]
    lly_Ref=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Ref:'])]['lly'].values[0]
    urx_Ref=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Ref:'])]['urx'].values[0]
    ulx_Symbol=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['+++('])]['ulx'].values[0]
    BookingRef=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_Ref-20) &
                                      (WordsAndCoordinatesDF['lly']<lly_Ref+20) &
                                      (WordsAndCoordinatesDF['ulx']>urx_Ref) &
                                      (WordsAndCoordinatesDF['urx']<ulx_Symbol-10))]['Word'].values[0]
    BookingRef="".join(BookingRef)
    #################### Get Nama Kapal #####################
    uly_Kapal=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Kapal:'])]['uly'].values[0]
    lly_Kapal=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Kapal:'])]['lly'].values[0]
    urx_Kapal=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Kapal:'])]['urx'].values[0]
    ulx_Flag=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Flag:'])]['ulx'].values[0]
    NamaKapal=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_Kapal-20) &
                                     (WordsAndCoordinatesDF['lly']<lly_Kapal+20) &
                                     (WordsAndCoordinatesDF['ulx']>urx_Kapal) &
                                     (WordsAndCoordinatesDF['urx']<ulx_Flag))]['Word'].values
    NamaKapal=" ".join(NamaKapal)
    #################### Get ETD #####################
    uly_ETD=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['ETD'])]['uly'].values[0]
    lly_ETD=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['ETD'])]['lly'].values[0]
    urx_ETD=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['ETD'])]['urx'].values[0]
    ulx_ETA=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['ETA'])]['ulx'].values[0]
    ETD=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_ETD-20) &
                               (WordsAndCoordinatesDF['lly']<lly_ETD+20) &
                               (WordsAndCoordinatesDF['ulx']>urx_ETD+40) &
                               (WordsAndCoordinatesDF['urx']<ulx_ETA))]['Word'].values
    ETD=" ".join(ETD)
    ################### Get ETA ###########################
    uly_DEST=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['DEST:'])]['uly'].values[0]
    lly_DEST=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['DEST:'])]['lly'].values[0]
    urx_DEST=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['DEST:'])]['urx'].values[0]
    ulx_SI=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['SI'])]['ulx'].values[0]
    DEST=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_DEST-20) &
                                (WordsAndCoordinatesDF['lly']<lly_DEST+20) &
                                (WordsAndCoordinatesDF['ulx']>urx_DEST) &
                                (WordsAndCoordinatesDF['urx']<ulx_SI))]['Word'].values
    ETA=" ".join(DEST)
    ################## Get SI ##############################
    uly_SI=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['SI'])]['uly'].values[0]
    lly_SI=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['SI'])]['lly'].values[0]
    urx_SI=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['SI'])]['urx'].values[0]
    SI=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_SI-20) &
                              (WordsAndCoordinatesDF['lly']<lly_SI+20) &
                              (WordsAndCoordinatesDF['ulx']>urx_SI+40))]['Word'].values
    SI=" ".join(SI)
    ################ Get Open Stack #########################
    uly_Open=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['STACK:'])]['uly'].values[0]
    lly_Open=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['STACK:'])]['lly'].values[0]
    urx_Open=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['STACK:'])]['urx'].values[0]
    ulx_Closing=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['EST.CLOSING'])]['llx'].values[0]
    Open=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_Open-20) &
                                (WordsAndCoordinatesDF['lly']<lly_Open+20) &
                                (WordsAndCoordinatesDF['ulx']>urx_Open) &
                                (WordsAndCoordinatesDF['urx']<ulx_Closing))]['Word'].values
    OpenTime=" ".join(Open)
    ############### Get Closing Time ########################
    uly_Close=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['TIME:'])]['uly'].values[0]
    lly_Close=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['TIME:'])]['lly'].values[0]
    urx_Close=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['TIME:'])]['urx'].values[0]
    Close=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_Close-20) &
                                 (WordsAndCoordinatesDF['lly']<lly_Close+20) &
                                 (WordsAndCoordinatesDF['ulx']>urx_Close))]['Word'].values
    CloseTime=" ".join(Close)
    ############### Get Cntrs ###############################
    uly_CNTRS=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['No.of'])]['uly'].values[0]
    lly_CNTRS=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['No.of'])]['lly'].values[0]
    urx_CNTRS=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['No.of'])]['urx'].values[0]
    ulx_commodity=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['COMMODITY:'])]['ulx'].values[0]
    CNTRS=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_CNTRS-20) &
                                 (WordsAndCoordinatesDF['lly']<lly_CNTRS+20) &
                                 (WordsAndCoordinatesDF['ulx']>urx_CNTRS) &
                                 (WordsAndCoordinatesDF['urx']<ulx_commodity))]['Word'].values
    CNTRS=" ".join(CNTRS)
    CNTRS=CNTRS.replace('CNTRS:',"")
    ################ Get Commodity ##########################
    uly_commodity=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['COMMODITY:'])]['uly'].values[0]
    lly_commodity=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['COMMODITY:'])]['lly'].values[0]
    urx_commodity=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['COMMODITY:'])]['urx'].values[0]
    Commodity=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_commodity-20) &
                                     (WordsAndCoordinatesDF['lly']<lly_commodity+20) &
                                     (WordsAndCoordinatesDF['ulx']>urx_commodity))]['Word'].values
    Commodity=" ".join(Commodity)
    ################ Get Remarks ############################
    uly_POL=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['POL:'])]['uly'].values[0]
    lly_commodity=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['COMMODITY:'])]['lly'].values[0]
    Remarks=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>lly_commodity+40) &
                                   (WordsAndCoordinatesDF['lly']<uly_POL-40))]['Word'].values
    Remarks=" ".join(Remarks)
    Remarks=Remarks.replace("Remarks:","")
    ################ Get POL ################################
    uly_POL=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['POL:'])]['uly'].values[0]
    lly_POL=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['POL:'])]['lly'].values[0]
    urx_POL=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['POL:'])]['urx'].values[0]
    ulx_transit=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Transit'])]['ulx'].min()
    Pol=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_POL-20) &
                               (WordsAndCoordinatesDF['lly']<lly_POL+20)&
                               (WordsAndCoordinatesDF['ulx']>urx_POL) &
                               (WordsAndCoordinatesDF['urx']<ulx_transit))]['Word'].values
    Pol=" ".join(Pol)
    ############## Get Transit Port #########################
    uly_Port=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Port:'])]['uly'].values[0]
    lly_Port=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Port:'])]['lly'].values[0]
    urx_Port=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Port:'])]['urx'].values[0]
    TransitPort=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_Port-20) &
                                       (WordsAndCoordinatesDF['lly']<lly_Port+20) &
                                       (WordsAndCoordinatesDF['ulx']>urx_Port))]['Word'].values
    TransitPort=" ".join(TransitPort)
    ################ Get POD ################################
    uly_POD=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['POD:'])]['uly'].values[0]
    lly_POD=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['POD:'])]['lly'].values[0]
    urx_POD=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['POD:'])]['urx'].values[0]
    ulx_transit=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Transit'])]['urx'].min()
    Pod=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_POD-20) &
                               (WordsAndCoordinatesDF['lly']<lly_POD+20) &
                               (WordsAndCoordinatesDF['ulx']>urx_POD) &
                               (WordsAndCoordinatesDF['urx']<ulx_transit))]['Word'].values
    Pod=" ".join(Pod)
    ############### Get TransitTerminal #####################
    uly_Terminal=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Terminal:'])]['uly'].values[0]
    lly_Terminal=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Terminal:'])]['lly'].values[0]
    urx_Terminal=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Terminal:'])]['urx'].values[0]
    TransitTerminal=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_Terminal-20) &
                                           (WordsAndCoordinatesDF['lly']<lly_Terminal+20) &
                                           (WordsAndCoordinatesDF['ulx']>urx_Terminal))]['Word'].values
    TransitTerminal=" ".join(TransitTerminal)
    ############## Get Final Destination #####################
    uly_DAPAT=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['DAPAT'])]['uly'].values[0]
    lly_Pod=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['POD:'])]['lly'].values[0]
    FinalDestination=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>lly_Pod+40) &
                                            (WordsAndCoordinatesDF['lly']<uly_DAPAT-40))]['Word'].values
    FinalDestination=" ".join(FinalDestination)
    FinalDestination=FinalDestination.replace("Final Dest:","").strip()
    ############## Get Address ##############################
    uly_DI=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['DI:'])]['uly'].values[0]
    lly_DI=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['DI:'])]['lly'].values[0]
    urx_DI=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['DI:'])]['urx'].values[0]
    llx_Approved=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Approved'])]['llx'].values[0]
    uly_Telp=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['TELP:'])]['uly'].values[0]
    AddressLine1=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_DI-20) &
                                        (WordsAndCoordinatesDF['lly']<lly_DI+20) &
                                        (WordsAndCoordinatesDF['ulx']>urx_DI))]['Word'].values
    AddressLine1=" ".join(AddressLine1)
    AddressLine2=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>lly_DI+20) &
                                        (WordsAndCoordinatesDF['lly']<uly_Telp-20) &
                                        (WordsAndCoordinatesDF['urx']<llx_Approved))]['Word'].values
    AddressLine2=" ".join(AddressLine2)
    Address=AddressLine1+" "+AddressLine2
    ################## Get Telephone ########################
    uly_Telp=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['TELP:'])]['uly'].values[0]
    lly_Telp=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['TELP:'])]['lly'].values[0]
    urx_Telp=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['TELP:'])]['urx'].values[0]
    llx_Approved=WordsAndCoordinatesDF[WordsAndCoordinatesDF['Word'].isin(['Approved'])]['llx'].values[0]
    Telephone=WordsAndCoordinatesDF[((WordsAndCoordinatesDF['uly']>uly_Telp-20) &
                                     (WordsAndCoordinatesDF['lly']<lly_Telp+20) &
                                     (WordsAndCoordinatesDF['ulx']>urx_Telp) &
                                     (WordsAndCoordinatesDF['lrx']<llx_Approved))]['Word'].values
    Telephone=" ".join(Telephone)
    ############ Create Dictionary and return ###############
    response_dict=dict(msg="Success",InvoiceDate=InvoiceDate,BookingReference=BookingRef,NamaKapal=NamaKapal,ETD=ETD,ETA_DEST=ETA,SI_No=SI,
                       EST_OPEN_STACK=OpenTime,EST_CLOSING_TIME=CloseTime,No_of_CNTRS=CNTRS,COMMODITY=Commodity,Remarks=Remarks,POL=Pol,
                       TransitPort=TransitPort,POD=Pod,TransitTerminal=TransitTerminal,FinalDestination=FinalDestination,
                       KONTAINER_DAPAT_DIAMBIL_DI=Address,TELP=Telephone)
    return response_dict
