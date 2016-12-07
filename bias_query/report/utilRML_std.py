# coding: utf-8


import string
import reportlab.lib.pagesizes as pagesize
#import pooler
#import text



class document():
    def __init__(self,):
        self.ObjectType= "Document"
        self.ElementList= []
        self.filename = 'Bias'
        self.noClosing = ''

    def setfilename(self, val):
        self.filename = val
	return
    def setnoClosing(self):
        self.noClosing = True
    def addElement(self, element):
        self.ElementList.append(element)
	return
    def __repr__(self):
        ss = ''
        ss = '<?xml version="1.0"?>\n<document filename="%s.pdf">\n'%(self.filename)
        for element in self.ElementList:
                ss= ss +  '     ' + element
        if self.noClosing:
            ss = ss 
        else:
            ss = ss + ' </document>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
        return self


class template():
    def __init__(self,):
        self.ObjectType= "Document"
        self.ElementList= []
        self.title = 'Bias'
        self.pageSize='letter'
        self.leftMargin = self.rightMargin = self.bottomMargin = self.topMargin = self.showBoundary = self.rotation= ''

    def addElement(self, element):
        self.ElementList.append(element)
    	return
    def setpageSize(self, val, portrait=False):
        if type(val).__name__ not in ('list','tuple'):
            try:
                pp = 'pagesize.%s'%(val)
                pp = eval(pp)
            except:
                pp = val.split(',')
        else:
            pp = val
            
        if portrait:
            pp = (pp[1],pp[0])
        self.pageSize = str(pp[0])+' , '+str(pp[1])
    	return
    def setleftMargin(self, val):
        self.leftMargin = val
    	return
    def setrightMargin(self, val):
        self.rightMargin = val
    	return
    def setbottomMargin(self, val):
        self.bottomMargin = val
    	return
    def settopMargin(self, val):
        self.topMargin = val        
    	return
    def showBoundary(self,):
        self.showBoundary = True
    	return
    def settitle(self, val):
        self.title = val
    	return
    def setrotation(self, val):
        self.rotation = val
    	return
    def __repr__(self):
        self.ss= '<template'
        if self.pageSize:
            self.ss= self.ss + ' pageSize="%s"' %(self.pageSize,)
        if self.title:
            self.ss= self.ss + ' title="%s"' %(self.title,)
        if self.rotation:
            self.ss= self.ss + ' rotation="%s"' %(self.rotation,)
        if self.leftMargin:
            self.ss= self.ss + ' leftMargin="%s"' %(self.leftMargin,)
        if self.rightMargin:
            self.ss= self.ss + ' rightMargin="%s"' %(self.rightMargin,)
        if self.bottomMargin:
            self.ss= self.ss + ' bottomMargin="%s"' %(self.bottomMargin,)
        if self.topMargin:
            self.ss= self.ss + ' topMargin="%s"' %(self.topMargin,)
        if self.showBoundary:
            self.ss= self.ss + ' showBoundary="%s"' %(self.showBoundary,)
        self.ss= self.ss + '>\n'
        for element in self.ElementList:
            self.ss= self.ss +  '     ' +element
        self.ss= self.ss + '</template>\n'
        return self.ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
	return

class pageTemplate():
    def __init__(self,):
        self.ObjectType= "PageTemplate"
        self.ElementList= []
        self.id = 'firstpage'
        self.pageSize = self.rotation = ''
        self.portrait=False

    def addElement(self, element):
        self.ElementList.append(element)
    	return
    def setid(self, val):
        self.id = val
    	return
    def setpageSize(self, val, portrait=False ):
        if type(val).__name__ not in ('list','tuple'):
            try:
                pp = 'pagesize.%s'%(val)
                pp = eval(pp)
            except:
                pp = val.split(',')
        else:

            pp = val
        if self.portrait:
                pp = (pp[1],pp[0])
        self.width = pp[0]
        self.heith = pp[1]
        self.pageSize = str(pp[0])+' , '+str(pp[1])
    def setrotation(self, val):
        self.rotation = val
    	return
    def __repr__(self):
        self.ss= '<pageTemplate id="%s"'%(self.id)
        if self.pageSize:
            self.ss= self.ss + ' pageSize="%s"' %(self.pageSize,)
        if self.rotation:
            self.ss= self.ss + ' rotation="%s"' %(self.rotation,)
        self.ss= self.ss + '>\n'
        for element in self.ElementList:
            self.ss= self.ss + '     ' +element
        self.ss= self.ss + '</pageTemplate>\n'
        return self.ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
    	return

