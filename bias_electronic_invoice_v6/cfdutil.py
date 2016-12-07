# -*- coding: utf-8 -*-


import os, time, string
from lxml import etree
from osv import fields, osv
import re

# raise osv.except_osv(('No Analytic Journal !'),("You must define an analytic journal of type '%s' !") % (tt,))

## Transforma un string representado como entero (entero en base 256) a string
def getBase256(nn):
    mystr = ""
    while nn >= 255:
        mystr = chr(nn % 256) + mystr
        nn /= 256
    mystr = chr(nn % 256) + mystr
    return mystr

def getNoSerie(certfname):
    cmd = "openssl x509 -inform DER -in %s -noout -serial" %(certfname, )
    fid = os.popen(cmd)
    data = fid.read()
    if data.find("serial=") == -1:
        raise osv.except_osv(('Error !'), ( "Error al extraer numero de serie"))
        return ""
    seriedata = data.split("=")[-1]
    serie = ""
    for i in range(len(seriedata) / 2):
        serie += chr(int(seriedata[i*2:(i+1)*2], 16))
    return serie

def getCertString(certfname):
    cmd = "openssl x509 -inform DER -in %s" %(certfname, )
    fid = os.popen(cmd)
    data = fid.readlines()
    return string.join(data[1:-1], "")[:-1] 
##    cmd = "openssl x509 -inform DER -in %s" %(certfname, )
##    fid = os.popen(cmd)
##    data = fid.read()
##    fid.close()
##    noheaderstring = ''.join(data.split('\n')[1:-2])
##    return noheaderstring

def getSello(cadena, privkeyfname, passphrase):
    randstr = os.popen("echo %s | md5sum | awk '{print $1}'" %(str(time.time()), )).read()[:-1]
    fname = "/tmp/" + randstr
    open(fname, "w").write(passphrase + "\n")
    cmd = "openssl pkcs8 -inform DER -in %s -passin file:%s" %(privkeyfname, fname, )
    privkey = os.popen(cmd).read()
    res = os.system("shred %s && rm %s" %(fname, fname))
    if res:
        raise osv.except_osv(('Error !'), ('Error al borrar archivo temporal.'))
        return ""
    open(fname, "w").write(privkey)
    cadena = re.sub('"','\\"', cadena)
    cmd = 'echo -n "%s" | openssl dgst -md5 -sign %s| base64 -w0' %(cadena, fname)
    fid = os.popen(cmd.encode("utf-8"))
    sello = fid.read()
    fid.close()
    res = os.system("shred %s && rm %s" %(fname, fname))
    if res:
         raise osv.except_osv(('Error !'), ( "Error al borrar archivo temporal"))
    return sello

def getSelloSHA1(cadena, privkeyfname, passphrase):
    randstr = os.popen("echo %s | md5sum | awk '{print $1}'" %(str(time.time()), )).read()[:-1]
    fname = "/tmp/" + randstr
    open(fname, "w").write(passphrase + "\n")
    cmd = "openssl pkcs8 -inform DER -in %s -passin file:%s" %(privkeyfname, fname, )
    privkey = os.popen(cmd).read()
    res = os.system("shred %s" %(fname, ))
    if res:
        print "Error al borrar archivo temporal"
        return ""
    open(fname, "w").write(privkey)
    cadena = re.sub('"','\\"', cadena)
    cmd = 'echo -n "%s" | openssl dgst -sha1 -sign %s| base64 -w0' %(cadena, fname)
    fid = os.popen(cmd.encode("utf-8"))
    sello = fid.read()
    fid.close()
    res = os.system("shred %s && rm %s" %(fname, fname))
    if res:
        print "Error al borrar archivo temporal"
    return sello

def verifySello(cadena, certfname, sello):
    timestr = os.popen("echo %s | md5sum | awk '{print $1}'" %(str(time.time()), )).read()[:-1]
    pemfname = "/tmp/pem" + timestr
    sellofname = "/tmp/sello" + timestr
    cmd = "openssl x509 -inform DER -in %s -noout -pubkey > %s" %(certfname, pemfname)
    res = os.system(cmd)
    if res:
        raise osv.except_osv(('Error !'), ( "Error al crear archivo temporal pem"))
        return False
    cmd = 'echo -n "%s" | base64 -d > %s' %(sello, sellofname)
    res = os.system(cmd)
    if res:
        raise osv.except_osv(('Error !'), ( "Error al crear archivo temporal sello"))
        return False
    cadena = re.sub('"','\\"', cadena)
    cmd = 'echo -n "%s" | openssl dgst -verify %s -signature %s' %(cadena, pemfname, sellofname)
    fid = os.popen(cmd.encode("utf-8"))
    data = fid.read()
    fid.close()
    res = os.system("rm %s %s" %(pemfname, sellofname))
    if res:
         raise osv.except_osv(('Error !'), ( "Error al borrar archivos temporales"))
    return "verified ok" in data.lower()


