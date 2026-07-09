from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from datetime import date
import os
import json
from web3 import Web3, HTTPProvider
import ipfsApi
import os
from django.core.files.storage import FileSystemStorage
import pickle
from datetime import date
import pyaes, pbkdf2, binascii, os, secrets
import base64
import urllib, mimetypes
from django.http import HttpResponse

global details, username
details=''
global contract

api = ipfsApi.Client(host='http://127.0.0.1', port=5001)

def readDetails(contract_type):
    global details
    details = ""
    print(contract_type+"======================")
    blockchain_address = 'http://127.0.0.1:9545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Decentralized.json' #Decentralized contract code
    deployed_contract_address = '0xf918405b0cE63af233066b8dF76d9edfDa40422e' #hash address to access Decentralized contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'addclient':
        details = contract.functions.getClientData().call()
    if contract_type == 'transaction':
        details = contract.functions.getBlockTransaction().call()
    print(details)    

def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Decentralized.json' #Decentralized contract file
    deployed_contract_address = '0xf918405b0cE63af233066b8dF76d9edfDa40422e' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'addclient':
        details+=currentData
        msg = contract.functions.addClientData(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'transaction':
        details+=currentData
        msg = contract.functions.addBlockTransaction(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)    

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})    

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})
    
def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def Upload(request):
    if request.method == 'GET':
       return render(request, 'Upload.html', {})

def getKey(): #generating key with PBKDF2 for AES
    password = "s3cr3t*c0d3"
    passwordSalt = '76895'
    key = pbkdf2.PBKDF2(password, passwordSalt).read(32)
    return key