class frame():
    def __init__(self, ):
        pp = pagesize.letter
        self.ObjectType= "Frame"
        self.id = 'defaultFrame'
        self.x1 ='10'
        self.y1 = '10'
        self.width = pp[0]
        self.height =  pp[1]

    def setid(self, val):
        self.id = val
    	return
    def setx1(self, val):
        self.x1 = val
    	return
    def sety1(self, val):
        self.y1 = val
    	return
    def setsize(self, val, portrait=False ):
        if type(val).__name__ not in ('list','tuple'):
            try:
                pp = 'pagesize.%s'%(val)
                pp = eval(pp)
            except:
                pp = val.split(',')
        else:
            pp = val
        if portrait:
                pp = (pp[1],pp[0])
                
        self.width = str(pp[0]-10)
        self.height = str(pp[1]-10)
    def __repr__(self):
        ss = ''
        ss = '<frame id="%s" x1="%s" y1="%s" width="%s" height="%s"/>\n'%(self.id, self.x1, self.y1, self.width, self.height)
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
    	return






class stylesheet:
    def __init__(self):
        self.TipoObjeto= "Style"
        self.ElementList= []

    def addElement(self, style):
        self.ElementList.append(style)
	return
    def __repr__(self):
        ss = ''
        ss = '<stylesheet>\n'
        #ss = ss + defaultStyles()
        for style in self.ElementList:
            ss= ss + '     '+ style
        ss = ss + ' </stylesheet>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
    	return

class paraStyle():
    def __init__(self,):
        self.ObjectType= "paraStyle"
        self.name = self.alias = self.parent = self.fontname = self.leading = self.leftIndent = self.rightIndent = self.firstLineIndent = self.spaceBefore = self.spaceAfter = self.alignment = self.bulletFontname = self.bulletFontsize = self.bulletIndent = self.textColor = self.backColor = ''

    def setname(self, val):
        self.name = val
    	return
    def setalias(self, val):
        self.alias = val
    	return
    def setparent(self, val):
        self.parent = val
    	return
    def setfontname(self, val):
        self.fontname = val
    	return
    def setleading(self, val):
        self.leading = val
    	return
    def setleftIndent(self, val):
        self.leftIndent = val
    	return
    def setrightIndent(self, val):
        self.rightIndent = val
    	return
    def setfirstLineIndent(self, val):
        self.firstLineIndent = val
    	return
    def setspaceBefore(self, val):
        self.spaceBefore = val
    	return
    def setspaceAfter(self, val):
        self.spaceAfter = val
    	return
    def setalignment(self, val):
        self.alignment= val
    	return
    def setbulletFontname(self, val):
        self.bulletFontname = val
    	return
    def setbulletFontsize(self, val):
        self.bulletFontsize = val
    	return
    def setbulletIndent(self, val):
        self.bulletIndent = val
    	return
    def settextColor(self, val):
        self.textColor= val
    	return
    def setbackColor(self, val):
        self.backColor = val
    	return
    def __repr__(self):
        ss= '<paraStyle'
        if self.name:
            ss= ss + ' name="%s"' %(self.name,)
        if self.alias:
            ss= ss + ' alias="%s"' %(self.alias,)
        if self.parent:
            ss= ss + ' parent="%s"' %(self.parent,)
        if self.fontname:
            ss= ss + ' fontname="%s"' %(self.fontname,)
        if self.leading:
            ss= ss + ' leading="%s"' %(self.leading,)
        if self.leftIndent:
            ss= ss + ' leftIndent="%s"' %(self.leftIndent,)
        if self.rightIndent:
            ss= ss + ' rightIndent="%s"' %(self.rightIndent,)
        if self.firstLineIndent:
            ss= ss + ' firstLineIndent="%s"' %(self.firstLineIndent,)
        if self.spaceBefore:
            ss= ss + ' spaceBefore="%s"' %(self.spaceBefore,)
        if self.spaceAfter:
            ss= ss + ' spaceAfter="%s"' %(self.spaceAfter,)
        if self.alignment:
            ss= ss + ' alignment="%s"' %(self.alignment,)
        if self.bulletFontname:
            ss= ss + ' bulletFontname="%s"' %(self.bulletFontname,)
        if self.bulletFontsize:
            ss= ss + ' bulletFontsize="%s"' %(self.bulletFontsize,)
        if self.bulletIndent:
            ss= ss + ' bulletIndent="%s"' %(self.bulletIndent,)
        if self.textColor:
            ss= ss + ' textColor="%s"' %(self.textColor,)
        if self.backColor:
            ss= ss + ' backColor="%s"' %(self.backColor,)
        ss= ss + '/>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
    	return

