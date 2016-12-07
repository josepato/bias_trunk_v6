## coding: utf-8


import time
from mx.DateTime import *
import re
import StringIO
from lxml import etree
import base64
from lxml.builder import ElementMaker
import codecs


cfe_str = '''<?xml version="1.0" encoding="UTF-8"?>
<Comprobante xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sat.gob.mx/cfd/2 http://www.sat.gob.mx/sitio_internet/cfd/2/cfdv2.xsd http://www.sat.gob.mx/ecc http://www.sat.gob.mx/sitio_internet/cfd/ecc/ecc.xsd" xmlns="http://www.sat.gob.mx/cfd/2" version="2.0" folio="1" fecha="2010-10-29T20:11:52" anoAprobacion="2010" formaDePago="Pago en una sola exhibicion" noAprobacion="174764" condicionesDePago="30 Days End of Month" noCertificado="00001000000102052521" certificado="MIIECzCCAvOgAwIBAgIUMDAwMDEwMDAwMDAxMDIwNTI1MjEwDQYJKoZIhvcNAQEF&#10;BQAwggE2MTgwNgYDVQQDDC9BLkMuIGRlbCBTZXJ2aWNpbyBkZSBBZG1pbmlzdHJh&#10;Y2nDs24gVHJpYnV0YXJpYTEvMC0GA1UECgwmU2VydmljaW8gZGUgQWRtaW5pc3Ry&#10;YWNpw7NuIFRyaWJ1dGFyaWExHzAdBgkqhkiG9w0BCQEWEGFjb2RzQHNhdC5nb2Iu&#10;bXgxJjAkBgNVBAkMHUF2LiBIaWRhbGdvIDc3LCBDb2wuIEd1ZXJyZXJvMQ4wDAYD&#10;VQQRDAUwNjMwMDELMAkGA1UEBhMCTVgxGTAXBgNVBAgMEERpc3RyaXRvIEZlZGVy&#10;YWwxEzARBgNVBAcMCkN1YXVodGVtb2MxMzAxBgkqhkiG9w0BCQIMJFJlc3BvbnNh&#10;YmxlOiBGZXJuYW5kbyBNYXJ0w61uZXogQ29zczAeFw0xMDEwMDUxNzQyMTBaFw0x&#10;MjEwMDQxNzQyMTBaMIGrMSAwHgYDVQQDExdBUlRVUk8gR0FMVkFOIFJPRFJJR1VF&#10;WjEgMB4GA1UEKRMXQVJUVVJPIEdBTFZBTiBST0RSSUdVRVoxIDAeBgNVBAoTF0FS&#10;VFVSTyBHQUxWQU4gUk9EUklHVUVaMRYwFAYDVQQtEw1HQVJBNjgwNjEwU0M2MRsw&#10;GQYDVQQFExJHQVJBNjgwNjEwSENMTERSMDMxDjAMBgNVBAsTBVVuaWNhMIGfMA0G&#10;CSqGSIb3DQEBAQUAA4GNADCBiQKBgQDcMzQ2ydNqJkVEo8D7qyIysKwhg4agyJ9q&#10;gdxa037B/XFxqCajPEaQny6WoZax7CTZgtzSRtLJv+S8ZfM2EZi0u8M+0Ldlo7Ej&#10;2JJgzI2C3lMpShRyhq4MQBWMNpvjDvHWMl7FMQWd4p2fRqEq5/0OdDgmcG2Y8v/b&#10;wGBngEf01QIDAQABox0wGzAMBgNVHRMBAf8EAjAAMAsGA1UdDwQEAwIGwDANBgkq&#10;hkiG9w0BAQUFAAOCAQEADOmZlowYyLpoQCuzirgnvSUhQDTPbCVyFggdnAJ6ioSa&#10;ZuohJemdIhkJv9wo/HmM+kzwxnZdL2NJJQC18P05o5bcvRvki4YkF/REX1XPOPl3&#10;nLKXUdKqgFBVCRqBfx2yHEXfUDKH0r3up7JstwuBa2ogeevzyzxNyI2GUU15bLGb&#10;UYmuCyjz/Ep4a29bmZsCAPUC728WOn6RjVrMfhEuLiEKVdyQpWbHveiDsmrXkggn&#10;iG9TlnwZHfK5+OBH1Qxr1ZJ1idWLJEYXIgZnDiP/e+e/P+PRbgs71mT5+c7UJU+W&#10;Tjku3tCbb+ZcdHKOmtdWxcIhJ/DGnWz32CvuGu2s+w==" subTotal="4640.0" total="4610.13" tipoDeComprobante="ingreso" sello="snKZMKGfp7fv6wxUmDOcN6PKP3rT5VbHhaisKpyQcPyYakG8Fb0jj5j/UQN5I4hRwg3EuRpyp0IM5C/fggUX8dLkfgkNy3arLPYsO+tA7o0Ddvvc0FColid5BMTDtwELpFYzbPd1wFoAutKhUquSA9qmPbCl3VkcCJpCUYnvYFM=">
  <Emisor rfc="GARA680610SC6" nombre="Arturo Galvan Rodriguez">
    <DomicilioFiscal calle="Valle de Moscatel No.124-1" colonia="Valle del Contry" municipio="Guadalupe" estado="Nuevo León" pais="Mexico" codigoPostal="67174"/>
  </Emisor>
  <Receptor rfc="BUC000703MN3" nombre="Balance Urbano Control de Plagas S.A. de C.V.">
    <Domicilio calle="Acueducto 631-C" colonia="Fracc. El Lechugal" municipio="Santa Catarina" estado="Nuevo León" pais="Mexico" codigoPostal="66376"/>
  </Receptor>
  <Conceptos>
    <Concepto cantidad="1.0" descripcion="Servidor Virtuales 512 MB" valorUnitario="640.0" importe="640.0" unidad="PCE"/>
    <Concepto cantidad="8.0" descripcion="Horas de Servicio" valorUnitario="500.0" importe="4000.0" unidad="PCE"/>
  </Conceptos>
  <Impuestos totalImpuestosRetenidos="132.27" totalImpuestosTrasladados="102.4">
    <Retenciones>
      <Retencion impuesto="ISR" importe="64.0"/>
      <Retencion impuesto="IVA" importe="68.27"/>
    </Retenciones>
    <Traslados>
      <Traslado impuesto="IVA" importe="102.4" tasa="16"/>
    </Traslados>
  </Impuestos>
</Comprobante>'''