def verifySelloSHA1(cadena, certfname, sello):
    timestr = os.popen("echo %s | md5sum | awk '{print $1}'" %(str(time.time()), )).read()[:-1]
    pemfname = "/tmp/pem" + timestr
    sellofname = "/tmp/sello" + timestr
    cmd = "openssl x509 -inform DER -in %s -noout -pubkey > %s" %(certfname, pemfname)
    res = os.system(cmd)
    if res:
        print "Error al crear archivo temporal pem"
        return False
    cmd = 'echo -n "%s" | base64 -d > %s' %(sello, sellofname)
    res = os.system(cmd)
    if res:
        print "Error al crear archivo temporal sello"
        return False
    cadena = re.sub('"','\\"', cadena)
    cadena = re.sub('`','\\`', cadena)
    cmd = 'echo -n "%s" | openssl dgst -sha1 -verify %s -signature %s' %(cadena, pemfname, sellofname)
    fid = os.popen(cmd.encode("utf-8"))
    data = fid.read()
    fid.close()
    res = os.system("rm %s %s" %(pemfname, sellofname))
    if res:
        print "Error al borrar archivos temporales"
    return "verified ok" in data.lower()

class CadenaOriginal:
    def __init__(self):
        self.cadena = ""

    def getCadena(self):
        return "||" + self.cadena + "||"

    def agregaElem(self, obj, attrib):
        item = obj.get(attrib)
        if isinstance(item, basestring) and len(item):
            item = eliminate_double_space(item)
            if len(self.cadena):
                self.cadena += "|" + item
            else:
                self.cadena += item


def eliminate_double_space(data):
		data = re.sub('[ \t\n\r\f\v]', ' ',data)
		data = data.strip(' ')
		while '  ' in data:
			data = re.sub('  ', ' ', data)
		return data


class LineaReporte:
    def __init__(self):
        self.linea = ""

    def getLinea(self):
        return "|" + self.linea + "|"

    def agregaElemDirecto(self, attrib, item):
        if isinstance(item, basestring) and len(item):
            itemstr = item
        else:
            itemstr = ""
        if len(self.linea):
            self.linea += "|" + itemstr
        else:
            self.linea += itemstr


    def agregaElem(self, obj, attrib, cancelada=False):
        item = obj.get(attrib)
        if attrib == "fecha":
            (fecha, hora) = item.split("T")
            (yyyy, mm, dd) = fecha.split("-")
            item = dd + "/" + mm + "/" + yyyy + " " + hora
        elif attrib == "estado":
            if cancelada:
                item = "0"
            else:
                item = "1"
        elif attrib == "noAprobacion":
            item2 = obj.get("anoAprobacion")
            item = item2 + item
        elif attrib == "tipoDeComprobante":
            if item == "ingreso":
                item = "I"
            elif item == "egreso":
                item = "E"
            elif item == "traslado":
                item = "T"
        if isinstance(item, basestring) and len(item):
            itemstr = item
        else:
            itemstr = ""
        if len(self.linea):
            self.linea += "|" + itemstr
        else:
            self.linea += itemstr

def testItem(item, tag):
    if tag in item.tag:
        return True
    else:
        return False


def getCadenaTimbre(obj):
    cadenastr = "||" + obj.get("version")
    cadenastr += "|" + obj.get("UUID")
    cadenastr += "|" + obj.get("FechaTimbrado")
    cadenastr += "|" + obj.get("selloCFD")
    cadenastr += "|" + obj.get("noCertificadoSAT")
    cadenastr += "||"
    return cadenastr