class blockTableStyle:
    ####Falta termiar de hacer blockValign = self.blockValign_ctx = self.blockLeftPadding= self.blockLeftPaddin_ctx = self.blockRightPadding = self.blockRightPadding_ctx  = self.blockbottomPadding =  self.blockbottomPadding_ctx = self.blockTopPadding = self.blockTopPadding_ctx
    def __init__(self, styleName):
        self.TipoObjeto= "blockTableStyle"
        self.blockTextColor = []
        self.blockTextColor_ctx = []
        self.blockLeading = []
        self.blockLeading_ctx = []
        self.blockAlignment = []
        self.blockAlignment_ctx = []
        self.blockValign = []
        self.blockValign_ctx = []
        self.blockLeftPadding= []
        self.blockLeftPaddin_ctx =[]
        self.blockRightPadding = []
        self.blockRightPadding_ctx  = []
        self.blockbottomPadding = []
        self.blockbottomPadding_ctx =[]
        self.blockTopPadding = []
        self.blockTopPadding_ctx = []
        self.blockBackground = []
        self.blockBackground_ctx = []
        self.lineStyle = []
        self.lineStyle2 = []
        self.lineStyle_ctx = []
        self.blockFont = []
        self.blockFont_ctx = []
        self.ListaRenglones= []
        self.styleName = styleName

    def addElement(self, renglon):
        self.ListaRenglones.append(renglon)
    	return
    def setblockFont(self, val, ctx = {}):
        self.blockFont.append(val)
        self.blockFont_ctx.append(ctx)
    def setblockTextColor(self,val, ctx = {}):
        self.blockTextColor.append(val)
        self.blockTextColor_ctx.append(ctx)
    def setblockAlignment(self, val, ctx = {}):
        self.blockAlignment.append(val)
        self.blockAlignment_ctx.append(ctx)
    def setblockBackground(self, val , ctx= {}):
        self.blockBackground.append(val)
        self.blockBackground_ctx.append(ctx)
    def setblockValign(self, val , ctx= {}):
        self.blockValign.append(val)
        self.blockValign_ctx.append(ctx)
    def setlineStyle(self, val, val2, ctx={}):
        self.lineStyle.append(val)
        self.lineStyle2.append(val2)
        self.lineStyle_ctx.append(ctx)
    def __repr__(self):
        ss = ''
        ss = ss + '<blockTableStyle id="%s" >\n' %( self.styleName)
        for ii in range(len(self.blockFont)):
                ss = ss + '     <blockFont name="%s"' %(self.blockFont[ii])
                for cc in self.blockFont_ctx[ii].keys():
                    ss = ss + ' ' +  cc + '="%s"' %(self.blockFont_ctx[ii][cc],)
                ss = ss + '/>\n'
        for ii in range(len(self.blockTextColor)):
            ss = ss + '     <blockTextColor colorName="%s"' %(self.blockTextColor[ii],)
            for cc in self.blockTextColor_ctx[ii].keys():
                ss = ss + ' ' +  cc + '="%s"' %(self.blockTextColor_ctx[ii][cc],)
            ss = ss + '/>\n'
        for ii in range(len(self.blockAlignment)):
            ss = ss + '     <blockAlignment value="%s"' %(self.blockAlignment[ii],)
            for cc in self.blockAlignment_ctx[ii].keys():
                    ss = ss + ' ' +  cc + '="%s"' %(self.blockAlignment_ctx[ii][cc],)
            ss = ss + '/>\n'
        for ii in range(len(self.blockBackground)):
            ss = ss + '     <blockBackground colorName="%s"' %(self.blockBackground[ii],)
            for cc in self.blockBackground_ctx[ii].keys():
                ss = ss + ' ' +  cc + '="%s"' %(self.blockBackground_ctx[ii][cc],)
            ss = ss + '/>\n'
        for ii in range(len(self.blockValign)):
            ss = ss + '     <blockValign value="%s"' %(self.blockValign[ii],)
            for cc in self.blockValign_ctx[ii].keys():
                    ss = ss + ' ' +  cc + '="%s"' %(self.blockValign_ctx[ii][cc],)
            ss = ss + '/>\n'
        for ii in range(len(self.lineStyle)):
            ss = ss + '     <lineStyle kind="%s" colorName="%s"' %(self.lineStyle[ii], self.lineStyle2[ii])
            for cc in self.lineStyle_ctx[ii].keys():
                ss = ss + ' ' +  cc + '="%s"' %(self.lineStyle_ctx[ii][cc],)
            ss = ss + '/>\n'
        ss= ss + '</blockTableStyle>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
        pass
    	return

class story():
    def __init__(self):
        self.TipoObjeto= "Story"
        self.ElementList= []
    def addElement(self, style):
        self.ElementList.append(style)
    	return
    def __repr__(self):
        ss = ''
        ss = '<story>\n'
        for element in self.ElementList:
            ss= ss + '     '+ element
        ss = ss + ' </story>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
       return other + self.__repr__()
    def imprime(self):
        pass
    	return

