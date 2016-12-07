# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

#from osv import fields, osv
import time
from mx.DateTime import *
import re
import StringIO
from lxml import etree
import base64
from lxml.builder import ElementMaker
import codecs


#Variables de ambiente
MYSUITEHOST = 'www.mysuitecfdi.com'
#MYSUITEHOST = 'www.mysuitetest.com' 
MYSUITEPORT = 443

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

def getTagName(elem):
    return elem.tag[elem.tag.find("}")+1:]

def getMySuiteData1(responsexml):
    xmltree = etree.parse(StringIO.StringIO(responsexml))
    root_elem = xmltree.getroot()
    if getTagName(root_elem) == "Envelope":
        body_elem = root_elem.getchildren()[0]
        if getTagName(body_elem) == "Body":
            resp_elem = body_elem.getchildren()[0]
            if getTagName(resp_elem) == "RequestTransactionResponse":
                result_elem = resp_elem.getchildren()[0]
                if getTagName(result_elem) == "RequestTransactionResult":
                    for child in result_elem.getchildren():
                        if getTagName(child) == "ResponseData":
                            for mydata in child.getchildren():
                                if getTagName(mydata) == "ResponseData1":
                                    data1 = base64.b64decode(mydata.text)
                                    return data1
    return "RESPONSE ERROR"


def getMySuiteData2(responsexml):
    xmltree = etree.parse(StringIO.StringIO(responsexml))
    root_elem = xmltree.getroot()
    print(etree.tostring(xmltree, pretty_print=True))
    if getTagName(root_elem) == "Envelope":
        body_elem = root_elem.getchildren()[0]
        if getTagName(body_elem) == "Body":
            resp_elem = body_elem.getchildren()[0]
            if getTagName(resp_elem) == "RequestTransactionResponse":
                result_elem = resp_elem.getchildren()[0]
                if getTagName(result_elem) == "RequestTransactionResult":
                    for child in result_elem.getchildren():
                        if getTagName(child) == "ResponseData":
                            for mydata in child.getchildren():
                                if getTagName(mydata) == "ResponseData2":
                                    data2 = mydata.text
                                    return data2
    return "RESPONSE ERROR"

def getMySuiteDataDescription(responsexml):
    xmltree = etree.parse(StringIO.StringIO(responsexml))
    root_elem = xmltree.getroot()
    result = ""
    if getTagName(root_elem) == "Envelope":
        body_elem = root_elem.getchildren()[0]
        if getTagName(body_elem) == "Body":
            resp_elem = body_elem.getchildren()[0]
            if getTagName(resp_elem) == "RequestTransactionResponse":
                result_elem = resp_elem.getchildren()[0]
                if getTagName(result_elem) == "RequestTransactionResult":
                    for child in result_elem.getchildren():
                        if getTagName(child) == "Response":
                            for mydata in child.getchildren():
                                if getTagName(mydata) == "Code":
                                    result += "Code: " + mydata.text + '\n'
                                if getTagName(mydata) == "Description":
                                    result += "Description: " + mydata.text + '\n'
                                if getTagName(mydata) == "Hint":
                                    result += "Hint: " + mydata.text + '\n'
                                if getTagName(mydata) == "Data":
                                    result += "Data: " + mydata.text + '\n'
    return result or "NOT FOUND"


class MySuiteConn:
    def __init__(self):
        self.requestor = ""
        self.transaction = ""
        self.country = "MX"
        self.entity = ""
        self.user = ""
        self.username = ""
        self.data1 = ""
        self.data2 = ""
        self.data3 = ""
    
class MySuiteXML:
    NAMESPACE = "http://www.fact.com.mx/schema/fx"
    MYSUITE = "{%s}" % NAMESPACE
    NSMAP= {"fx": NAMESPACE}
    NS = 'http://www.w3.org/2001/XMLSchema-instance'
    location_attribute = '{%s}schemaLocation' % NS

    def __init__(self):
