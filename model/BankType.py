class BankType :
    Bank = [
          {'class':'Maybank','val':'MayBank'}
        , {'class':'HLB','val':'HLBBank'}
        , {'class':'CIMB', 'val': 'CIMBBank'}
        , {'class':'PBe', 'val': 'PublicBank'}
        , {'class':'Krungsri','val':'krungsri'}
        , {'class':'Kasikorn','val':'kasikornbank'}
        , {'class':'KTB', 'val': 'ktbnetbank'}
        , {'class':'AMBBank','val':'AMBBank'}
        , {'class':'RHBBank','val':'RHBBank'}
        , {'class':'Bangkok','val':'bangkokbank'}
        , {'class':'Scbeasy','val':'scbeasy'} #10
            ]
    class ToBank:
        MayBank={
            'MayBank':'Maybank',
            'HLBBank':'LEONG',
            'CIMBBank':'CIMB',
            'PublicBank':'PUBLIC',
            'RHBBank':'RHB',
        }
        HLBBank = {
            'MayBank':'MAYBANK',
            'HLBBank':'HLB',   #选3rd Party HLB Account转账页
            'CIMBBank':'CIMB',
            'PublicBank':'PUBLIC',
            'RHBBank': 'RHB',
        }
        CIMBBank = {
            'MayBank':'MAYBANK',
            'HLBBank':'HONG',
            'CIMBBank':'CIMB',  #选WITHIN CIMB BANK转账页
            'PublicBank':'PUBLIC',
            'RHBBank': 'RHB',
        }
        PublicBank = {
            'MayBank':'588734',#Maybank Berhad
            'HLBBank':'588830',#Hong Leong Bank Berhad
            'CIMBBank':'501855',#CIMB Bank Berhad
            'PublicBank':'PB',  #选PB Account转账页
            'RHBBank': '564160',  #RHB Bank Berhad
        }
        Krungsri = {
            'ktbnetbank':"3",
            'krungsri':"1",
            'uob':"17",
            'scbeasy':"13",
            'kasikornbank': "4",
            'bangkokbank': "2",
        }
        Kasikorn = {
            'ktbnetbank':"15",
            'krungsri':"16",
            'uob':"30",
            'scbeasy':"25",
            'kasikornbank': "1",
            'bangkokbank': "2",
        }
        ktbnetbank = {
            'ktbnetbank': "0",
            'krungsri': "25", #Bank Of Ayudhya
            'uob': "24", #United Overseas Bank (Thai) PCL.
            'scbeasy': "14", #Siam Commercial Bank
            'kasikornbank': "4", #Kasikorn Bank
            'bangkokbank': "2", #Bangkok Bank
        }
        bangkokbank = {
            'ktbnetbank': "KTB - Krung Thai Bank",
            'krungsri': "BAY - Bank of Ayudhaya",
            'uob': "UOBT - United Overseas Bank (Thai)",
            'scbeasy': "SCB - Siam Commercial Bank",
            'kasikornbank': "KBANK - Kasikornbank",
            'bangkokbank': "BBL - Bangkok Bank",
        }
        Scbeasy = {
            'ktbnetbank': "19",
            'krungsri': "2",
            'uob': "8",
            'scbeasy': "0",
            'kasikornbank': "1",
            'bangkokbank': "0",
        }
    class PaymentType:
        CIMBBank = {
            'funds': 0,
            'credit': 1,
            'Loans': 2,
        }
        PublicBank = {
            'funds': '00',
            'credit': '30',
            'Loans': '32',
        }