class para():
    def __init__(self,):
        self.ObjectType= "para"
        self.ElementList = []
        self.style = self.fontname = self.fontsize = self.leading = self.leftIndent = self.rightIndent = self.firstLineIndent = self.spaceBefore = self.spaceAfter = self.alignment = self.bulletFontname = self.bulletFontsize = self.bulletIndent = self.textColor = self.backColor = self.noClosing = ''
    def setstyle(self, val):
        self.style = val
    	return
    def setfontname(self, val):
        self.fontname = val
    	return
    def setfontsize(self, val):
        self.fontsize = val
    	return
    def setleading(self, val):
        self.leading = val
    	return
    def setleftIndent(self, val):
        self.leftIndent = val
    	return
    def setrightIndent(self, val):
        self.rightIndent = val
    	return
    def setfirstLineIndent(self, val):
        self.firstLineIndent = val
    	return
    def setspaceBefore(self, val):
        self.spaceBefore = val
    	return
    def setspaceAfter(self, val):
        self.spaceAfter = val
    	return
    def setalignment(self, val):
        self.alignment= val
    	return
    def setbulletFontname(self, val):
        self.bulletFontname = val
    	return
    def setbulletFontsize(self, val):
        self.bulletFontsize = val
    	return
    def setbulletIndent(self, val):
        self.bulletIndent = val
    	return
    def settextColor(self, val):
        self.textColor= val
    	return
    def setbackColor(self, val):
        self.backColor = val
    	return
    def setnoClosing(self):
        self.noClosing = True
    	return
    def __repr__(self):
        ss= '<para'
        if self.fontname:
            ss= ss + ' fontName="%s"' %(self.fontname,)
        if self.fontsize:
            ss= ss + ' fontSize="%s"' %(self.fontsize,)
        if self.leading:
            ss= ss + ' leading="%s"' %(self.leading,)
        if self.leftIndent:
            ss= ss + ' leftIndent="%s"' %(self.leftIndent,)
        if self.rightIndent:
            ss= ss + ' rightIndent="%s"' %(self.rightIndent,)
        if self.firstLineIndent:
            ss= ss + ' firstLineIndent="%s"' %(self.firstLineIndent,)
        if self.spaceBefore:
            ss= ss + ' spaceBefore="%s"' %(self.spaceBefore,)
        if self.spaceAfter:
            ss= ss + ' spaceAfter="%s"' %(self.spaceAfter,)
        if self.alignment:
            ss= ss + ' alignment="%s"' %(self.alignment,)
        if self.bulletFontname:
            ss= ss + ' bulletFontname="%s"' %(self.bulletFontname,)
        if self.bulletFontsize:
            ss= ss + ' bulletFontsize="%s"' %(self.bulletFontsize,)
        if self.bulletIndent:
            ss= ss + ' bulletIndent="%s"' %(self.bulletIndent,)
        if self.textColor:
            ss= ss + ' textColor="%s"' %(self.textColor,)
        if self.backColor:
            ss= ss + ' backColor="%s"' %(self.backColor,)
        if self.style:
            ss= ss + ' style="%s"' %(self.style,)
        ss= ss + '>\n'
        for element in self.ElementList:
            ss= ss + element
        if self.noClosing:
            ss = ss+ ' '
        else:
            ss = ss + '</para>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
        pass
    	return

class h1():
    def __init__(self,):
        self.ObjectType= "h1"
        self.ElementList = []
        self.style = ''
    def setstyle(self, val):
        self.style = val
    	return
    def addElement(self, val):
        self.ElementList.append(val)
    	return
    def __repr__(self):
        ss= '<h1'
        if self.style:
            ss= ss + ' style="%s"' %(self.style,)
        ss= ss + '/>\n'
        for element in self.ElementList:
            ss= ss + element
        ss= ss + '</h1>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
        pass
    	return

class h2():
    def __init__(self,):
        self.ObjectType= "h2"
        self.ElementList = []
        self.style = ''
    def setstyle(self, val):
        self.style = val
    	return
    def addElement(self, val):
        self.ElementList.append(val)
    	return
    def __repr__(self):
        ss= '<h2'
        if self.style:
            ss= ss + ' style="%s"' %(self.style,)
        ss= ss + '/>\n'
        for element in self.ElementList:
            ss= ss + element
        ss= ss + '</h2>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
        pass
    	return

class h3():
    def __init__(self,):
        self.ObjectType= "h3"
        self.ElementList = []
        self.style = ''
    def setstyle(self, val):
        self.style = val
    	return
    def addElement(self, val):
        self.ElementList.append(val)
    	return
    def __repr__(self):
        ss= '<h3'
        if self.style:
            ss= ss + ' style="%s"' %(self.style,)
        ss= ss + '/>\n'
        for element in self.ElementList:
            ss= ss + element
        ss= ss + '</h3>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
        pass
    	return

class title():
    def __init__(self,):
        self.ObjectType= "title"
        self.ElementList = []
        self.style = ''
    def setstyle(self, val):
        self.style = val
    	return
    def addElement(self, val):
        self.ElementList.append(val)
    	return
    def __repr__(self):
        ss= '<title'
        if self.style:
            ss= ss + ' style="%s"' %(self.style,)
        ss= ss + '/>\n'
        for element in self.ElementList:
            ss= ss + element
        ss= ss + '</title>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
        pass
    	return

class pageGraphics():
    def __init__(self,):
        self.ObjectType= "pageGraphics"
        self.ElementList = []
    def addElement(self, val):
        self.ElementList.append(val)
    	return
    def __repr__(self):
        ss= '<pageGraphics'
        ss= ss + '>\n'
        for element in self.ElementList:
            ss= ss + element
        ss= ss + '</pageGraphics>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
        pass
	return