#        self.root = etree.Element('{%s}FactDocMX' %(self.NAMESPACE, ), nsmap=self.NSMAP, attrib={self.location_attribute: 'http://www.fact.com.mx/schema/fx http://www.mysuitemex.com/fact/schema/fx_2010_c.xsd'})
        self.root = etree.Element('{%s}FactDocMX' %(self.NAMESPACE, ), nsmap=self.NSMAP, attrib={self.location_attribute: 'http://www.fact.com.mx/schema/fx http://www.mysuitemex.com/fact/schema/fx_2010_d.xsd'})

        tmp = etree.SubElement(self.root, "{%s}Version" %(self.NAMESPACE, ))
        tmp.text = "5"


    def agregaElem(self, tag, text=""):
        mytag = etree.SubElement(self.root, "{%s}" %(self.NAMESPACE, ) + tag)
        if text:
            mytag.text = text
        return mytag

    def agregaSubElem(self, obj, tag, text=""):
        mytag = etree.SubElement(obj, "{%s}" %(self.NAMESPACE, ) + tag)
        if text:
            mytag.text = text
        return mytag



    def show(self):
        print etree.tostring(self.root, pretty_print=True)


MySuiteDict = {"ingreso": "FACTURA",
               "egreso": "NOTA_DE_CREDITO",
               "traslado":"CARTA_PORTE",
               "Pago en una sola exhibicion": "PAGO EN UNA SOLA EXHIBICION",}


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
#    Real Systems 25-04-2012
# 
    for item in emisor.iterchildren():
        xx = mysuite.agregaSubElem(idtag, "LugarExpedicion", "{0}, {1}".format(item.get("pais"),item.get("estado")))
    mysuite.agregaSubElem(idtag, "NumCtaPago","No identificado" )
#    Real Systems 25-04-2012
# 
    ####Emisor
    idtag = mysuite.agregaElem("Emisor")
    idtagDF = mysuite.agregaSubElem(idtag, "DomicilioFiscal")        
    for item in emisor.iterchildren():
        mysuite.agregaSubElem(idtagDF, "Calle", item.get("calle"))
        mysuite.agregaSubElem(idtagDF, "Colonia", item.get("colonia"))
        mysuite.agregaSubElem(idtagDF, "Municipio", item.get("municipio"))
        mysuite.agregaSubElem(idtagDF, "Estado", item.get("estado"))
        mysuite.agregaSubElem(idtagDF, "Pais", item.get("pais"))
        mysuite.agregaSubElem(idtagDF, "CodigoPostal", item.get("codigoPostal"))
           
#	Real Systems 25-04-2012
# 
    idtagRE = mysuite.agregaSubElem(idtag, "RegimenFiscal") 
    mysuite.agregaSubElem(idtagRE, "Regimen", 'Regimen General de Ley Personas Morales')
    
