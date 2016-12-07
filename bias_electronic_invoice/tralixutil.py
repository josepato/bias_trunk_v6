import httplib
from lxml import etree

def getTimbreTralix(obj):
    objroot = obj.getroot()
    NS = "http://schemas.xmlsoap.org/soap/envelope/"
    TREE = "{%s}" % NS
    NSMAP = {"soapenv": NS}
    soapobj = etree.Element(TREE + "Envelope", nsmap=NSMAP)
    header = etree.SubElement(soapobj, TREE + "Header")
    body = etree.SubElement(soapobj, TREE + "Body")
    body.append(objroot)
    sendstr = '<?xml version="1.0" encoding="UTF-8"?>\n' +  etree.tostring(soapobj, pretty_print=True, encoding="utf-8")
    hostname = "pruebastfd.tralix.com"
    portnum = 7070
    conn = httplib.HTTPSConnection(hostname, portnum)
    conn.connect()
    conn.putrequest('POST', '/')
    conn.putheader("Content-Type", "text/xml;charset=UTF-8")
    conn.putheader("SOAPAction", '"urn:TimbradoCFD"')
    conn.putheader("User-Agent", "Python httplib client")
    conn.putheader("Content-Length", str(len(sendstr)))
    conn.endheaders()
    conn.send(sendstr)
    respobj = etree.parse(conn.getresponse())
    envelope = respobj.getroot()
    body = envelope.getchildren()[0]
    if not "body" in body.tag.lower():
        raise Exception ("Error en cuerpo de respuesta.")
    child = body.getchildren()[0]
    if "fault" in child.tag.lower():
        detail = child.getchildren()[0]
        error = detail.getchildren()[0]
        codigo = error.attrib["codigo"]
        desc = error.getchildren()[0].text.encode("iso-8859-1")
        print "Error %s:\n %s" %(codigo, desc)
        raise Exception("Error %s: %s" %(codigo, desc))
    return respobj.getroot()


# #<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:cfdi="http://www.sat.gob.mx/cfd/3">

# cfdobj = etree.parse(open("/home/agalvan/duglas/tralix/cfd.xml"))
# cfdroot = cfdobj.getroot()

# respobj = etree.parse(TralixRequest(sendstr))
# print etree.tostring(respobj, pretty_print=True, encoding="utf-8")