class drawString():
    def __init__(self,):
        self.ObjectType= "drawString"
        self.ElementList = []
        self.x = self.y ='1cm'
    def setx(self, val):
        self.x = val
    	return
    def sety(self, val):
        self.y = val
    	return
    def addElement(self, val):
        self.ElementList.append(val)        
    	return
    def __repr__(self):
        ss= '<drawString'
        if self.x:
            ss= ss + ' x="%s"' %(self.x,)
        if self.y:
            ss= ss + ' y="%s"' %(self.y,)
        ss= ss + '>\n'
        for element in self.ElementList:
            ss= ss + element
        ss= ss + '</drawString>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
        pass
    	return

class drawRightString():
    def __init__(self,):
        self.ObjectType= "drawRightString"
        self.ElementList = []
        self.x = self.y ='1cm'
    def setx(self, val):
        self.x = val
    	return
    def sety(self, val):
        self.y = val
    	return
    def addElement(self, val):
        self.ElementList.append(val)        
    	return
    def __repr__(self):
        ss= '<drawRightString'
        if self.x:
            ss= ss + ' x="%s"' %(self.x,)
        if self.y:
            ss= ss + ' y="%s"' %(self.y,)
        ss= ss + '/>\n'
        for element in self.ElementList:
            ss= ss + element
        ss= ss + '</drawRightString>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
        pass
    	return

class drawCentredString():
    def __init__(self,):
        self.ObjectType= "drawCentredString"
        self.ElementList = []
        self.x = self.y ='1cm'
    def setx(self, val):
        self.x = val
    	return
    def sety(self, val):
        self.y = val
    	return
    def addElement(self, val):
        self.ElementList.append(val)        
    	return
    def __repr__(self):
        ss= '<drawCentredString'
        if self.x:
            ss= ss + ' x="%s"' %(self.x,)
        if self.y:
            ss= ss + ' y="%s"' %(self.y,)
        ss= ss + '/>\n'
        for element in self.ElementList:
            ss= ss + element
        ss= ss + '</drawCentredString>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
        pass
    	return

class blockTable:
    def __init__(self):
        self.TipoObjeto= "Tabla"
        self.style = self.colWidths = self.rowHeights= self.repeatRows = self.lineStyle = self.blockFont = ''
        self.ListaRenglones = []
    def agregaRenglon(self, renglon):
        self.ListaRenglones.append(renglon)
    	return
    def addElement(self, renglon):
        self.ListaRenglones.append(renglon)
    	return
    def setstyle(self, val):
        self.style = val
    	return
    def setcolWidths(self, val):
        self.colWidths = val
    	return
    def setrowHeights(self, val):
        self.rowHeights = val
    	return
    def setrepeatRows(self, val):
        self.repeatRows = val
    	return
    def setblockFont(self, val):
        self.blockFont =  val
    	return
    def setlineStyle(self, val):
        self.lineStyle = val
    	return
    def __repr__(self):
        ss= '<blockTable'
        if self.style:
            ss= ss + ' style="%s"' %(self.style,)
        if self.colWidths:
            ss= ss + ' colWidths="%s"' %(self.colWidths,)
        if self.rowHeights:
            ss= ss + ' rowHeights="%s"' %(self.rowHeights,)
        if self.repeatRows:
            ss= ss + ' repeatRows="%s"' %(self.repeatRows,)
        if self.lineStyle:
            ss = ss + ' lineStyle="%s"' %(self.lineStyle,)
        if self.blockFont:
            ss = ss + ' blockFont name="%s"' %(self.blockFont,)
        ss= ss + '>\n'
        for renglon in self.ListaRenglones:
            ss= ss + renglon
        ss= ss + '</blockTable>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
    	return

