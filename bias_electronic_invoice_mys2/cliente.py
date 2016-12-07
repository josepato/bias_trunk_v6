import os

requestor = "12211111-1111-1111-1111-111111111111"
transaction = "CONVERT_NATIVE_XML"
country = "MX"
entity = "AAA010101AAA"
user = "12211111-1111-1111-1111-111111111111"
username = "josepato"
data1 = "/home/agalvan/duglas/hacienda/mysuite/data1.txt"
data2 = "XML"
data3 = ""

fid = os.popen('java MySuiteClient --requestor="%s" --transaction="%s" --country="%s" --entity="%s" --user="%s" --username="%s" --data1="%s" --data2="%s" --data3="%s" 2>/dev/null' %(requestor, transaction, country, entity, user, username, data1, data2, data3))
resp = fid.readlines()
fid.close()

base64data = ""
for linea in resp:
    if linea.find("Data1: ") == 0:
        base64data = linea[7:]

if base64data:
    fid = os.popen('echo "%s" | base64 -d' %(base64data, ))
    print fid.read()
    fid.close()
    