#	Real Systems 25-04-2012
#

    ####Receptor
    idtag = mysuite.agregaElem("Receptor")
    xx = mysuite.agregaSubElem(idtag, "CdgPaisReceptor", my_suite_dir['CdgPaisReceptor'])
    xx = mysuite.agregaSubElem(idtag, "RFCReceptor", receptor.get("rfc"))
    xx = mysuite.agregaSubElem(idtag, "NombreReceptor", receptor.get("nombre"))
    idtagDR = mysuite.agregaSubElem(idtag, "Domicilio")
    idtagDFM = mysuite.agregaSubElem(idtagDR, "DomicilioFiscalMexicano")        
    for item in receptor.iterchildren():
        mysuite.agregaSubElem(idtagDFM, "Calle", item.get("calle"))
        item.get("colonia") and mysuite.agregaSubElem(idtagDFM, "Colonia", item.get("colonia"))
        mysuite.agregaSubElem(idtagDFM, "Municipio", item.get("municipio"))
        mysuite.agregaSubElem(idtagDFM, "Estado", item.get("estado"))
        mysuite.agregaSubElem(idtagDFM, "Pais", item.get("pais"))
        mysuite.agregaSubElem(idtagDFM, "CodigoPostal", item.get("codigoPostal"))
    
    #### Conceptos
    cc = mysuite.agregaElem("Conceptos")
    line_num = 0
    totalIVATrasladado = 0
    totalIEPSTrasladado = 0
    totalISRRetenido = 0
    totalIVARetenido = 0
    totalTransladosLocales = 0
    totalRetencionesLocales = 0 
    for item in conceptos.iterchildren():
        importe_total = 0
        concepto = mysuite.agregaSubElem(cc, "Concepto")
        xx = mysuite.agregaSubElem(concepto, "Cantidad", item.get("cantidad"))
        xx = mysuite.agregaSubElem(concepto, "UnidadDeMedida", item.get("unidad"))
        xx = mysuite.agregaSubElem(concepto, "Descripcion", item.get("descripcion"))
        xx = mysuite.agregaSubElem(concepto, "ValorUnitario", item.get("valorUnitario"))
        xx = mysuite.agregaSubElem(concepto, "Importe", item.get("importe"))
        if my_suite_dir.has_key('impuestos_conceptos'):
            importe_total += float(item.get("importe"))
            if my_suite_dir['impuestos_conceptos'].has_key(line_num):
                ccx = mysuite.agregaSubElem(concepto, "ConceptoEx")
                imps = mysuite.agregaSubElem(ccx, "Impuestos")
                for tax in my_suite_dir['impuestos_conceptos'][line_num]:
                    impuesto = mysuite.agregaSubElem(imps, "Impuesto")
                    mysuite.agregaSubElem(impuesto, "Contexto", tax['contexto'])
                    mysuite.agregaSubElem(impuesto, "Operacion", tax['operacion'])
                    mysuite.agregaSubElem(impuesto, "Codigo", tax['codigo'])
                    mysuite.agregaSubElem(impuesto, "Base", tax['base_amount'])
                    mysuite.agregaSubElem(impuesto, "Tasa", tax['tasa'])
                    mysuite.agregaSubElem(impuesto, "Monto", tax['tax_amount'])
                    if  tax['operacion'] == 'RETENCION':
                        importe_total -= float(tax['tax_amount'])
                        if tax['codigo'] == 'IVA':
                            totalIVARetenido +=  float(tax['tax_amount'])
                        if tax['codigo'] == 'ISR':
                            totalISRRetenido +=  float(tax['tax_amount'])
                        if tax['contexto'] == 'LOCAL':
                            totalRetencionesLocales +=  float(tax['tax_amount'])
                    else:
                        importe_total += float(tax['tax_amount'])
                        if tax['codigo'] == 'IEPS':
                            totalIEPSTrasladado +=  float(tax['tax_amount'])
                        if tax['codigo'] == 'IVA':
                            totalIVATrasladado +=  float(tax['tax_amount'])
                        if tax['contexto'] == 'LOCAL':
                            totalTransladosLocales +=  float(tax['tax_amount'])
                mysuite.agregaSubElem(ccx, "ImporteTotal", str(importe_total))
        line_num += 1


    ####Totales
    Totales = mysuite.agregaElem("Totales")
    xx = mysuite.agregaSubElem(Totales, "Moneda", my_suite_dir['Moneda'])
    xx = mysuite.agregaSubElem(Totales, "TipoDeCambioVenta", my_suite_dir['tipoDeCambio'])
    xx = mysuite.agregaSubElem(Totales, "SubTotalBruto", cfdroot.get('subTotal'))
    xx = mysuite.agregaSubElem(Totales, "SubTotal", cfdroot.get('subTotal'))
    rDyR = mysuite.agregaSubElem(Totales, "ResumenDeDescuentosYRecargos")
    mysuite.agregaSubElem(rDyR, "TotalDescuentos","0")
    mysuite.agregaSubElem(rDyR, "TotalRecargos","0")
    imps = mysuite.agregaSubElem(Totales, "Impuestos")
    for item in impuestos.iterchildren():
        if testItem(item, "Retenciones"):
            for item in item.iterchildren():
                impuesto = mysuite.agregaSubElem(imps, "Impuesto")
                mysuite.agregaSubElem(impuesto, "Contexto", 'FEDERAL')
                mysuite.agregaSubElem(impuesto, "Operacion", 'RETENCION')
                mysuite.agregaSubElem(impuesto, "Monto", item.get("importe"))
                mysuite.agregaSubElem(impuesto, "Codigo", item.get("impuesto"))
        if testItem(item, "Traslados"):
            for item in item.iterchildren():
                impuesto = mysuite.agregaSubElem(imps, "Impuesto")
                mysuite.agregaSubElem(impuesto, "Contexto", 'FEDERAL')
                mysuite.agregaSubElem(impuesto, "Operacion", 'TRASLADO')
                mysuite.agregaSubElem(impuesto, "Codigo", item.get("impuesto"))
                mysuite.agregaSubElem(impuesto, "Base", str(float(item.get("importe"))/float(item.get("tasa"))*100))
                mysuite.agregaSubElem(impuesto, "Tasa", item.get("tasa"))
                mysuite.agregaSubElem(impuesto, "Monto", item.get("importe"))
    resumenDeImpuestos = mysuite.agregaSubElem(Totales, "ResumenDeImpuestos")
    mysuite.agregaSubElem(resumenDeImpuestos, "TotalTrasladosFederales", impuestos.get("totalImpuestosTrasladados"))
    mysuite.agregaSubElem(resumenDeImpuestos, "TotalIVATrasladado", str(totalIVATrasladado))
    mysuite.agregaSubElem(resumenDeImpuestos, "TotalIEPSTrasladado", str(totalIEPSTrasladado))
    mysuite.agregaSubElem(resumenDeImpuestos, "TotalRetencionesFederales", impuestos.get("totalImpuestosRetenidos") or str(0))
    mysuite.agregaSubElem(resumenDeImpuestos, "TotalISRRetenido", str(totalISRRetenido))
    mysuite.agregaSubElem(resumenDeImpuestos, "TotalIVARetenido", str(totalIVARetenido))
    mysuite.agregaSubElem(resumenDeImpuestos, "TotalTrasladosLocales", str(totalTransladosLocales))
    mysuite.agregaSubElem(resumenDeImpuestos, "TotalRetencionesLocales", str(totalRetencionesLocales))

    mysuite.agregaSubElem(Totales, "Total", cfdroot.get('total'))
    mysuite.agregaSubElem(Totales, "TotalEnLetra", my_suite_dir['TotalEnLetra'])
    mysuite.agregaSubElem(Totales, "FormaDePago", MySuiteDict[cfdroot.get('formaDePago')])
    comporobanteEx = mysuite.agregaElem("ComprobanteEx")
    datosnegocio = mysuite.agregaSubElem(comporobanteEx, "DatosDeNegocio")
    mysuite.agregaSubElem(datosnegocio, "Sucursal",  my_suite_dir['sucursal'])
#	Real Systems 25-04-2012
#
    terminosdepago=mysuite.agregaSubElem(comporobanteEx, "TerminosDePago")
    mysuite.agregaSubElem(terminosdepago, "MetodoDePago", cfdroot.get('metodoDePago'))

#    referenciasbancarias=mysuite.agregaSubElem(comporobanteEx, "ReferenciasBancarias")
#	referenciabancaria=mysuite.agregaSubElem(referenciasbancarias, "ReferenciaBancaria")
#	mysuite.agregaSubElem(referenciabancaria, "")
	
	
#	Fin Real Systems 25-04-2012
#

    return etree.tostring(mysuite.root, pretty_print=True)