class tr:
    def __init__(self):
        self.TipoObjeto= "tr"
        self.ListaElem = []
        self.ListafontName = []
        self.ListafontSize = []
        self.ListafontColor = []
        self.Listaleading = []
        self.ListaleftPadding = []
        self.ListarightPadding = []
        self.ListatopPadding = []
        self.Listabackground = []
        self.ListabottomPadding = []
        self.Listaalign = []
        self.ListavAlign = []
    def addElement(self, elem, context={}):
        if type(elem).__name__ in ['int', 'long int',  'float']:
            self.ListaElem.append(`elem`)
        else:
            if type(elem).__name__ == 'str':
                elem = elem.strip("'u'")
                elem = elem.strip("'")
                self.ListaElem.append(str(elem))
            else:
                self.ListaElem.append(str(elem.encode('utf-8')))
        if context.get('fontName', False):
            self.ListafontName.append(context['fontName'])
        else:
            self.ListafontName.append('')
        if context.get('fontSize', False):
            self.ListafontSize.append(context['fontSize'])
        else:
            self.ListafontSize.append('')
        if context.get('fontColor', False):
            self.ListafontColor.append(context['fontColor'])
        else:
            self.ListafontColor.append('')
        if context.get('leading', False):
            self.Listaleading.append(context['leading'])
        else:
            self.Listaleading.append('')
        if context.get('leftPadding', False):
            self.ListaleftPadding.append(context['leftPadding'])
        else:
            self.ListaleftPadding.append('')
        if context.get('rightPadding', False):
            self.ListarightPadding.append(context['rightPadding'])
        else:
            self.ListarightPadding.append('')
        if context.get('topPadding', False):
            self.ListatopPadding.append(context['topPadding'])
        else:
            self.ListatopPadding.append('')
        if context.get('bottomPadding', False):
            self.ListabottomPadding.append(context['bottomPadding'])
        else:
            self.ListabottomPadding.append('')
        if context.get('background', False):
            self.Listabackground.append(context['background'])
        else:
            self.Listabackground.append('')
        if context.get('align', False):
            self.Listaalign.append(context['align'])
        else:
            self.Listaalign.append('')
        if context.get('vAlign', False):
            self.ListavAlign.append(context['vAlign'])
        else:
            self.ListavAlign.append('')
    	return

    def __repr__(self):
        ss= '<tr'
        ss= ss + '>'
        for i in range(len(self.ListaElem)):
            ss = ss  + '<td'
            if self.ListafontName[i]:
                ss= ss + ' fontNam="%s"' %(self.ListafontName[i], )
            if self.ListafontSize[i]:
                ss= ss + ' fontSize="%s"' %(self.ListafontSize[i], )
            if self.ListafontColor[i]:
                ss= ss + ' fontColor="%s"' %(self.ListafontColor[i], )
            if self.Listaleading[i]:
                ss= ss + ' leading="%s"' %(self.Listaleading[i], )
            if self.ListaleftPadding[i]:
                ss= ss + ' leftPadding="%s"' %(self.ListaleftPadding[i], )
            if self.ListarightPadding[i]:
                ss= ss + ' rightPadding="%s"' %(self.ListarightPadding[i], )
            if self.ListatopPadding[i]:
                ss= ss + ' topPadding="%s"' %(self.ListatopPadding[i], )
            if self.ListabottomPadding[i]:
                ss= ss + ' bottomPadding="%s"' %(self.ListabottomPadding[i], )
            if self.Listabackground[i]:
                ss= ss + ' background="%s"' %(self.Listabackground[i], )
            if self.Listaalign[i]:
                ss= ss + ' align="%s"' %(self.Listaalign[i], )
            if self.ListavAlign[i]:
                ss= ss + ' vAlign="%s"' %(self.ListavAlign[i], )
            ss= ss + '>'
            ss= ss + str(self.ListaElem[i])
            ss= ss + '</td>'
        ss= ss + '</tr>\n'
        return ss
    def __add__(self, other):
        return self.__repr__() + other
    def __radd__(self, other):
        return other + self.__repr__()
    def imprime(self):
	return