def agregaTag(obj, tag, text, factory):
    mytag = eval("factory.%s()" %(tag, ))
    if text:
        mytag.text = text
    obj.append(mytag)
    return mytag


def testItem(item, tag):
    if tag in item.tag:
        return True
    else:
        return False


class MySuiteXML:
    def __init__(self):
        self.factory = ElementMaker(namespace="http://www.fact.com.mx/schema/fx", 
                              nsmap={'fx' : "http://www.fact.com.mx/schema/fx",
                                     'xsi':"http://www.w3.org/2001/XMLSchema-instance",
                                     "schemaLocation": "http://www.fact.com.mx/schema/fx  http://www.mysuitemex.com/fact/schema/fx_2010_c.xsd"})
        self.root = self.factory.FactDocMX()
        tmp = agregaTag(self.root, "Version", "4", self.factory)

    def agregaElem(self, tag, text=""):
        return agregaTag(self.root, tag, text, self.factory)

    def agregaSubElem(self, obj, tag, text=""):
        return agregaTag(obj, tag, text, self.factory)

    def show(self):
        print etree.tostring(self.root, pretty_print=True)


MySuiteDict = {"ingreso": "FACTURA"}

def create_mysuite_xml(cfe_str, my_suite_dir, *args):
    mysuite = MySuiteXML()
    cfe = etree.parse(StringIO.StringIO(cfe_str))
    cfdroot = cfe.getroot()
    for item in cfdroot.iterchildren():
        if testItem(item, "Emisor"):
            emisor = item
        elif testItem(item, "Receptor"):
            receptor = item
        elif testItem(item, "Conceptos"):
            conceptos = item
        elif testItem(item, "Impuestos"):
            impuestos = item
    idtag = mysuite.agregaElem("Identificacion")
    xx = mysuite.agregaSubElem(idtag, "CdgPaisEmisor", my_suite_dir['CdgPaisEmisor'])
    xx = mysuite.agregaSubElem(idtag, "TipoDeComprobante", MySuiteDict[cfdroot.get("tipoDeComprobante")])
    xx = mysuite.agregaSubElem(idtag, "RFCEmisor", emisor.get("rfc"))
    xx = mysuite.agregaSubElem(idtag, "RazonSocialEmisor", emisor.get("nombre"))
    xx = mysuite.agregaSubElem(idtag, "Usuario", my_suite_dir['Usuario'])
    ####Emisor
    idtag = mysuite.agregaElem("Emisior")
    idtagDF = mysuite.agregaSubElem(idtag, "DomicilioFiscal")        
    for item in emisor.iterchildren():
        mysuite.agregaSubElem(idtagDF, "Calle", item.get("calle"))
        mysuite.agregaSubElem(idtagDF, "Colonia", item.get("colonia"))
        mysuite.agregaSubElem(idtagDF, "Municipio", item.get("municipio"))
        mysuite.agregaSubElem(idtagDF, "Estado", item.get("estado"))
        mysuite.agregaSubElem(idtagDF, "Pais", item.get("pais"))
        mysuite.agregaSubElem(idtagDF, "CodigoPostal", item.get("codigoPostal"))
    ####Receptor
    idtag = mysuite.agregaElem("Receptor")
    xx = mysuite.agregaSubElem(idtag, "CdgPaisReceptor", my_suite_dir['CdgPaisReceptor'])
    xx = mysuite.agregaSubElem(idtag, "RFCReceptor", receptor.get("rfc"))
    xx = mysuite.agregaSubElem(idtag, "NombreReceptor", receptor.get("nombre"))
    idtagDF = mysuite.agregaSubElem(idtag, "Domicilio")        
    for item in receptor.iterchildren():
        mysuite.agregaSubElem(idtagDF, "Calle", item.get("calle"))
        mysuite.agregaSubElem(idtagDF, "Colonia", item.get("colonia"))
        mysuite.agregaSubElem(idtagDF, "Municipio", item.get("municipio"))
        mysuite.agregaSubElem(idtagDF, "Estado", item.get("estado"))
        mysuite.agregaSubElem(idtagDF, "Pais", item.get("pais"))
        mysuite.agregaSubElem(idtagDF, "CodigoPostal", item.get("codigoPostal"))
    
    #### Conceptor
    cc = mysuite.agregaElem("Conceptos")
    for item in conceptos.iterchildren():
        concepto = mysuite.agregaSubElem(cc, "Concepto")
        xx = mysuite.agregaSubElem(concepto, "Cantidad", item.get("cantidad"))
        xx = mysuite.agregaSubElem(concepto, "UnidadDeMedida", item.get("unidad"))
        xx = mysuite.agregaSubElem(concepto, "Descripcion", item.get("descripcion"))
        xx = mysuite.agregaSubElem(concepto, "ValorUnitario", item.get("valorUnitario"))
        xx = mysuite.agregaSubElem(concepto, "Importe", item.get("importe"))
        #ccx = mysuite.agregaSubElem(concepto, "ConceptoEx")
        #imps = mysuite.agregaSubElem(ccx, "Impuestos")

    ####Totales
    Totales = mysuite.agregaElem("Totales")
    xx = mysuite.agregaSubElem(Totales, "Moneda", my_suite_dir['Moneda'])
    xx = mysuite.agregaSubElem(Totales, "TipoDeCambioVenta", my_suite_dir['tipoDeCambio'])
    xx = mysuite.agregaSubElem(Totales, "SubTotalBruto", cfdroot.get('subTotal'))
    xx = mysuite.agregaSubElem(Totales, "SubTotal", cfdroot.get('subTotal'))
    imps = mysuite.agregaSubElem(Totales, "Impuestos")
    for item in impuestos.iterchildren():
        if testItem(item, "Retenciones"):
            print 'entra'
            for item in item.iterchildren():
                impuesto = mysuite.agregaSubElem(imps, "Impuesto")
                mysuite.agregaSubElem(impuesto, "Contexto", 'Federal')
                mysuite.agregaSubElem(impuesto, "Operacion", 'RETENCION')
                mysuite.agregaSubElem(impuesto, "Monto", item.get("importe"))
                mysuite.agregaSubElem(impuesto, "Codigo", item.get("impuesto"))
        if testItem(item, "Traslados"):
            for item in item.iterchildren():
                impuesto = mysuite.agregaSubElem(imps, "Impuesto")
                mysuite.agregaSubElem(impuesto, "Contexto", 'Federal')
                mysuite.agregaSubElem(impuesto, "Operacion", 'TRASLADO')
                mysuite.agregaSubElem(impuesto, "Tasa", item.get("tasa"))
                mysuite.agregaSubElem(impuesto, "Monto", item.get("importe"))
                mysuite.agregaSubElem(impuesto, "Codigo", item.get("impuesto"))
                mysuite.agregaSubElem(impuesto, "Base", str(float(item.get("importe"))/float(item.get("tasa"))*100))
    resumenDeImpuestos = mysuite.agregaSubElem(Totales, "ResumenDeImpuestos")
    mysuite.agregaSubElem(resumenDeImpuestos, "TotalTrasladosFederales", impuestos.get("totalImpuestosTrasladados"))
    mysuite.agregaSubElem(resumenDeImpuestos, "TotalRetencionesFederales", impuestos.get("totalImpuestosRetenidos"))
    mysuite.agregaSubElem(Totales, "Total", cfdroot.get('total'))
    mysuite.agregaSubElem(Totales, "TotalEnLetra", my_suite_dir['TotalEnLetra'])
    mysuite.agregaSubElem(Totales, "FormaDePago", cfdroot.get('formaDePago'))
    comporobanteEx = mysuite.agregaElem("ComprobanteEx")
    datosnegocio = mysuite.agregaSubElem(comporobanteEx, "DatosDeNegocio")
    mysuite.agregaSubElem(datosnegocio, "Sucursal",  my_suite_dir['sucrusal'])
    mysuite.show()


create_mysuite_xml(cfe_str, {'CdgPaisEmisor': 'MX',
                             'CdgPaisReceptor': 'MX',
                             'Usuario':'MX.AAA010101AAA.AAA010101AAA',
                             'Moneda':'MXN',
                             'tipoDeCambio':'1',
                             'TotalEnLetra':'Mil',
                             'sucrusal':"BIAS"
                             })
