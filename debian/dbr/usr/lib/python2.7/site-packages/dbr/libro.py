# -*- coding: iso-8859-15 -*-


import xml.dom.minidom as MD
import ntpath,re

from dbr_i18n import _          #For i18n support

class Libro:
  """
  Class to manipulate a book
  """



  def __init__(self, fichero, pos_indice=0, pos_nodos_libro=0, pos_audio=0):
    """
    Start a book object that allows access to all data files DAISY
    """
    
    self.indice = []
    self.nodos_libro = []
    self.pos_sig_indice = self.pos_indice = pos_indice
    self.pos_sig_nodos_libro = self.pos_nodos_libro = pos_nodos_libro
    self.pos_audio = pos_audio
    self.tree = MD.parse(fichero)
    self.nombre_libro = self.obtener_nombre()
    self.ruta_libro = fichero
    self.obtener_arbol()
    self.obtener_pistas(self.nodos_libro[self.pos_nodos_libro])
    

  # strip whitespaces start
  @staticmethod
  def process_group(group_in):
    return " ".join(group_in).replace('> <', '><') + '\n'
    
  def create_new_temp_file(self, nombre):
      new_file = open(nombre+'.tmp', "w")
      
      with open(nombre, "r") as fp_in:
        starters = ["<h1", "<h2", "<span", "</body"]
        this_group = []
        for rec in fp_in:
            rec = rec.strip()
            for start_lit in starters:
                if rec.startswith(start_lit):
                    new_file.write(self.process_group(this_group))
                    this_group = []
            this_group.append(rec)
 
      ## process last group
      new_file.write(self.process_group(this_group))
      new_file.close()
      return new_file.name

  def obtener_nombre(self):
    """
    Method to obtain the name of the book
    """
    nombre = ''
    meta = self.tree.getElementsByTagName('meta')
    encontrado = 0
    i = 0
    while encontrado == 0 and i < len(meta):
      if meta[i].hasAttribute('name'):
        if meta[i].attributes['name'].value == 'dc:title':
          nombre = meta[i].attributes['content'].value
          encontrado = 1
      i = i+1
    return nombre


  def obtener_numero_paginas(self):
    """
    Method to get the number of pages of a book
    """
    meta = self.tree.getElementsByTagName('meta')
    encontrado = 0
    i = 0
    while (encontrado == 0) and (i < len(meta)):
      if meta[i].hasAttribute('name'):
        if (meta[i].attributes['name'].value == 'ncc:pageNormal') or (meta[i].attributes['name'].value == 'ncc:page-normal'):
          paginas_totales_libro = meta[i].attributes['content'].value
          encontrado = 1
      i = i+1
    return paginas_totales_libro


  def obtener_datos_para_marca(self):
    """
    Method to get the index position of the nodes of the book , audio , and the name and path of the book
    """
    informacion = []
    informacion.append(self.nombre_libro)
    informacion.append(self.ruta_libro)
    informacion.append(self.pos_indice)
    informacion.append(self.pos_nodos_libro)
    informacion.append(self.pos_audio-1)
    return informacion


  def obtener_indice(self):
    """
    Method to get the index of the book
    """
    return self.indice


  def obtener_pos_indice(self):
    """
    Method to get the index position
    """
    return self.pos_indice


  def obtener_nodo_actual(self):
    """
    Method for playing the current node
    """
    return self.nodos_libro[self.pos_nodos_libro]
    
  def obtener_nodo_distance(self,direction):
    """
    Method for finding out the distance between current playing node and nearest h1 node(i.e chapter) in forward/backward
    direction
    """
    
    if(direction == "forward"):
	counter = 0
	for i in range(self.pos_indice,len(self.indice)):
	    if(self.indice[i+1].tagName == "h1"):
	       break
	    else:
	       counter = counter+1
	return counter+1

    if(direction == "backword"):
	rev_counter = 0
	for j in range(self.pos_indice,-1,-1):
	    
	    if(self.indice[j-1].tagName == "h1"):
	       break
	    else:
	       rev_counter = rev_counter + 1
	return rev_counter+1
 
  def obtener_subarbol(self, listaNodos, lista, listado):
    """
    Método para obtener un subarbol del libro
    """
    for x in listaNodos:
      x.childNodes = [i for i in x.childNodes if str(i.nodeValue).strip()]
      if len(x.childNodes) > 1:
        lista, listado = self.obtener_subarbol(x.childNodes, lista, listado)
      elif len(x.childNodes) == 1 and str(x.nodeValue).strip():
        listado.append(x)
        if x.hasAttribute('class'):
          at = x.attributes['class']
          if ((at.value == 'title') or (at.value == 'chapter') or (at.value == 'section') or (at.value == 'sub-section') or(at.value == 'jacket') or (at.value == 'front') or (at.value == 'title-page') or (at.value == 'copyright-page') or (at.value == 'acknowledgement') or (at.value == 'prolog') or (at.value == 'introduction') or (at.value == 'dedication') or (at.value == 'foreword') or (at.value == 'preface') or (at.value == 'print-toc') or (at.value == 'part') or (at.value == 'minor-head') or (at.value == 'bibliography') or (at.value == 'glosary') or (at.value == 'appendix') or (at.value == 'index') or (at.value == 'index-category')):
            lista.append(x)
        elif not x.hasAttribute('class'):
          lista.append(x)
    return lista, listado


  def obtener_arbol(self):
    """
    Método de control  para obtener el árbol del libro
    """
    lista = []
    listado = []
    nodos = self.tree.getElementsByTagName('body')
    tamanyo = len(nodos)
    # Si existe el arbol, se muestra
    if tamanyo >= 1:
      lista, listado = self.obtener_subarbol(nodos, lista, listado)
      self.indice = lista
      self.nodos_libro = listado


  def obtener_capitulos(self):
    """
    Method for the chapters of the book and its position in the list of nodes
    """
    i = 0
    j = 0
    capitulos = []
    pos_capitulos = []
    result = [element for element in self.indice if element.tagName!="h2"]
    while (i < len(self.indice)):
        while(j<len(result)):
            if (self.indice[i].toxml() == result[j].toxml()):
                nombre_capitulo = result[j].childNodes[0].firstChild.toprettyxml()
                capitulos.append(nombre_capitulo)
                pos_capitulos.append(i)
                j = j + 1
            else:
                i = i + 1
        i = i + 1
    return capitulos, pos_capitulos



  def obtener_capitulo(self, pos):
    """
    Method for a particular chapter and its position in the index nodes and the book
    pos: signifies the next or previous chapter
    """
    encontrado = 0
    cambio = 0
    nueva_pos_indice = self.pos_indice
    while (encontrado == 0) and (nueva_pos_indice < len(self.indice)):
      nueva_pos_indice = nueva_pos_indice + pos
      
      if nueva_pos_indice < len(self.indice):
        if self.indice[nueva_pos_indice].hasAttribute('class'):
          clase = self.indice[nueva_pos_indice].attributes['class'].value
          if (clase == 'section' or clase == 'title'):
            encontrado = 1
            cambio = 1
        elif not self.indice[nueva_pos_indice].hasAttribute('class'):
          encontrado = 1
          cambio = 1
    if encontrado == 1:
      id_indice = self.indice[nueva_pos_indice].attributes['id'].value
      encontrado = 0
      i = 0
      while (encontrado == 0) and (i < len(self.nodos_libro)):
        id_nod_libro = self.nodos_libro[i].attributes['id'].value
        if id_indice == id_nod_libro:
          encontrado = 1
          self.pos_sig_indice = self.pos_indice = nueva_pos_indice
          self.pos_sig_nodos_libro = self.pos_nodos_libro = i
        self.pos_audio = 0
        i = i + 1
    return cambio

  def cambiar_pagina(self, pos):
    """
    Method to switch to the previous or next page
    pos: Indicates whether the next or previous page
    """
    encontrado = 0
    cambio = 0
    nueva_pos_nodos_libro = self.pos_nodos_libro
    while (encontrado == 0) and (nueva_pos_nodos_libro > 0) and (nueva_pos_nodos_libro < len(self.nodos_libro)):
      nueva_pos_nodos_libro = nueva_pos_nodos_libro + pos
      if nueva_pos_nodos_libro < len(self.nodos_libro):
        if self.nodos_libro[nueva_pos_nodos_libro].hasAttribute('class'):
          clase = self.nodos_libro[nueva_pos_nodos_libro].attributes['class'].value
          if clase == 'page-normal':
            encontrado = 1
            cambio = 1
    if encontrado == 1:
      self.actualizar_posicion_indice(nueva_pos_nodos_libro)
    return cambio


  def actualizar_posicion_indice(self, nueva_pos_nodos_libro):
    """
    Method to update the index position With respect to the position in the list of nodes in the book
    nueva_pos_nodos_libro : new position in the list of nodes
    """
    encontrado = 0
    i = nueva_pos_nodos_libro
    while (encontrado == 0) and (i > 0):
      i = i - 1
      if self.nodos_libro[i].hasAttribute('class'):
        clase = self.nodos_libro[i].attributes['class'].value
        if (clase == 'title') or (clase == 'jacket') or (clase == 'front') or (clase == 'title-page') or (clase == 'copyright-page') or (clase == 'acknowledgement') or (clase == 'prolog') or (clase == 'introduction') or (clase == 'dedication') or (clase == 'foreword') or (clase == 'preface') or (clase == 'print-toc') or (clase == 'part') or (clase == 'chapter') or (clase == 'section') or (clase == 'sub-section') or (clase == 'minor-head') or (clase == 'bibliography') or (clase == 'glossary') or (clase == 'appendix') or (clase == 'index') or (clase == 'index-category'):
          id_nodos_libro = self.nodos_libro[i].attributes['id'].value
          encontrado = 1
          terminado = 0
          j = len(self.indice)-1
          while (terminado == 0) and (j >= 0):
            id_indice = self.indice[j].attributes['id'].value
            if id_indice == id_nodos_libro:
              self.pos_sig_indice = self.pos_indice = j
              self.pos_sig_nodos_libro = self.pos_nodos_libro = nueva_pos_nodos_libro
              self.pos_audio = 0
              terminado = 1
            if j > 0:
              j = j - 1
      elif not self.nodos_libro[i].hasAttribute('class'):
        id_nodos_libro = self.nodos_libro[i].attributes['id'].value
        encontrado = 1
        terminado = 0
        j = len(self.indice)-1
        while (terminado == 0) and (j >= 0):
          self.m[self.pos_audio][0]
          id_indice = self.indice[j].attributes['id'].value
          if id_indice == id_nodos_libro:
            self.pos_sig_indice = self.pos_indice = j
            self.pos_sig_nodos_libro = self.pos_nodos_libro = nueva_pos_nodos_libro
            self.pos_audio = 0
            terminado = 1
          if j > 0:
            j = j - 1


  def actualizar_pos_nodos_libro(self, nueva_pos_indice):
    """
    Method to update the position in the list of nodes in the book with respect to the index
    nueva_pos_indice : new position in the index
    """
    encontrado = 0
    i = 0
    id_indice = self.indice[nueva_pos_indice].attributes['id'].value
    while (encontrado == 0) and (i < (len(self.nodos_libro)-1)):
      id_nodos_libro = self.nodos_libro[i].attributes['id'].value
      if id_indice == id_nodos_libro:
        self.pos_sig_indice = self.pos_indice = nueva_pos_indice
        self.pos_sig_nodos_libro = self.pos_nodos_libro = i
        self.pos_audio = 0
        self.obtener_pistas(self.nodos_libro[self.pos_nodos_libro])
        encontrado = 1
      i = i + 1

  def establecer_pos_lectura(self, indice_pos, nodos_libro_pos, audio_pos):
    """
    Method for setting the reading position at a particular point in the book
    """
    self.pos_indice = self.pos_sig_indice = indice_pos
    self.pos_nodos_libro = self.pos_sig_nodos_libro = nodos_libro_pos
    self.pos_audio = audio_pos
    self.obtener_pistas(self.nodos_libro[self.pos_nodos_libro])


  def buscar_pagina(self, pagina): #look for page
    """
    Method to locate a particular page
    """
    pagina = int(pagina)
    paginas_totales = self.obtener_numero_paginas()
    paginas_totales = int(paginas_totales)
    i = 0
    encontrado = 0
    cambio = 0 
    if (pagina >= 0) and (pagina <= paginas_totales):
      while (i < len(self.nodos_libro)) and (encontrado == 0):
        if self.nodos_libro[i].hasAttribute('class'):
          clase = self.nodos_libro[i].attributes['class'].value
          if clase == "page-normal":
            numero = self.nodos_libro[i].childNodes[0].firstChild
            if pagina == int(numero.toprettyxml()):
              encontrado = 1
              cambio = 1
              self.actualizar_posicion_indice(i)
        i = i + 1
    return cambio, i


  def obtener_texto(self, pos):
    """
    Method to obtain a block of text to the next or previous position in the list of nodes in the book
    pos : Indicates whether to search the text forward or backward relative to the position in the list of nodes in the book
    """
    encontrado = 0
    cambio = 0
    nueva_pos_nodos_libro = self.pos_nodos_libro
    while (encontrado == 0) and (nueva_pos_nodos_libro > 0) and (nueva_pos_nodos_libro < len(self.nodos_libro)):
      nueva_pos_nodos_libro = nueva_pos_nodos_libro + pos
      if nueva_pos_nodos_libro < len(self.nodos_libro):
        if self.nodos_libro[nueva_pos_nodos_libro].hasAttribute('class'):
          clase = self.nodos_libro[nueva_pos_nodos_libro].attributes['class'].value
          if clase == 'group':
            encontrado = 1
            cambio = 1
    if encontrado == 1:
      self.actualizar_posicion_indice(nueva_pos_nodos_libro)
    return cambio



  def obtener_pista(self):
    """
    Method to extract an audio track , the start position and end positions and update the index nodes of 
    the book and audio
    """
    if self.pos_sig_nodos_libro == (self.pos_nodos_libro + 1):
      self.pos_nodos_libro = self.pos_sig_nodos_libro
    if self.pos_sig_indice == (self.pos_indice + 1):
      self.pos_indice = self.pos_sig_indice
    if self.pos_audio == -1:
      self.pos_audio = 0

    fichero = self.m[self.pos_audio][0]
    pos_ini = self.m[self.pos_audio][1]
    pos_fin = self.m[self.pos_audio][2]
    ind_sig_id = None
    if (self.pos_audio < (len(self.m)-1)) and (self.pos_audio >= 0):
      self.pos_audio = self.pos_audio + 1
    else:
      if self.pos_nodos_libro < (len(self.nodos_libro)-1):
        ind_id = self.indice[self.pos_indice].attributes['id'].value
        nod_id = self.nodos_libro[self.pos_nodos_libro].attributes['id'].value
        try:
          ind_sig_id = self.indice[self.pos_indice+1].attributes['id'].value
        except IndexError:
          pass
        nod_sig_id = self.nodos_libro[self.pos_nodos_libro+1].attributes['id'].value
        if (ind_id == nod_id) or (ind_sig_id == nod_sig_id):
          self.pos_sig_indice = self.pos_sig_indice + 1
        self.pos_sig_nodos_libro = self.pos_sig_nodos_libro + 1
        self.pos_audio = 0
        self.obtener_pistas(self.nodos_libro[self.pos_sig_nodos_libro])
      else:
        self.pos_sig_indice = self.pos_indice = 0
        self.pos_sig_nodos_libro = self.pos_nodos_libro = 0
        self.pos_audio = 0
    return fichero, pos_ini, pos_fin

    
    

  def obtener_pistas(self, nodo): #get_tracks
    """
    Method for audio tracks of a node
    node: node you want to rip audio
    """
    m = []
    self.ruta = self.ruta_libro.split("ncc.html")
    a = nodo.getElementsByTagName('a')
    valor = a[0].attributes['href']
    fichero = valor.value.split("#")
    ruta_completa = self.ruta[0] + fichero[0] #output e.g /home/anes/Documents/Daisy Books/Mahathcharithamaala/012.smil
    #print ruta_completa
    smil = MD.parse(ruta_completa)
    seq = smil.getElementsByTagName('seq')
    par = seq[0].getElementsByTagName('par')
    if len(par) > 0:
      for i in range(len(par)):
        text = par[i].getElementsByTagName('text')
        at = text[0].attributes['id'].value
        if at == fichero[1]:
          audio = par[i].getElementsByTagName('audio')
          for j in range(len(audio)):
            if audio[j].hasAttribute('clip-begin'):
              ruta_audio = self.ruta[0] + audio[j].attributes['src'].value
              l = []
              l.append(ruta_audio)
              inicio = self.obtener_tiempo(audio[j].attributes['clip-begin'].value)
              l.append(inicio)
              fin = self.obtener_tiempo(audio[j].attributes['clip-end'].value)
              l.append(fin)
              m.append(l)
    else:
      audio = seq[0].getElementsByTagName('audio')
      for j in range(len(audio)):
        if audio[j].hasAttribute('clip-begin'):
          ruta_audio = self.ruta[0] + audio[j].attributes['src'].value
          l = []
          l.append(ruta_audio)
          inicio = self.obtener_tiempo(audio[j].attributes['clip-begin'].value)
          l.append(inicio)
          fin = self.obtener_tiempo(audio[j].attributes['clip-end'].value)
          l.append(fin)
          m.append(l)
    #print(m)
    self.m = m


  def obtener_tiempo(self, audio):
    """
    Method for converting a nanosecond time spent in a text string
    audio : text string containing the value of the audio
    """
    aux = audio.split("=")
    tiempo = aux[1].split("s")
    aux = float(tiempo[0]) * 1000000000
    ns = int(aux)
    return ns


  def obtener_inf_libro(self):
    """
    Method for an overview of the book
    """
    l = []
    informacion = ''
    separador = ''
    v = ['ncc:sourceTitle', 'dc:title', 'dc:creator', 'ncc:sourceEdition', 'ncc:sourceDate', 'ncc:sourcePublisher', 'ncc:sourceRights']
    datos = self.tree.getElementsByTagName('meta')
    for i in range(len(v)):
      for x in datos:
        if x.hasAttribute('name'):
          at = x.attributes['name']
          if at.value == v[i]:
            l.append(x.attributes['content'].value)
            l.append("\n")
    informacion = separador.join(l)
    return informacion


  def obtener_inf_traduccion(self):
    """
    Method of obtaining information from the translation of the book
    """
    l = []
    informacion = ''
    separador = ''
    v = ['ncc:sourceTitle', 'dc:title', 'dc:publisher', 'dc:identifier', 'ncc:producer', 'ncc:narrator', 'dc:date', 'dc:format', 'ncc:totalTime', 'ncc:totaltime']
    datos = self.tree.getElementsByTagName('meta')
    for i in range(len(v)):
      for x in datos:
        if x.hasAttribute('name'):
          at = x.attributes['name']
          if at.value == v[i]:
            l.append(x.attributes['content'].value)
            l.append("\n")
    informacion = separador.join(l)
    return informacion


  def obtener_pos_actual_audio(self):
    """
    Method to get the current playback position of the book in seconds
    """
    audio_pos = self.pos_audio
    nodo = self.pos_nodos_libro
    duracion = 0
    i = 0
    while i <= nodo:
      href = self.nodos_libro[i].firstChild.attributes['href'].value
      smil = href.split("#")
      ruta_completa = self.ruta[0] + smil[0]
      fichero = MD.parse(ruta_completa)
      if i < nodo:
        seq = fichero.getElementsByTagName('seq')
        par = seq[0].getElementsByTagName('par')
        j = 0
        for j in range(len(par)):
          text = par[j].getElementsByTagName('text')
          at = text[0].attributes['id'].value
          if at == smil[1]:
            audio = par[j].getElementsByTagName('audio')
            k = 0
            for k in range(len(audio)):
              if audio[k].hasAttribute('clip-begin'):
                inicio = self.obtener_tiempo(audio[k].attributes['clip-begin'].value)
                fin = self.obtener_tiempo(audio[k].attributes['clip-end'].value)
                aux = fin - inicio
                duracion = duracion + aux
              k = k + 1
          j = j + 1 
      elif i == nodo:
        seq = fichero.getElementsByTagName('seq')
        par = seq[0].getElementsByTagName('par')
        j = 0
        for j in range(len(par)):
          text = par[j].getElementsByTagName('text')
          at = text[0].attributes['id'].value
          if at == smil[1]:
            audio = par[j].getElementsByTagName('audio')
            k = 0
            while k < audio_pos:
              if audio[k].hasAttribute('clip-begin'):
                inicio = self.obtener_tiempo(audio[k].attributes['clip-begin'].value)
                fin = self.obtener_tiempo(audio[k].attributes['clip-end'].value)
                aux = fin - inicio
                duracion = duracion + aux
              k = k + 1
            aux = audio[k].attributes['clip-begin'].value
            begin = self.obtener_tiempo(aux)
            aux = begin / 1000000000
            aux = int(aux)
          j = j + 1
      i = i + 1
    segundos = duracion / 1000000000
    return segundos, aux


  def obtener_tiempo_total_audio(self):
    """
    Method for the total recording time of the book
    """
    i = 0
    encontrado = 0
    meta = self.tree.getElementsByTagName('meta')
    while (i < len(meta)) and (encontrado == 0):
      if meta[i].hasAttribute('name'):
        if (meta[i].attributes['name'].value == 'ncc:totalTime') or (meta[i].attributes['name'].value == 'ncc:totaltime'):
          tiempo_total = meta[i].attributes['content'].value
          encontrado = 1
      i = i + 1
    aux = tiempo_total.split(":")
    tiempo_total = int(aux[0]) * 3600
    tiempo_total = tiempo_total + int(aux[1]) * 60
    tiempo_total = tiempo_total + int(aux[2])
    return float(tiempo_total)


  def establecer_formato_hora(self, time_int):
    """
    Conventir method for the second hour format "hh : mm : ss "
    """
    time_str = ""
    time_int = int(time_int)
    if time_int >= 3600:
      _hours = time_int / 3600
      time_int = time_int - (_hours * 3600)
      time_str = str(_hours) + ":"
    if time_int >= 600:
      _mins = time_int / 60
      time_int = time_int - (_mins * 60)
      time_str = time_str + str(_mins) + ":"
    elif time_int >= 60:
      _mins = time_int /60
      time_int = time_int - (_mins * 60)
      time_str = time_str + "0" + str(_mins) + ":"
    else:
      time_str = time_str + "00:"
    if time_int > 9:
      time_str = time_str + str(time_int)
    else:
      time_str = time_str + "0" + str(time_int)
    return time_str