def getdefaultStyles():
    res = '''
         <paraStyle name="H1" fontName="Helvetica-Bold" fontSize="18" spaceBefore="0.4 cm" alignment="CENTER"/>
         <paraStyle name="H2" fontName="Helvetica-Bold" fontSize="14" spaceBefore="0.4 cm" alignment="CENTER"/>
         <paraStyle name="H3" fontName="Helvetica-Bold" fontSize="12" spaceBefore="0.4 cm" alignment="CENTER"/>
         <paraStyle name="body1" fontName="Helvetica" fontSize="10" leftIndent="5" spaceAfter="5" alignment="LEFT"/>
         <paraStyle name="body1c" fontName="Helvetica" fontSize="10" leftIndent="5" spaceAfter="5" alignment="CENTER"/>
         <paraStyle name="right"  alignment="RIGTH"/>


         <blockTableStyle id="products">
         <!-- <blockBackground colorName="grey" start="0,0" stop="-1,0"/> -->
         <blockFont name="Helvetica-Bold" size="10" start="0,0" stop="-1,0" />
         <lineStyle kind="LINEBELOW" colorName="#000000" start="0,0" stop="-1,0"/>
         <blockValign value="TOP"/>
         <blockAlignment value="LEFT"/>
         <lineStyle kind="LINEBELOW" colorName="#e6e6e6" start="0,1" stop="-1,-1"/>
         <!-- <lineStyle kind="GRID" colorName="black"/> -->
         </blockTableStyle>

         <blockTableStyle id="table1">
         <blockBackground colorName="silver" start="0,0" stop="-1,0"/>
         <blockAlignment value="LEFT"/>
         <blockValign value="MIDDLE"/>
         <!-- Set fonts -->
         <blockFont name="Helvetica-Bold" size="12" start="0,0" stop="-1,0" />
         <blockFont name="Helvetica" size="10" start="1,0" stop="-1,-1" />
         <lineStyle kind="GRID" colorName="black" />
         </blockTableStyle> \n

         <blockTableStyle id="table2">
         <blockBackground colorName="whitesmoke" start="0,0" stop="-1,0"/>
         <blockAlignment value="LEFT"/>
         <blockValign value="MIDDLE"/>
         <!-- Set fonts -->
         <blockFont name="Helvetica-Bold" size="10" start="0,0" stop="-1,0" />
         <blockFont name="Helvetica" size="7" start="1,1" stop="1,-1" />
         <lineStyle kind="GRID" colorName="black" start="0,0" stop="-1,0" />
         </blockTableStyle> \n

         
         <blockTableStyle id="table_header">
              <blockBackground colorName="whitesmoke" start="0,0" stop="-1,0"/>
              <blockAlignment value="CENTER"/>
              <blockValign value="MIDDLE"/>
              <!-- Set fonts -->
         <blockFont name="Helvetica-Bold" size="11" start="1,1" stop="1,1" /> 
         
         <blockFont name="Helvetica" size="8" start="2,0" stop="2,-1" />
         <!-- <lineStyle kind="GRID" colorName="black" start="0,0" stop="-1,-1" /> -->
         </blockTableStyle> \n



       <blockTableStyle id="header" >
             <blockFont name="Helvetica" start="0,0" stop="-1,-1" size="9"/>
             <blockFont name="Helvetica" start="1,0" stop="1,0" size="9"/>
             <blockFont name="Helvetica" start="2,0" stop="2,1" size="7"/>
             <blockFont name="Helvetica-Bold" start="1,1" stop="1,1" size="12"/>
             <blockAlignment value="CENTER" start="1,0" stop="1,-1"/>
             <blockAlignment value="LEFT" start="0,0" stop="0,-1"/>
             <blockAlignment value="RIGHT" start="2,0" stop="2,-1"/>
       </blockTableStyle>

       <blockTableStyle id="header-options" >
          <blockFont name="Helvetica" start="0,0" stop="-1,-1" size="9"/>
          <blockAlignment value="LEFT" start="0,0" stop="-1,-1"/>
       </blockTableStyle>
         


         '''
    return res

def getdefaultTemplate(paper='letter',portrait=False):
    temp = template()
    temp.settitle('Bias Report')
    temp.setpageSize(paper, portrait)
    pageT = pageTemplate()
    pageT.setid('first')
    fr = frame()
    fr.setx1('10')
    fr.sety1('10')
    pageGP = pageGraphics()
    drawStr = drawString()
    drawStr.sety('10')
    drawStr.sety('10')
    drawStr.addElement('Page: "<pageNumber/>"')
    pageGP.addElement(drawStr)
    pageT.addElement(fr)
    pageT.addElement(pageGP)
    temp.addElement(pageT)
    #temp.addElement(fr)
    return temp


def _make_file(text):
    import StringIO, base64
    buf=StringIO.StringIO()
    writer=buf.write(text)
    out=base64.encodestring(buf.getvalue())
    buf.close()
    return out

def imprimeTablaCSV_CDR(cdrData ,colTitles, csv_text):
    if colTitles:
        for i in colTitles:
            csv_text += `i` + ','
        csv_text += '\n'
    for ii in cdrData:
        rrx=[]
        for i in range(len(ii)):
            if type(ii[i]).__name__ == 'unicode':
                ii[i] = ii[i].encode('utf-8')
            csv_text += `ii[i]` + ','
        csv_text += '\n'
    return csv_text

def getstandarReportHeader(data, table_functions):
    style = blockTableStyle('header',)
    style.setblockFont('Helvetica',{'size':'9','start':'0,0','stop':'-1,-1'})
    style.setblockFont('Helvetica',{'size':'14','start':'1,0','stop':'1,0'})
    style.setblockFont('Helvetica-Bold',{'size':'16','start':'1,1','stop':'1,2'})
    #style.setlineStyle('Box','Black')
    style.setblockAlignment('CENTER',{'start':'0,1','stop':'-1,1'})
    style.setblockAlignment('LEFT',{'start':'0,0','stop':'0,-1'})
    style.setblockAlignment('RIGHT',{'start':'-1,0','stop':'-1,1'})
    style.setlineStyle('BOX' , 'black',)
    table = blockTable()
    table.setrowHeights(".5cm")
    pp = 'pagesize.%s'%(table_functions['page'])
    pp = eval(pp)
    if table_functions['portrait']:
        pp = (pp[1],pp[0])
    col_len = (pp[0]-20) / 3
    table.setcolWidths("%s,%s,%s"%(col_len,col_len,col_len))
    table.setstyle('header')
    for complete_row in data:
        row = tr()
        for row_data in complete_row:
            row.addElement(row_data)
        table.addElement(row)
    return table, style