def encrypt(plaintext): #AES data encryption
    aes = pyaes.AESModeOfOperationCTR(getKey(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    ciphertext = aes.encrypt(plaintext)
    return ciphertext

def decrypt(enc): #AES data decryption
    aes = pyaes.AESModeOfOperationCTR(getKey(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    decrypted = aes.decrypt(enc)
    return decrypted

def calculateBlock(file_data):
    length = len(file_data)
    tot_blocks = 0
    size = 0
    if length >= 1000:
        size = length / 10
        tot_blocks = 10
    if length < 1000 and length > 500:
        size = length / 5
        tot_blocks = 5
    if length < 500 and length > 1:
        size = length / 3
        tot_blocks = 3
    return int(size), tot_blocks, length  

def UploadAction(request):
    if request.method == 'POST':
        global username
        today = date.today()   
        filedata = request.FILES['t1'].read()
        filename = request.FILES['t1'].name
        size, tot_blocks, length = calculateBlock(filedata)
        names = ""
        code = ""
        start = 0
        end = size
        block = []
        for i in range(0, tot_blocks):
            chunk = filedata[start:end]
            chunk = encrypt(chunk)
            block.append(chunk[0:20])
            start = end
            end = end + size
            chunk = pickle.dumps(chunk)
            hashcode = api.add_pyobj(chunk)
            names += filename+"_block_"+str(i)+" "
            code += hashcode+" "
        remain =  length - start
        if remain > 0:
            chunk = filedata[start:length]
            chunk = encrypt(chunk)
            block.append(chunk[0:20])
            start = start + remain
            chunk = pickle.dumps(chunk)
            hashcode = api.add_pyobj(chunk)
            names += filename+"_block_"+str(len(block))+" "
            code += hashcode+" "
        names = names.strip()
        code = code.strip()
        code_arr = code.split(" ")
        names_arr = names.split(" ")
        data = username+"#"+filename+"#"+str(today)+"#"+names+"#"+code+"\n"
        saveDataBlockChain(data,"transaction")
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Uploader Name</font></th>'
        output+='<th><font size=3 color=black>Filename</font></th>'
        output+='<th><font size=3 color=black>Uploading Date</font></th>'
        output+='<th><font size=3 color=black>Chunk Name</font></th>'
        output+='<th><font size=3 color=black>Encrypted Chunk Data</font></th>'
        output+='<th><font size=3 color=black>Chunk Hashcode</font></th></tr>'
        for i in range(len(block)):
            output+='<tr><td><font size=3 color=black>'+username+'</font></td>'
            output+='<td><font size=3 color=black>'+filename+'</font></td>'
            output+='<td><font size=3 color=black>'+str(today)+'</font></td>'
            output+='<td><font size=3 color=black>'+names_arr[i]+'</font></td>'
            output+='<td><font size=3 color=black>'+str(block[i])+'</font></td>'
            output+='<td><font size=3 color=black>'+code_arr[i]+'</font></td></tr>'
        context= {'data': output}
        return render(request, 'UserScreen.html', context)
        
def DownloadAction(request):
    if request.method == 'GET':
        global username
        filename = request.GET['file']
        readDetails("transaction")
        rows = details.split("\n")
        if os.path.exists("DecentralizedApp/static/"+filename):
            os.remove("DecentralizedApp/static/"+filename)
        with open("DecentralizedApp/static/"+filename, "wb+") as myfile:
            for i in range(len(rows)-1):
                arr = rows[i].split("#")
                if arr[0] == username and arr[1] == filename:
                    blocks = arr[4].split(" ")
                    for k in range(len(blocks)):
                        content = api.get_pyobj(blocks[k])
                        content = pickle.loads(content)
                        content = decrypt(content)
                        myfile.write(content)
                    break
        myfile.close()
        with open("DecentralizedApp/static/"+filename, "rb") as myfile:
            data = myfile.read()
        myfile.close()
        file_mimetype = mimetypes.guess_type(filename)
        response = HttpResponse(data,content_type=file_mimetype)
        #response['X-Sendfile'] = filename
        response['Content-Length'] = os.stat("DecentralizedApp/static/"+filename).st_size
        response['Content-Disposition'] = 'attachment; filename=%s/' % str(filename) 
        return response


def Download(request):
    if request.method == 'GET':
        global username
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Uploader Name</font></th>'
        output+='<th><font size=3 color=black>Filename</font></th>'
        output+='<th><font size=3 color=black>Uploading Date</font></th>'
        output+='<th><font size=3 color=black>Download File</font></th></tr>'
        readDetails("transaction")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == username:
                output+='<tr><td><font size=3 color=black>'+arr[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[2]+'</font></td>'
                output+='<td><a href=\'DownloadAction?file='+arr[1]+'\'><font size=3 color=black>Click Here</font></a></td></tr>'
        context= {'data': output}        
        return render(request, 'UserScreen.html', context)

def ViewBlocks(request):
    if request.method == 'GET':
        global username
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Uploader Name</font></th>'
        output+='<th><font size=3 color=black>Filename</font></th>'
        output+='<th><font size=3 color=black>Uploading Date</font></th>'
        output+='<th><font size=3 color=black>Block Names</font></th>'
        output+='<th><font size=3 color=black>Block Hash</font></th></tr>'
        readDetails("transaction")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == username:
                output+='<tr><td><font size=3 color=black>'+arr[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[3]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[4]+'</font></td></tr>'
        context= {'data': output}        
        return render(request, 'UserScreen.html', context)     

def Signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        contact = request.POST.get('contact', False)
        email = request.POST.get('email', False)
        address = request.POST.get('address', False)
        record = 'none'
        readDetails("addclient")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[1] == username:
                record = "exists"
                break
        if record == 'none':
            data = username+"#"+password+"#"+contact+"#"+email+"#"+address+"\n"
            saveDataBlockChain(data,"addclient")
            context= {'data':'Signup process completed and record saved in Blockchain'}
            return render(request, 'Register.html', context)
        else:
            context= {'data':username+'Username already exists'}
            return render(request, 'Register.html', context)
        
def UserLogin(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        status = 'none'
        readDetails("addclient")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == username and arr[1] == password:
                status = 'success'
                break
        if status == 'success':
            context= {'data':"Welcome "+username}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'Login.html', context)            


        
        



        
            