def getCadenaOriginal(obj):
    cadena = CadenaOriginal()
    cfdroot = obj.getroot()
    for item in cfdroot.iterchildren():
        if testItem(item, "Emisor"):
            emisor = item
        elif testItem(item, "Receptor"):
            receptor = item
        elif testItem(item, "Conceptos"):
            conceptos = item
        elif testItem(item, "Impuestos"):
            impuestos = item
    cadena.agregaElem(cfdroot, "version")
    cadena.agregaElem(cfdroot, "serie")
    cadena.agregaElem(cfdroot, "folio")
    cadena.agregaElem(cfdroot, "fecha")
    cadena.agregaElem(cfdroot, "noAprobacion")
    cadena.agregaElem(cfdroot, "anoAprobacion")
    cadena.agregaElem(cfdroot, "tipoDeComprobante")
    cadena.agregaElem(cfdroot, "formaDePago")
    cadena.agregaElem(cfdroot, "condicionesDePago")
    cadena.agregaElem(cfdroot, "subTotal")
    cadena.agregaElem(cfdroot, "descuento")
    cadena.agregaElem(cfdroot, "total")
    cadena.agregaElem(emisor, "rfc")
    cadena.agregaElem(emisor, "nombre")
    domicilio = expedidoen = None
    for item in emisor.iterchildren():
        if testItem(item, "DomicilioFiscal"):
            domicilio = item
        elif testItem(item, "ExpedidoEn"):
            expedidoen = item
    cadena.agregaElem(domicilio, "calle")
    cadena.agregaElem(domicilio, "noExterior")
    cadena.agregaElem(domicilio, "noInterior")
    cadena.agregaElem(domicilio, "colonia")
    cadena.agregaElem(domicilio, "localidad")
    cadena.agregaElem(domicilio, "referencia")
    cadena.agregaElem(domicilio, "municipio")
    cadena.agregaElem(domicilio, "estado")
    cadena.agregaElem(domicilio, "pais")
    cadena.agregaElem(domicilio, "codigoPostal")
    if expedidoen:
        cadena.agregaElem(expedidoen, "calle")
        cadena.agregaElem(expedidoen, "noExterior")
        cadena.agregaElem(expedidoen, "noInterior")
        cadena.agregaElem(expedidoen, "colonia")
        cadena.agregaElem(expedidoen, "localidad")
        cadena.agregaElem(expedidoen, "referencia")
        cadena.agregaElem(expedidoen, "municipio")
        cadena.agregaElem(expedidoen, "estado")
        cadena.agregaElem(expedidoen, "pais")
        cadena.agregaElem(expedidoen, "codigoPostal")
    cadena.agregaElem(receptor, "rfc")
    cadena.agregaElem(receptor, "nombre")
    domicilio = None
    for item in receptor.iterchildren():
        if testItem(item, "Domicilio"):
            domicilio = item
    cadena.agregaElem(domicilio, "calle")
    cadena.agregaElem(domicilio, "noExterior")
    cadena.agregaElem(domicilio, "noInterior")
    cadena.agregaElem(domicilio, "colonia")
    cadena.agregaElem(domicilio, "localidad")
    cadena.agregaElem(domicilio, "referencia")
    cadena.agregaElem(domicilio, "municipio")
    cadena.agregaElem(domicilio, "estado")
    cadena.agregaElem(domicilio, "pais")
    cadena.agregaElem(domicilio, "codigoPostal")
    for item in conceptos.iterchildren():
        cadena.agregaElem(item, "cantidad")
        cadena.agregaElem(item, "unidad")
        cadena.agregaElem(item, "noIdentificacion")
        cadena.agregaElem(item, "descripcion")
        cadena.agregaElem(item, "valorUnitario")
        cadena.agregaElem(item, "importe")
    retenciones = traslados = None
    for item in impuestos.iterchildren():
        if testItem(item, "Retenciones"):
            retenciones = item
        elif testItem(item, "Traslados"):
            traslados = item
    if retenciones != None:
       for item in retenciones.iterchildren():
           cadena.agregaElem(item, "impuesto")
           cadena.agregaElem(item, "importe")
       cadena.agregaElem(impuestos, "totalImpuestosRetenidos")
    if traslados != None:
        for item in traslados.iterchildren():
            cadena.agregaElem(item, "impuesto")
            cadena.agregaElem(item, "tasa")
            cadena.agregaElem(item, "importe")
        cadena.agregaElem(impuestos, "totalImpuestosTrasladados")
    return cadena.getCadena()


def getLineaReporte(obj, cancelada=False, subtotalstr=None, taxstr=None):
    linea = LineaReporte()
    cfdroot = obj.getroot()
    for item in cfdroot.iterchildren():
        if testItem(item, "Emisor"):
            emisor = item
        elif testItem(item, "Receptor"):
            receptor = item
        elif testItem(item, "Conceptos"):
            conceptos = item
        elif testItem(item, "Impuestos"):
            impuestos = item
    linea.agregaElem(receptor, "rfc")
    linea.agregaElem(cfdroot, "serie")
    linea.agregaElem(cfdroot, "folio")
    linea.agregaElem(cfdroot, "noAprobacion")
    linea.agregaElem(cfdroot, "fecha")
    if subtotalstr:
        linea.agregaElemDirecto("subTotal", subtotalstr)
    else:
        raise osv.except_osv("Warning !",  "No se extrajo subTotal de pólizas.")
    if taxstr:
        linea.agregaElemDirecto("totalImpuestosTrasladados", taxstr)
    else:
        raise osv.except_osv(("Warning !", ),  ("No se extrajo subTotal de pólizas.", ))
    linea.agregaElem(cfdroot, "estado", cancelada)
    linea.agregaElem(cfdroot, "tipoDeComprobante")
    #######  Revisar  (esta informacion no esta en cfdroot  ##########
    linea.agregaElem(cfdroot, "pedimento")
    linea.agregaElem(cfdroot, "fechaPedimento")
    linea.agregaElem(cfdroot, "aduana")
    return linea.getLinea()

def getLineaFacturaCancelada(obj):
    linea = getLineaReporte(obj, True)
    return linea


def validaXML(xmlstring, schemafname):
    fid = open(schemafname)
    schema = etree.XMLSchema(file = fid)
    fid.close()
    parser = objectify.makeparser(schema=schema)
    try:
        xx = objectify.fromstring(xmlstring, parser)
    except etree.XMLSyntaxError, msg:
        print msg
        return False
    return True


def createBarCodeImg(rfcemisor, rfcreceptor, total, uuid, outfname, dotsize=3):
    cmd = 'echo -n "?re={0}&rr={1}&tt={2:0=17.6f}&id={3}" | qrencode -o {4} -s {5}'.format(rfcemisor, rfcreceptor, total, uuid, outfname, dotsize)
    res = os.system(cmd)
    if res:
        raise osv.except_osv(("Error !", ),  ("Error al crear código de barras 2D", ))