def getstandarTable(data, colTitles, colWidths, rowHeight):
    if (data and colTitles) and (len(data[0]) != len(colTitles)):
        table = blockTable()
        row = tr()
        row.addElement('The lenght of the Column Titles( %i ) and the data ( %i ) are diferent'%(len(colTitles),len(data[0])))
        table.setrowHeights("1cm")
        table.setcolWidths("10cm")
        table.setrepeatRows('1')
        table.addElement(row)
        return table
    if (colWidths and data) and (len(data[0]) != len(colWidths.split(','))):
        table = blockTable()
        row = tr()
        row.addElement('The lenght of the Column Widths ( %i )  and the data ( %i ) are diferent'%(len(colWidths.split(',')),len(data[0])))
        table.addElement(row)
        table.setrowHeights("1cm")
        table.setcolWidths("10cm")
        return table
    decimal = 2
    table = blockTable()
    hh = 0
    if colTitles:
        row = tr()
        for dd in colTitles:
            row.addElement(str(dd))
        table.addElement(row)
        hh += 1
    word_size = colWidths.split(',')
    for row_data in data:
        row = tr()
        for i,dd in enumerate(row_data):
            if type(dd).__name__ == 'float':
                dd = '%.2f'%dd
                dd = text.moneyfmt(dd)
                row.addElement(dd)
            elif type(dd).__name__ == 'int':
                dd = text.moneyfmt(dd)
                row.addElement(dd)
            elif type(dd).__name__ == 'bool':
                row.addElement(dd)
            else:
                ws = int(round((float(word_size[i]) - .3)/.2))
                if ws == 0:
                    ws =1
                ws = int(round(ws / 8)) + ws
                row.addElement('<para>' + dd[:ws] + '</para>')
        table.addElement(row)
        hh += 1
    if not rowHeight:
        rowHeights = smallrowHeights(hh)
    else:
        rowHeights = standarRowHeights(hh, rowHeight)
    if not colWidths:
        colWidths = [1 for a in range(len(data[0]))]
    #table.setrowHeights(rowHeights)
    table.setcolWidths(colWidths)
    return table



def cleanData(dd, decimal):
    dd_type = type(dd).__name__
    res = dd
    dd_type_ctx = {}
    if dd_type ==  'float':
        res = '%.2f'%(dd)
    if dd_type in ['int', 'long int']:
        res = `dd`
    if dd_type in ['int', 'long int','float']:
        dd_type_ctx['align'] = 'RIGHT'
        if dd < 0 :
            dd_type_ctx['fontColor']='red'
    
    return res, dd_type_ctx

def tableKeyTitles(dicc, titles, keys):
    rrT = tr()
    for kk in keys:
        context =  {
            'fontName':'Helvetica-Bold',
            'fontSize':'12',
            'align':'CENTER',
            'background':'lightgrey'}
        if titles.get(kk, False):
            tt = titles[kk]
        else:
            tt = kk
        rrT.addElement(tt, context)
    return rrT

def logicaDict(data, res , nombre_renglon='', last_key = ''):
        keys = data.keys()
        keys.sort()
        for level_key in keys:
            if nombre_renglon or last_key:
                nombre_renglon = last_key + ' | ' + level_key
            else:
                nombre_renglon = level_key
            if type(data[level_key]).__name__ == 'dict':
                last_key = nombre_renglon
                nombre_renglon = ''
                res, nombre_renglon, last_key = logicaDict(data[level_key], res, nombre_renglon, last_key)
            else:
                res[nombre_renglon] = data[level_key]
                #nombre_renglon
                nombre_renglon = last_key
        last_key = ''
        nombre_renglon = ''
        return res, nombre_renglon , last_key
    
def smallrowHeights(len):
    rowheigths = ''
    for rr in range(len):
        if rowheigths:
            rowheigths = rowheigths + ','
        rowheigths = 	rowheigths +  '.5cm'
    return rowheigths

def standarRowHeights(len, height=''):
    rowheigths = ''
    if not height:
        height = '.5cm'
    for rr in range(len):
        if rowheigths:
            rowheigths = rowheigths + ','
        rowheigths = 	rowheigths +  height
    return rowheigths

def autocolWidths(collen, pp, collen_last=[]):
    ttw = 0
    if type(pp).__name__ == 'str':
        if pp.isdigit():
            size = int(pp)
    elif type(pp).__name__ in ['tuple', 'list']:
        size = pp[0]
    available_with = size
    margin = available_with * .05
    available_with = available_with - margin
    i = 0
    if not collen_last:
        for rr in collen:
            collen_last.append(rr)
    for aa in collen:
        ttw += (int(aa) + int(collen_last[i]))/2
    if not ttw:
        ttw = 1
    proporcion = available_with/ttw
    colwith = ''
    collen_new = []
    for aa in collen:
        if colwith:
            colwith = colwith + ','
        colwith  = colwith + str('%.0f'%(((int(aa) + int(collen_last[i]))/2)*proporcion))
        collen_new.append((int(aa)+ int(collen_last[i])/2)*proporcion)
    return colwith, collen_new
    


