# -*- coding: iso-8859-15 -*-


import pygtk
pygtk.require('2.0')
import gtk
import os,sys
import libro
import time,re
from xml.dom.minidom import parse

from dbr_i18n import _          #For i18n support


# Comprobacion la version de pygtk
if gtk.pygtk_version < (2,3,90):
  print "PyGtk 2.3.90 or later required for this example"
  raise SystemExit


class Controlador:
  """
  Class Driver for control between the view class and the book , DVD and Registration class
  """ 

  def setVista(self, v):
    self.v = v


  def __init__(self, r, reg):
    """
    Start a controller object for GestiÃ³n interface callbacks
    r : a player object
    reg : a Record object
    """
    self.r = r
    self.l = None
    self.reg = reg
    

  def obtener_configuracion(self):
    """
    MÃ © all for the configuration of the DBR . If this is the first time the application is run, 
    iniciarÃ¡ the creation of the configuration file
    """
    lista_indice = []
    registro = self.reg.obtener_configuracion()
    if registro[0] != None:
      if os.path.exists(registro[1]):
        self.l = libro.Libro(registro[1], (registro[2]), (registro[3]), registro[4])
        if registro[0] == self.l.obtener_nombre():
          lista_indice = self.l.obtener_indice()
        else:
          self.l = None
      else:
        self.l = None
    else:
      pass
    return lista_indice, registro[2]


  def destroy(self, widget):
    """
    MÃ © everything to destroy a window
    """
    
    return True

  def destroy_dialogo(self):
    """
    MÃ © everything to destroy a window
    """
    #gtk.main_quit() # close all window...
    #print(gtk.RESPONSE_DELETE_EVENT)
    
    return True


  def carga_fichero_inicial(self):
    """
    MÃ © All to play the last book played to load the DBR
    """
    fichero, pos_ini, pos_fin = self.l.obtener_pista()
    self.r.reproducir(fichero, pos_ini, pos_fin)


  def cargaFichero(self, w, data):
    """
    MÃ © everything to load the file containing the index of the book
    """
    # Creating a new control file selection
    seleccion = gtk.FileChooserDialog(_("Open book"), None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    seleccion.set_default_response(gtk.RESPONSE_OK)

    # filter to display only files called ncc.html
    filtro = gtk.FileFilter()
    path = os.path.abspath("ncc")
    seleccion.set_filename(path)
    # allowed for the file extension
    filtro.add_pattern("*.html")
    seleccion.add_filter(filtro)

    response = seleccion.run()
    if response == gtk.RESPONSE_OK:
      try:
        # The book is loaded
        nombre = seleccion.get_filename()
        # print "name is: "+nombre --/home/anes/Documents/Daisy Books/124. Njanmalala/ncc.html
        dom = parse(nombre)
        name = dom.getElementsByTagName('title')
        exact_name = name[0].firstChild.nodeValue
        #print exact_name
        with open(os.path.expanduser("~/.recent_books"), 'a+') as f:
          f.write(exact_name+'--'+nombre+'\n')
        self.l = libro.Libro(nombre)
      except IOError:
        self.mostrar_mensaje(_("Failed to open"), _(" The book can not be opened"))
    elif response == gtk.RESPONSE_CANCEL:
      self.mostrar_mensaje(_("Cancelled selection"), _("No book has been selected"))
    seleccion.destroy()
    indice = self.l.obtener_indice()
    if len(indice) > 1:
      return indice


  def buscar_libro_callback(self, w, data): #Find Book (Which already added in Bookmark) ..
    """
    MÃ © primarily to control the search of books stored in the configuration file
    """
    reproducir = False
    if self.r.obtener_estado() == "Reproduciendo":
      reproducir = True
      self.r.reproducir_pausar()
    libros = self.reg.buscar_libros()
    # print libros 
    ''' [[u'Njan Malala', '/home/anes/Documents/Daisy Books/124. Njanmalala/ncc.html'], [u'Mahathcharithamala', '/home/anes/Documents/Daisy Books/Mahathcharithamaala/ncc.html']'''
    if libros != []:
      nombre_libros = []
      for i in range(len(libros)):
        nombre_libros.append(libros[i][0])
      indice_libro = self.mostrar_combobox(_("Find books"), _("Choose the book which you want to open"), nombre_libros)
      if indice_libro != None:
        l_aux = libro.Libro(libros[indice_libro][1])
        if l_aux.obtener_nombre() == libros[indice_libro][0]:
          self.r.detener()
          self.v.limpiar_modelo()
          self.l = l_aux
          self.v.mostrar_libro(self.l.obtener_indice())
          self.sinc_vista_audio()
        else:
          self.mostrar_mensaje(_("Warning"), _("Specified book doesn't match with the book currently in that path"))
      else:
        self.mostrar_mensaje("Warning", _("You have not selected any book"))
    else:
      self.mostrar_mensaje(_("Warning"), _("There are no saved books"))
    if (self.r.obtener_estado() == "Pausado") and reproducir:
      self.r.reproducir_pausar()

  def recent_books_callback(self, w, data): #Recent Books (Which saved in .recent_books in Home folder) ..
    """
    MÃ © primarily to show the recent books stored in the configuration file(.recent_books)
    """
    reproducir = False
    if self.r.obtener_estado() == "Reproduciendo":
      reproducir = True
      self.r.reproducir_pausar()
    libros = self.reg.recent_books()
    if libros != [] and libros is not None and len(libros) !=0 :
      libros = zip(libros[::2], libros[1::2])
    '''libros = [[u'Njan Malala', '/home/anes/Documents/Daisy Books/124. Njanmalala/ncc.html'], [u'Aalahayuday Penmakkal', '/home/anes/Documents/Daisy Books/95. Alahayuday Penmakkal/ncc.html']]'''
    #print libros
    if libros != [] and libros is not None and len(libros) !=0 :
      nombre_libros = []
      for i in range(len(libros)):
        nombre_libros.append(libros[i][0])
      indice_libro = self.mostrar_combobox(_("Find books"), _("Choose the book which you want to open"), nombre_libros)
      if indice_libro != None:
        l_aux = libro.Libro(libros[indice_libro][1])
        if l_aux.obtener_nombre() == libros[indice_libro][0]:
          self.r.detener()
          self.v.limpiar_modelo()
          self.l = l_aux
          self.v.mostrar_libro(self.l.obtener_indice())
          self.sinc_vista_audio()
        else:
          self.mostrar_mensaje(_("Warning"), _("Specified book doesn't match with the book currently in that path"))
      else:
        self.mostrar_mensaje("Warning", _("You have not selected any book"))
    else:
      self.mostrar_mensaje(_("Warning"), _("There are no recent books"))
    if (self.r.obtener_estado() == "Pausado") and reproducir:
      self.r.reproducir_pausar()


  def cerrar_libro_callback(self, w, data):
    """
    MÃ © primarily to control the closing of a book
    """
    if self.comprobar_libro():
      self.r.detener()
      self.l = None
      self.v.limpiar_modelo()


  def cerrar_aplicacion(self):
    """
    MÃ © all that closes the application and saves the reading position and the configuration of the player
    """
    if self.comprobar_libro():
      self.r.detener()
      registro = self.l.obtener_datos_para_marca()
      volumen = self.r.obtener_volumen()
      registro.append(volumen)
      self.reg.escribir_configuracion(registro)


  def mostrar_inf_libro_callback(self, w, data):
    """
    MÃ © All to display general information book
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      info = self.l.obtener_inf_libro()
      self.mostrar_mensaje(_("Book information"), info)
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def mostrar_inf_traduccion_callback(self, w, data):
    """
    MÃ © All to display information from the book traducciÃ³n
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      info = self.l.obtener_inf_traduccion()
      self.mostrar_mensaje(_("Book translation information"), info)
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def mostrar_pos_actual_callback(self, w, data):
    """
   MÃ © All to show laposiciÃ³n current reading in the format " hh : mm : ss "
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      pos = self.r.obtener_ins_actual()
      pos = pos / 1000000000
      segundos, aux = self.l.obtener_pos_actual_audio()
      t = segundos +(pos - aux)
      hora = self.l.establecer_formato_hora(t)
      self.mostrar_mensaje(_("Elapsed playback time"), hora)
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def mostrar_tiempo_total_callback(self, w, data):
    """
    MÃ © All to display the total playing time of the book
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      tiempo = self.l.obtener_tiempo_total_audio()
      hora = self.l.establecer_formato_hora(tiempo)
      self.mostrar_mensaje(_("Total book's playback time"), hora)
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("Tehre are currently no playing book"))


  def sinc_vista_audio(self):
    """
    MÃ © All to synchronize the view of the index of the book with the audio playback when the program automatically 
    advances the reproduction of the book or when the user clicks a choice of menu navigation
    """
    
    #self.v.slider.adj2.configure(1, 0, 100, 1, 1, 0)
    #self.v.test()
    self.v.actualizar_vista(self.l.obtener_pos_indice()) #toupdate_vista (user view )
    fichero, pos_ini, pos_fin = self.l.obtener_pista() #get_clue
    self.r.reproducir(fichero, pos_ini, pos_fin)
    
  def sinc_vista_audio_skip_reverse(self):
    """
    MÃ © All to synchronize the view of the index of the book with the audio playback when the program 
    advance back when clicking reverse skip option
    """
    if self.comprobar_libro():
      cambio = self.l.cambiar_pagina(-1)
      if cambio == 1:
        self.r.detener()
        self.l.obtener_pistas(self.l.obtener_nodo_actual())
        self.sinc_vista_audio()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))

  def sinc_audio_vista(self, indice_pos):
    """
   MÃ © All to synchronize the audio with the view of the index when the user clicks a scroll key or 
   when you click with the mouse
    """
    #print indice_pos
    self.r.detener()
    try:
      self.l.actualizar_pos_nodos_libro(indice_pos)
    except AttributeError as e:
      return 
    fichero, pos_ini, pos_fin = self.l.obtener_pista()
    self.r.reproducir(fichero, pos_ini, pos_fin)



  def detener_callback(self, w, data):
    """
    MÃ © primarily to control the arrest in playback , checking if there is a book full
    """
    if self.comprobar_libro():
      self.r.detener()
      self.l.establecer_pos_lectura(0, 0, 0)
      self.sinc_vista_audio()
      if self.r.obtener_estado() == "Reproduciendo":
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def comprobar_libro(self): #check_book
    """
    MÃ © everything checks for any book loaded
    """
    if self.l == None:
      return False
    else:
      return True


  def control_estado_callback(self, w, data):
    """
    MÃ © primarily to control the change of status of the player
    """
    #self.v.toggle.connect("toggled", self.v.play)
    #self.v.toggle.connect("expose-event", self.v.draw_play_toggle)
    #print self.v.toggle.get_active()
    #print self.r.estado
    #print self.r.obtener_estado()
    '''if(self.v.toggle.get_active()):
      self.v.toggle.set_active(False)
    else:
      self.v.toggle.set_active(True)'''
    '''vv = self.v.toggle.get_active()
    vs = not vv
    self.v.toggle.set_active(vs)'''
    if self.comprobar_libro():
      self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))

  def change_toggle_status(self,status):
    """
    To change the toggle status for play/pause
    """
    if(status == "pause"):
      self.v.toggle.set_active(True)
    else:
      self.v.toggle.set_active(False)
    
      
  def forward_play(self):
    """
    MÃ © to forward current playing mp3
    """
    self.r.forward_final()
    
  def backward_play(self):
    """
    MÃ © to reverse current playing mp3
    """
    self.r.reverse_final()


  def listar_capitulos_callback(self, w, data):
    """
    MÃ © primarily to control the presentation of chapters and display
    """
    reproducir = False
    if self.comprobar_libro(): #check_book is loaded there or not...
      if self.r.obtener_estado() == "Reproduciendo": #Reproduciendo = playing
        reproducir = True
        self.r.reproducir_pausar() #pausar = pause
        
      capitulos, pos_capitulos = self.l.obtener_capitulos()
      if capitulos != []:
        pos_capitulo = self.mostrar_combobox(_("Go to chapter"), _("Select which chapter do you want to go"), capitulos)
        #print "pos_capitulo is: "
        #print pos_capitulo
        if pos_capitulo != None:
          self.r.detener()
          self.l.actualizar_pos_nodos_libro(pos_capitulos[pos_capitulo])
          self.sinc_vista_audio()
        else:
          self.mostrar_mensaje(_("Warning"), _("You have not selected any chapter"))
      else:
        self.mostrar_mensaje(_("Error"), _("Don't exist any chapter in the book"))
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))

  def listar_capitulos_by_nombre_callback(self, w, data):
    """
    MÃ © primarily to select a chapter by chapter number
    """
    reproducir = False
    if self.comprobar_libro(): #check_book is loaded there or not...
      if self.r.obtener_estado() == "Reproduciendo": #Reproduciendo = playing
        reproducir = True
        self.r.reproducir_pausar() #pausar = pause
        
      capitulos, pos_capitulos = self.l.obtener_capitulos()
      if capitulos != []:
        chapter = self.mostrar_entrada_texto(_("Go to chapter"), _("Enter the chapter no which you want to go"), 10)
        if chapter.isdigit():
          chapter = int(chapter) - 1
          capitulos,pos_capitulos = self.l.obtener_capitulos()
          str1 = ''.join(capitulos)
          length = len(re.findall('(?=\n)', str1))
          if length >= chapter:
            self.r.detener()
            self.l.actualizar_pos_nodos_libro(pos_capitulos[chapter])
            self.sinc_vista_audio()
          else:
            self.mostrar_mensaje(_("Warning"), _("There is no chapter as given number"))
        else:
          self.mostrar_mensaje(_("Error"), _("Please give a number as chapter"))
      else:
        self.mostrar_mensaje(_("Warning"), _("There is no chapter in the currently playing book"))
    if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def ir_cap_sig_callback(self, w, data):
    """
    MÃ © all to the next chapter
    """
    pos_change = self.l.obtener_nodo_distance("forward")    
    if self.comprobar_libro(): #check_book
      cambio = self.l.obtener_capitulo(pos_change) # cambio = change, capitulo = chapter
      #cambio = 1
      #print "cambio is: "
      #print cambio
      if cambio == 1:
        self.r.detener()
        self.l.obtener_pistas(self.l.obtener_nodo_actual()) # get_tracks from libro.py line 388
        self.sinc_vista_audio()
    else:
      self.m.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def ir_cap_ant_callback(self, w, data):
    """
    MÃ©todo para ir al capÃ­tulo anterior
    """
    pos_change = self.l.obtener_nodo_distance("backword")
    if self.comprobar_libro():
      cambio = self.l.obtener_capitulo(-pos_change)
      if cambio == 1:
        self.r.detener()
        self.l.obtener_pistas(self.l.obtener_nodo_actual())
        self.sinc_vista_audio()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def ir_pag_sig_callback(self, w, data): # to find out next page
    """
    MÃ © all to control the passage to the next page specified by the user
    """
    if self.comprobar_libro():
      cambio = self.l.cambiar_pagina(1)
      if cambio == 1:
        self.r.detener()
        self.l.obtener_pistas(self.l.obtener_nodo_actual())
        self.sinc_vista_audio()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def ir_pag_ant_callback(self, w, data):
    """
    MÃ© primarily to control the change to the previous page specified by the user
    """
    if self.comprobar_libro():
      cambio = self.l.cambiar_pagina(-1)
      if cambio == 1:
        self.r.detener()
        self.l.obtener_pistas(self.l.obtener_nodo_actual())
        self.sinc_vista_audio()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def ir_texto_ant_callback(self, w, data): # previous paragraph navigation ...
    """
    MÃ © primarily to control the change to block previous text specified by the user
    """
    if self.comprobar_libro():
      cambio = self.l.obtener_texto(-1)
      if cambio == 1:
        self.r.detener()
        self.l.obtener_pistas(self.l.obtener_nodo_actual())
        self.sinc_vista_audio()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def ir_texto_sig_callback(self, w, data):
    """
    MÃ © all to control the passage to the next block of text entered by the user
    """
    if self.comprobar_libro():
      cambio = self.l.obtener_texto(1)
      #print cambio
      if cambio == 1:
        self.r.detener()
        self.l.obtener_pistas(self.l.obtener_nodo_actual())
        self.sinc_vista_audio()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))

  def ir_a_pagina_callback(self, w, data): #goto page
    """
    MÃ © primarily to control the search for a page specified by the user
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo": #playing = Reproduciendo
        reproducir = True
        self.r.reproducir_pausar() #stop current playing file
      pagina = self.mostrar_entrada_texto(_("Go to page"), _("Enter the page which you want to go"), 10)
      if pagina.isdigit():
        pagina = int(pagina)
        cambio, pos = self.l.buscar_pagina(pagina)
        if cambio == 1:
          self.r.detener()
          self.l.obtener_pistas(self.l.nodos_libro[pos])
          self.sinc_vista_audio()
        else:
          self.mostrar_mensaje(_("Warning"), _("Page out of range"))
      else:
        self.mostrar_mensaje(_("Error"), _("You have not entered a number"))
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def control_aumento_volumen_callback(self, w, data):
    """
    MÃ©primarily to control the increase in volume indicated by the user
    """
    if self.comprobar_libro():
      self.r.cambiar_volumen(1)
      current_volume = self.current_volume()
      self.v.adj2.configure(current_volume, 0, 10, 1, 1, 0)
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def control_disminucion_volumen_callback(self, w, data):
    """
    MÃ©to decrease the volume of play....
    """
    if self.comprobar_libro():
      self.r.cambiar_volumen(-1)
      current_volume = self.current_volume()
      self.v.adj2.configure(current_volume, 0, 10, 1, 1, 0)
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))
      
  def change_volume(self, adj):
    """
    MÃ©todo increase/decrese volume through slider
    """
    if self.comprobar_libro():
        self.r.cambiar_volumen(adj.value)
    else:
        self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))

  def activar_desactivar_sonido_callback(self, w, data):
    """
    MÃ©todo para controlar la activaciÃ³n o desactivaciÃ³n del sonido
    """
    if self.comprobar_libro():
      self.r.silenciar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def establecer_marca_callback(self, w, data):
    """
    MÃ © primarily to control the creation of a mark in the book playback
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      nombre_marca = self.mostrar_entrada_texto(_("Set bookmark"), _("Enter the bookmark name"), 50)
      if nombre_marca != '':
        marca = self.l.obtener_datos_para_marca() # take book details including path...
        marca.append(nombre_marca)
        self.reg.crear_marca(marca)
      else:
        self.mostrar_mensaje(_("Error"), _("You have not entered a bookmark name"))
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def listar_marcas_callback(self, w, data):
    """
    MÃ © all manufacturers to list a book
    """
    reproducir = False
    if self.comprobar_libro():
      nombre_libro = self.l.obtener_nombre()
      marcas = self.reg.obtener_marcas_libro_actual(nombre_libro)
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      if marcas != []:
        nombre_marcas = []
        for i in range(len(marcas)):
          nombre_marcas.append(marcas[i][0])
        indice_marca = self.mostrar_combobox(_("Bookmark list"), _("Choose the bookmark which you want to go"), nombre_marcas)
        if indice_marca != None:
          self.r.detener()
          self.l.establecer_pos_lectura(marcas[indice_marca][1], marcas[indice_marca][2], marcas[indice_marca][3])
          self.sinc_vista_audio()
        else:
          self.mostrar_mensaje(_("Warning"), _("You have not selected any bookmark"))
      else:
        self.mostrar_mensaje(_("Warning"), _("There are not bookmarks for this book"))
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def borrado_de_marcas_callback(self, w, data):
    """
    MÃ © primarily to control erasing a mark of book reproduction specified by the user
    """
    reproducir = False
    if self.comprobar_libro():
      nombre_libro = self.l.obtener_nombre()
      marcas = self.reg.obtener_marcas_libro_actual(nombre_libro)
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
      if marcas != []:
        nombre_marcas = []
        for i in range(len(marcas)):
          nombre_marcas.append(marcas[i][0])
        indice_marca = self.mostrar_combobox(_("Bookmarks deletion"), _("Choose the bookmark which you want to delete"), nombre_marcas)
        if indice_marca != None:
          self.reg.borrar_marca(nombre_libro, indice_marca)
        else:
          self.mostrar_mensaje(_("Warning"), _("You have not selected any bookmark"))
      else:
        self.mostrar_mensaje(_("Warning"), _("Don't exist bookmarks for this book"))
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()
    else:
      self.mostrar_mensaje(_("Warning"), _("There are currently no playing book"))


  def mostrar_mensaje(self, titulo, mensaje):
    """
    MÃ © All to display a message
    title : title of the message
    message : message to be displayed
    """
    # Creating a dialog
    ventana_mensaje = gtk.Dialog(titulo, None, 0, (gtk.STOCK_OK, gtk.RESPONSE_OK))

    # creating a label with the error message
    ventana_mensaje.etiqueta = gtk.Label(mensaje)
    ventana_mensaje.vbox.pack_start(ventana_mensaje.etiqueta, True, True, 0)
    ventana_mensaje.etiqueta.show()
    response = ventana_mensaje.run()
    ventana_mensaje.destroy()

  def entry_activated_cb(self,dialogo):
    def callback(widget):
      dialogo.response(gtk.RESPONSE_OK)
      return True
    return callback

  def mostrar_entrada_texto(self, titulo, texto_etiqueta, longitud):
    """
    MÃ © All to display a text input and get the text entered by the user
    title : title of the dialog window
    texto_etiqueta : label text
    length: ± or maximum size of the text entry
    """
    
    dialogo = gtk.Dialog(titulo, None, 0, (gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    '''etiqueta = gtk.Label(texto_etiqueta)
    etiqueta.show()
    dialogo.vbox.pack_start(etiqueta)
    entrada = gtk.Entry()
    entrada.set_max_length(longitud)
    entrada.select_region(0, len(entrada.get_text()))
    entrada.show()
    dialogo.vbox.pack_start(entrada, False)
    response = dialogo.run()'''
    entry = gtk.Entry()
    entry.connect("activate", self.entry_activated_cb(dialogo))
    action_area = dialogo.get_content_area()
    action_area.pack_start(entry)

    dialogo.show_all()
    response = dialogo.run()
    if response == gtk.RESPONSE_OK:
      texto = entry.get_text()
    else:
      texto = ''
    dialogo.destroy()
    return texto




  def mostrar_combobox(self, titulo, texto_etiqueta, lista):
    """
    MÃ © All to show a combobox on screen and get the option chosen
    """
    #dialogo = gtk.Dialog(titulo, None, 0, (gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    #dialogo = gtk.Dialog(titulo, None,  gtk.DIALOG_MODAL, None)
    self.dialogo = gtk.Dialog("Go to Chapter/Bookmark", None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)) 
    etiqueta = gtk.Label(texto_etiqueta)
    etiqueta.show()
    self.dialogo.vbox.pack_start(etiqueta)
    combobox = gtk.combo_box_new_text()
    for x in lista:
      combobox.append_text(x)
    combobox.connect('changed', self.changed_cb)
    #combobox.set_active(0)
    
    self.dialogo.vbox.pack_start(combobox, False)
    combobox.show()
    response = self.dialogo.run()
    print response
    self.dialogo.hide()
    if (response!= -2):
      elemento_activo = combobox.get_active()
      return elemento_activo

 
  def changed_cb(self, combobox):
    #model = combobox.get_model()
    index = combobox.get_active()
    #self.dialogo.destroy()
    #response = self.dialogo.run()
    if index > -1:
      #print index
      self.dialogo.response(gtk.RESPONSE_ACCEPT)


  def mostrar_ayuda_callback(self, w, data):
    """
    MÃ © All to display the help file of DBR
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
    if os.path.exists("docs/help.html"): #ayuda.html
      os.system("firefox docs/help.html")
    else:
      self.mostrar_mensaje(_("Warning!"), _("The help file can not be found"))
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()


  def close_about_dialog_callback(self, w, data):
    #reproducir = False
    reproducir = True
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()

    if data==gtk.RESPONSE_CANCEL:
      w.destroy()

  def display_about_dialog_callback(self, w, data):
    """
    This method is used for displaying "About Daisy Book Reader" notice
    """
    reproducir = False
    if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
    program_name="Daisy Book Reader"
    authors=['Muhammad Shameer S, Anes P A', \
            'Sreelakshmi R.V']
    #translations=_("This program has been translated by:\n\nJuan C. BuÃ±o\n")
    license=_("This program is under GNU/General Public License version 3. This program is free software: you can \n redistribute it and/or modify it under the terms of the GNU General Public License as published \n by the Free Software Foundation, either version 3 of the License, or (at your\n option) any later version.\n This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without \n even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the \n GNU General Public License for more details. You should have received a copy of the GNU General Public License \n along with this program.  If not, see <http://www.gnu.org/licenses/>.You can also contact with the author of \n the program at <info@insight.org.in>.") 
    #version="0.1.1"
    version = "1.0"
    copyright="Copyright 2015 Insight"
    #website="http://dbr.sourceforge.net"

    ADlg=gtk.AboutDialog()
    ADlg.set_program_name(program_name)
    ADlg.set_version(version)
    ADlg.set_copyright(copyright)
    ADlg.set_authors(authors)
    #ADlg.set_translator_credits(translations)
    ADlg.set_license(license)
    #ADlg.set_website(website)

    ADlg.connect("response", self.close_about_dialog_callback)
    ADlg.show()


  def mostrar_licencia_callback(self, w, data):
    """
    MÃ © All to show the license to use the DBR
    """
    reproducir = False
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Reproduciendo":
        reproducir = True
        self.r.reproducir_pausar()
    if os.path.exists("docs/licence.html"):
      os.system("firefox docs/licence.html")
    else:
      self.mostrar_mensaje(_("Warning!"), _("The help file can not be found"))
    if self.comprobar_libro():
      if self.r.obtener_estado() == "Pausado" and reproducir:
        self.r.reproducir_pausar()

  def current_volume(self):
    """
    MÃ©todo to take current volume for vista(view)...
    """
    return self.r.obtener_volumen()
    #return self.r.get_by_name("volume").get_property("volume")

