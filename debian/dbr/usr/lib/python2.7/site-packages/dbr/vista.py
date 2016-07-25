# -*- coding: iso-8859-15 -*-

import pygtk
pygtk.require('2.0')
import gtk
import controlador, libro, reproductor
import xml.dom.minidom as MD
import time
import math,pango,cairo
import pangocairo
from cStringIO import StringIO
import sys,os
from dbr_i18n import _          #For i18n support

class Vista:
  """
  Class creation interface view for the DBR
  """



  def ventanaNueva(self):
    """
    Method to create the main window of DBR
    """
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.connect("destroy", self.destruir_aplicacion)
    window.connect("key-press-event", self.key_press_event_toggle)
    #window.connect("delete-event", gtk.main_quit) #added 
    window.set_title("Insight Daisy Book Reader")
    window.set_border_width(1)
    #window.set_default_size(1280, 1024)
    window.set_default_size(780, 545)
    return window

  def menuPrincipal(self, ventana):
    """
    Method for creating the main menu bar
    """
    accel_group = gtk.AccelGroup()
    # Initialization ItemFactory.
    # Parameter 1: Type menu.
    # Parameter 2: Route menu.
    # Parameter 3: A reference to accelgroup.
    item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)

    # Generating menu items .
    item_factory.create_items(self.menu_items)
    # accelgroup group includes the window.
    ventana.add_accel_group(accel_group)

    # a reference to item_factory is needed to prevent its destruction
    self.item_factory = item_factory
    # bar menu created is returned.
    return item_factory.get_widget("<main>")


  def __init__(self, controlador):
    """
    __init__ method of the View class
    """
    self.c = controlador
    self.c.setVista(self)

    self.menu_items = (
      ( _("/_File"), "<alt>F", None, 0, "<Branch>"),
      (_("/File/_Open book"), "<control>O", self.inicio_cargaFichero_callback, 0, None),
      (_("/File/_Find book"), "<control>F", self.c.buscar_libro_callback, 0, None),
      (_("/File/_Close book"), "<control>F4", self.c.cerrar_libro_callback, 0, None),
      (_("/File/_Quit"), "<control>Q", self.cerrar_aplicacion, 0, None),

      (_("/_Controls"), "<alt>C", None, 0, "<Branch>"),
      #(_("/Controls/_Play-Pause"), "<control>space", self.c.control_estado_callback, 0, None),
      #(_("/Controls/_Play-Pause"), "space", self.c.control_estado_callback, 0, None),
      (_("/Controls/_Mute(Unmute)"), "<control>M", self.c.activar_desactivar_sonido_callback, 0, None),
      (_("/Controls/_Stop"), "<control>S", self.c.detener_callback, 0, None),
      

      (_("/Controls/_Volume"), "<alt>V", None, 0, "<Branch>"),
      #(_("/Controls/Volume/Increase volume"), "<control>V", self.c.control_aumento_volumen_callback, 0, None),
      (_("/Controls/Volume/Increase volume"), "<control>Up", self.c.control_aumento_volumen_callback, 0, None),
      #(_("/Controls/Volume/Decrease volume"), "<control><shift>V", self.c.control_disminucion_volumen_callback, 0, None),
      (_("/Controls/Volume/Decrease volume"), "<control>Down", self.c.control_disminucion_volumen_callback, 0, None),

      (_("/_Navigation"), "<alt>N", None, 0, "<Branch>"),
      #(_("/Navigation/Previous chapter"), "<control><shift>L", self.c.ir_cap_ant_callback, 0, None),
      (_("/Navigation/Previous heading"), "<control><shift>H", self.c.ir_cap_ant_callback, 0, None),
      #(_("/Navigation/Next chapter"), "<control>L", self.c.ir_cap_sig_callback, 0, None),
      (_("/Navigation/Next heading"), "<control>H", self.c.ir_cap_sig_callback, 0, None),
      #(_("/Navigation/Previous page"), "<control><shift>N", self.c.ir_pag_ant_callback, 0, None),
      #(_("/Navigation/Previous page"), "<control><shift>P", self.c.ir_pag_ant_callback, 0, None),
      (_("/Navigation/Previous page"), "<control>Left", self.c.ir_pag_ant_callback, 0, None),
      #(_("/Navigation/Next page"), "<control>N", self.c.ir_pag_sig_callback, 0, None),
      #(_("/Navigation/Next page"), "<control>P", self.c.ir_pag_sig_callback, 0, None),
      (_("/Navigation/Next page"), "<control>Right", self.c.ir_pag_sig_callback, 0, None),
      (_("/Navigation/Previous paragraph"), "<control><shift>P", self.c.ir_texto_ant_callback, 0, None),
      (_("/Navigation/Next paragraph"), "<control>P", self.c.ir_texto_sig_callback, 0, None),
      (_("/_GoTo"), "<control>G", None, 0, "<Branch>"),
      (_("/GoTo/Chapter"), None, self.c.listar_capitulos_callback, 0, None),
      (_("/GoTo/Page"), "<control>G", self.c.ir_a_pagina_callback, 0, None),
      (_("/GoTo/Recent Books"), None, self.c.recent_books_callback, 0, None),
      (_("/GoTo/Chapter by Number"), None, self.c.listar_capitulos_by_nombre_callback, 0, None),
      (_("/_Bookmarks"), "<alt>B", None, 0, "<Branch>"),
      (_("/Bookmarks/_Set bookmark"), "<control>K", self.c.establecer_marca_callback, 0, None),
      (_("/Bookmarks/_Delete bookmarks"), "<control>D", self.c.borrado_de_marcas_callback, 0, None),
      (_("/Bookmarks/_List bookmarks"), "<control>B", self.c.listar_marcas_callback, 0, None),
      (_("/_Info"), "<alt>I", None, 0, "<Branch>"),
      (_("/Info/_Book info"), "<control>O", self.c.mostrar_inf_libro_callback, 0, None),
      (_("/Info/Book _translation information"), "<control>N", self.c.mostrar_inf_traduccion_callback, 0, None),
      (_("/Info/Playback _duration"), "<control>X", self.c.mostrar_pos_actual_callback, 0, None),
      (_("/Info/Total play _duration"), "<control>W", self.c.mostrar_tiempo_total_callback, 0, None),
      (_("/_Help"), "<alt>H", None, 0, "<Branch>"),
      #(_("/Help/_User help"), "<control>u", self.c.mostrar_ayuda_callback, 0, None),
      (_("/Help/_About DBR"), "<control>Y", self.c.display_about_dialog_callback, 0, None),
      #(_("/Help/_License"), "<control>J", self.c.mostrar_licencia_callback, 0, None)
      )

    self.ventana = self.ventanaNueva()


    caja_principal = gtk.VBox(False, 1)
    caja_principal.set_border_width(1)
    caja_principal.show()

    barraMenu = self.menuPrincipal(self.ventana)

    caja_principal.pack_start(barraMenu, False, True, 0)
    barraMenu.show()
    # Take Python version
    self.version = "python"+str(sys.version_info.major)+"."+str(sys.version_info.minor)
    pixbuf = self.draw_icon()
    #self.set_icon(pixbuf)
    image = gtk.Image()
    image.set_from_pixbuf(pixbuf)
  
    #take current volume
    
    self.volume = self.c.current_volume()
    self.adj2 = gtk.Adjustment(self.volume, 0, 10, 1, 1, 0)
    self.adj2.connect("value_changed", self.c.change_volume)
    self.slider =  gtk.HScale(self.adj2)
    
    self.slider.set_value_pos(gtk.POS_LEFT)

    self.slider.set_size_request(160, 50)
    
    #caja_principal.pack_start(self.slider, False, False, 0)
    self.table = gtk.Table(rows=1, columns=2, homogeneous=False)
    self.table.set_col_spacings(12)
    self.table.set_size_request(110, 80)
    self.table.attach(image, 0, 1, 0, 1, xoptions=gtk.FILL, yoptions=0)
    self.table.attach(self.slider, 1, 2, 0, 1, xoptions=gtk.EXPAND|gtk.FILL, yoptions=0)
    
    #self.table.attach_defaults(self.slider, 2, 3, 5, 6)
    caja_principal.pack_start(self.table, True, True, 0)
    self.table.show()
    
    # Add play/pause toggle button
    self.toggle = gtk.ToggleButton(label=None, use_underline=False)
    self.toggle.set_size_request(333, 80)
    self.toggle.set_app_paintable(True)
    self.toggle.connect("expose-event", self.draw_play_toggle)
    self.toggle.connect("toggled", self.play)
    caja_principal.pack_start(self.toggle, False, True, 0)
    #self.toggle.show()

    # Create a TreeStore with a text column .
    self.treestore = gtk.TreeStore(str)

    # Creating the TreeView using treestore
    self.treeview = gtk.TreeView(self.treestore)

    
    lista, posicion_indice = self.c.obtener_configuracion()
    # Creation of TreeViewColumn to display data
    if len(lista) == 0 :
      self.tvcolumn = gtk.TreeViewColumn('Welcome to Daisy Book Reader application')
    # Add the column to treeview
    else:
      self.tvcolumn = gtk.TreeViewColumn("Book contents")
    self.treeview.append_column(self.tvcolumn)
    # create a CellRendererText to display data
    self.cell = gtk.CellRendererText()

    # Add the cell to expand and allow vcolumn
    self.tvcolumn.pack_start(self.cell, True)

    # Include the "text " attribute of the cell column 0 - to return the text
    # from the column in the tree.
    self.tvcolumn.add_attribute(self.cell, 'text', 0)
    
    # do searchable
    self.treeview.set_search_column(0)
    self.treeselection = self.treeview.get_selection()
    

    self.cursor_cambiado = self.treeview.connect("cursor-changed", self.actualizar_audio)
    self.treeview.connect('key-press-event' , self.key_press_event)
    
    ventana_libro = gtk.ScrolledWindow()
    ventana_libro.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    ventana_libro.show()
    ventana_libro.add_with_viewport(self.treeview)
    self.treeview.show_all()
    caja_general = gtk.VBox(False, 1)
    caja_general.set_border_width(1)
    self.ventana.add(caja_general)
    caja_general.show()
    caja_general.pack_start(caja_principal, False, True, 0)
    caja_general.pack_start(ventana_libro, True, True, 0)
    self.ventana.show_all()
   
    if len(lista) == 0:
      self.treestore.clear()
      '''  
      iter = self.treestore.insert(None,['%s' %y])'''
      Firstdesc = self.treestore.append(None, ["""                                                                 Insight - ICT for the Differently Abled"""])
      self.treestore.append(Firstdesc, ["Insight is a project under Department of Social Justice, Govt. of Kerala and Kerala Federation of the Blind, aimed at empowering the differently abled through computers, Internet and other ICT tools. We believe that technology has the potential to impact \n positively on the lives of persons with disabilities, with regards to information access, education and entertainment. It would not only expand the world of a person with a physical limitation, but also plays the role of a great equalizer. INSIGHT aims to bring \n technology closer to Persons with Disabilities, and to empower them using the possibilities offered by technology."])
      '''fedora = self.treestore.append(None, ["Fedora"])
      self.treestore.append(fedora, ["http://fedoraproject.org/"])
      self.treestore.append(None, ["Sabayon"])
      self.treestore.append(None, ["Arch"])
      debian = self.treestore.append(None, ["Debian"]) 
      self.treestore.append(debian, ["http://www.debian.org/"])'''
          
    if len(lista) > 0:
      #print len(lista)
      self.mostrar_libro(lista)
      self.actualizar_vista(posicion_indice)
      self.c.carga_fichero_inicial()


  def inicio_cargaFichero_callback(self, w, data):
    """
    Method to display the book on the screen when it is opened from the menu
    """
    lista = self.c.cargaFichero(w, data) # take the file with ncc..
    self.mostrar_libro(lista)
    self.c.sinc_vista_audio()


  def mostrar_libro(self, lista):
    """
    Method for displaying a book on the screen when you load the DBR
    """
    self.limpiar_modelo()
    l = []
    for x in range(len(lista)):
      y = lista[x].childNodes
      try:
        z = y[0].firstChild.toprettyxml()
        l.append(y[0])
        iter = self.treestore.append(None, ['%s' % z])
      except:
        pass

  def limpiar_modelo(self):
    """
    Method for removing rows treemodel
    """
    self.treestore.clear()
    

  def actualizar_vista(self, n):
    """
    Method to update the view cursor treeview
    """
    t = (n)
    self.treeview.handler_block(self.cursor_cambiado)
    self.treeview.set_cursor_on_cell(t, self.tvcolumn, self.cell)
    self.treeview.handler_unblock(self.cursor_cambiado)


  def actualizar_audio(self, data):
    """
    Method to update the audio when the user moves the cursor
    """
    pos_cursor = self.treeview.get_cursor()
    aux = list(pos_cursor)
    lista = list(aux[0])
    self.c.sinc_audio_vista(lista[0])
    
  def key_press_event(self, treeview, event):
    """
    Method to fast forward/reverse (skip only) the current playing mp3 file...
    """
    if (event.keyval == 65363):
        self.c.forward_play()
    if (event.keyval == 65361):
        self.c.backward_play()

  def key_press_event_toggle(self,widget, event):
    """
    Method to toggle play/pause.
    """
    #print event.keyval
    if (event.keyval == 32):
      if(self.toggle.get_active()):
        self.toggle.set_active(False)
      else:
        self.toggle.set_active(True)
      self.c.control_estado_callback




  def cerrar_aplicacion(self, w, data):
    """
    Method to close the application from the menu
    """
    self.c.cerrar_aplicacion()
    gtk.main_quit()


  def destruir_aplicacion(self, widget):
    """
    Method to close the application when the signal is emitted destroy
    """
    self.c.cerrar_aplicacion()
    gtk.main_quit()
    
  def draw_play_toggle(self, event, widget):
    #Draw on the toggle button window.
    width = self.toggle.allocation.width #1274
    height = self.toggle.allocation.height #12
    win = self.toggle.get_event_window()
    cr = win.cairo_create()
    if(self.toggle.get_active()): #play shown
      #print "if"
      cr.set_source_rgb(1.0, 0.0, 1.0);
      cr.paint()
      cr.set_source_rgb(0.0, 0.0, 0.0);
      cr.set_line_width(3) #6
      cr.move_to(width/2 - 10, height/2 - 15)
      cr.line_to(width/2 - 10, height/2 + 15)
      cr.line_to(width/2 + 15, height/2)
      cr.line_to(width/2 - 10, height/2 - 15)
      cr.fill()
      cr.stroke()        
    else:
      #print "else"
      cr.set_source_rgb(1.0, 1.0, 0.0);
      cr.paint()
      cr.set_source_rgb(0.0, 0.0, 0.0);
      cr.set_line_width(6)
      cr.move_to(width/2 - 6, height/2 - 15)
      cr.line_to(width/2 - 6, height/2 + 15)
      cr.stroke()
      cr.move_to(width/2 + 6, height/2 - 15)
      cr.line_to(width/2 + 6, height/2 + 15)
      cr.stroke()
      return True    
      
  def play(self,event):
    """
    Method to Play/pause current reading part..
    """
    self.c.control_estado_callback(0,None)

        
  def draw_icon(self):
    #Create a surface to draw a 256x256 icon.
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 48, 48) #256,256
    cr = cairo.Context(surface)
   
    #Paint the background green.
    cr.set_source_rgb(0.0, 1.0, 0.0)
    cr.paint()

    #Draw a sound icon.
    cr.set_source_rgb(0.0, 0.0, 0.0) #green
    #cr.set_source_rgb(1.0, 1.0, 0.0) #yellow
    #cr.set_line_width(3) #6

    cr.rectangle(5.63, 18.76, 9.38, 10.51) #30,100,50,56
    cr.fill()
    cr.stroke()

    cr.move_to(15, 18.76) #80,100
    cr.line_to(24.39, 9.38) #130,50
    cr.rel_curve_to(-1.88, 14.63, -1.88, 14.63, 0, 29.27) #-10,78,-10,78,0,156
    cr.rel_line_to(-9.38, -9.38)     
    #cr.close_path()
    cr.fill()
    cr.arc(18.76, 24, 11.26, -math.pi/(8), math.pi/(8)) #100,128,60, -math.pi/8,math.pi/8
    cr.stroke()
    cr.arc(18.76, 24, 17.82, -math.pi/(4), math.pi/(4)) #100,128,95,-math.pi/4,math.pi/4
    cr.stroke()
    cr.arc(18.76, 24, 24.39, -math.pi/(3.5), math.pi/(3.5)) #100,128,130,-math.pi/3, math.pi/3
    cr.stroke()
   
    #In GTK3 use pixbuf_get_from_surface()
    icon = self.image_surface_to_pixbuf(surface)
 
    return icon;
    
  def image_surface_to_pixbuf(self, surf):
    png_dp = StringIO()
    surf.write_to_png(png_dp)
    pixbuf_loader = gtk.gdk.PixbufLoader()
    pixbuf_loader.write(png_dp.getvalue())
    pixbuf_loader.close()
    return pixbuf_loader.get_pixbuf()
