# -*- coding: iso-8859-15 -*-
import sys, os, os.path, time
import pygst
pygst.require("0.10")
import gst

from dbr_i18n import _          #For i18n support

class Reproductor:
  """
  Class for the reproduction of a book
  """

  def setControlador(self, c):
    self.c = c

  def __init__(self):
    """
    Initializes the player for playback of audio files DAISY book
    """
    self.estado = "Parado" #parado = stationary
    self.activar = "Si" #Si = And
    self.time_format = gst.Format(gst.FORMAT_TIME)
    self.reproductor = gst.Pipeline("player")
    fuente = gst.element_factory_make("filesrc", "file-source")
    self.reproductor.add(fuente)
    decoder = gst.element_factory_make("mad", "mp3-decoder")
    self.reproductor.add(decoder)
    conv = gst.element_factory_make("audioconvert", "converter")
    self.reproductor.add(conv)
    volume = gst.element_factory_make("volume", "volume")
    self.reproductor.add(volume)
    #speed = gst.element_factory_make("speed", "speed")
    #self.reproductor.add(speed)
    #frequency = gst.element_factory_make("frequency", "frequency")
    #self.reproductor.add(frequency)
    sink = gst.element_factory_make("alsasink", "alsa-output")
    self.reproductor.add(sink)
    gst.element_link_many(fuente, decoder, conv, volume, sink)
    self.reproductor.set_state(gst.STATE_NULL)
    bus = self.reproductor.get_bus()
    bus.add_signal_watch()
    bus.connect('message', self.on_message)

  def prueba(self, l): #proof
    i = 0
    while (i < len(l)):
      if self.estado == "Parado" or self.estado == "Pausado":
        if os.path.exists(l[i][0]):
          self.reproductor.get_by_name("file-source").set_property('location', l[i][0])
          self.estado = "Reproduciendo"
          self.reproductor.set_state(gst.STATE_PAUSED)
          time.sleep(0.1)
          self.reproductor.seek(1.0, self.time_format, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, l[i][1], gst.SEEK_TYPE_SET, l[i][2])
          time.sleep(0.1)
          self.reproductor.set_state(gst.STATE_PLAYING)
          espera = (l[i][2]-l[i][1]) / 1000000000 + 0.1
          time.sleep(espera)
          i = i + 1
          self.reproductor.set_state(gst.STATE_NULL)
      elif self.estado == "Reproduciendo":
        if os.path.exists(l[i][0]):
          self.reproductor.get_by_name("file-source").set_property('location', l[i][0])
          # self.estado = "Reproduciendo"
          self.reproductor.set_state(gst.STATE_PAUSED)
          time.sleep(0.1)
          self.reproductor.seek(1.0, self.time_format, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, l[i][1], gst.SEEK_TYPE_SET, l[i][2])
          self.reproductor.set_state(gst.STATE_PLAYING)
          espera = (l[i][2]-l[i][1]) / 1000000000 + 0.1
          time.sleep(espera)
          i = i + 1
          self.reproductor.set_state(gst.STATE_NULL)

  def start_stop(self, l):
    i = 0
    if self.estado == "Parado":
      while ((self.reproductor.get_state() == gst.STATE_NULL) and (i <= range(len(l)))):
        print l[i][0]
        if os.path.exists(l[i][0]):
          print "aquÃ­ tb estoy"
          self.estado = "Reproduciendo"
          self.reproductor.get_by_name("file-source").set_property('location', l[0])
          self.reproductor.set_state(gst.STATE_PLAYING)
          time.sleep(0.1)
          self.reproductor.seek(1.0, self.time_format, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, l[i:1], gst.SEEK_TYPE_SET, l[i:2])
    else:
      print "hola"
      while self.reproductor.get_state == (gst.STATE_PAUSED or gst.STATE_PLAYING) and i < len(l):
        if self.reproductor.get_message == gst.MESSAGE_EOS:
          self.reproductor.set_state(gst.STATE_NULL)
          self.estado = "Parado"
          self.reproductor.set_state(gst.STATE_PLAYING)
          time.sleep(0.1)
          self.player.seek(1.0, self.time_format, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, l[i:1], gst.SEEK_TYPE_SET, l[i:2])
          i = i + 1


  def reproducir(self, fichero, pos_ini, pos_fin):
    """
    MÃ © All to play an audio track .
    file : file playback
    pos_ini : position start playback
    pos_fin : Playback end position
    """
    if self.estado == "Parado" and self.activar == "Si":
      if os.path.exists(fichero):
        self.estado = "Reproduciendo"
        self.reproductor.get_by_name("file-source").set_property('location', fichero)
        self.reproductor.set_state(gst.STATE_PAUSED)
        time.sleep(0.0001)
        self.reproductor.seek(1.0, self.time_format, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, pos_ini, gst.SEEK_TYPE_SET, pos_fin)
        self.reproductor.set_state(gst.STATE_PLAYING)
    elif (self.estado == "Pausado" or self.estado == "Parado") and self.activar == "No":
      if os.path.exists(fichero):
        self.estado = "Pausado"
        self.reproductor.set_state(gst.STATE_NULL)
        self.reproductor.get_by_name("file-source").set_property('location', fichero)
        self.reproductor.set_state(gst.STATE_PAUSED)
        time.sleep(0.0001)
        self.reproductor.seek(1.0, self.time_format, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, pos_ini, gst.SEEK_TYPE_SET, pos_fin)
        self.reproductor.set_state(gst.STATE_PAUSED)



  def detener(self): #stop
    """
    MÃ © everything to stop playback of an audio track
    """
    #self.c.change_toggle_status("pause")
    if self.estado == "Reproduciendo" or self.estado == "Pausado":
      self.reproductor.set_state(gst.STATE_NULL)
      self.estado = "Parado"



  def on_message(self, bus, message):
    """
    MÃ © all to detect when some message occurs in gst h
    Bus: Bus pipeline
    message: message delivered by gst
    """
    t = message.type
    if t == gst.MESSAGE_EOS:
      #print "enter here!"
      #time.sleep(4)
      self.reproductor.set_state(gst.STATE_NULL)
      self.estado = "Parado" #parado = stationary
      #self.c.change_toggle_status("play")
      self.c.sinc_vista_audio()
    elif t == gst.MESSAGE_ERROR:
      self.reproductor.set_state(gst.STATE_NULL)
      self.estado = "Parado"
      err, debug = message.parse_error()
      print "Error: %s" % err, debug

  def reproducir_pausar(self):
    """
    MÃ © all to pause or resume playback of a book
    """
    if self.estado == "Reproduciendo": # playing
      self.reproductor.set_state(gst.STATE_PAUSED)
      self.estado = "Pausado"
      self.activar = "No"
      #self.c.change_toggle_status("pause")
    elif self.estado == "Pausado" or self.activar == "No":
      self.reproductor.set_state(gst.STATE_PLAYING)
      self.estado = "Reproduciendo"
      self.activar = "Si"
      #self.c.change_toggle_status("play")
   
  
  def forward_final(self):
      """
      To fast forward file ...
      """
                  
      self.position = None
      try:
        self.position = (self.reproductor.query_position(gst.FORMAT_TIME,None) [0] ) / gst.SECOND
      except gst.QueryError:
        self.position = None
        pass
      self.duration = (self.reproductor.query_duration(gst.FORMAT_TIME,None) [0] ) / gst.SECOND
      if not self.position is None:
        self.pos_fin = self.position + .00000000001
        #self.pos_fin = self.position + 30
      else:
        self.position = 1
      
      if self.pos_fin < self.duration:
        self.reproductor.seek(1.0, self.time_format, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, \
                         self.position * gst.SECOND, gst.SEEK_TYPE_SET, self.pos_fin * gst.SECOND)

      else:
        self.reproductor.seek(1.0, self.time_format, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, \
             self.position * gst.SECOND, gst.SEEK_TYPE_SET, self.duration * gst.SECOND)

        
      
        
  def reverse_final(self):
      """
      To reverse file ...
      """
      #print "Reverese"
      self.position = None
      self.pos_fin = None
      try:
        self.position = (self.reproductor.query_position(gst.FORMAT_TIME,None) [0] ) / gst.SECOND
      except gst.QueryError:
        self.position = None
        pass
      self.duration = (self.reproductor.query_duration(gst.FORMAT_TIME,None) [0] ) / gst.SECOND
      if (self.pos_fin is None or self.pos_fin < self.duration):
        self.pos_fin = self.duration
      if not self.position is None:
        #self.position = self.position - 30
        self.position = self.position - 8
      else:
        self.position = 0
      #self.reproductor.set_state(gst.STATE_PAUSED)  
      if (self.position > 0):
        self.reproductor.seek(1.0, gst.FORMAT_TIME, \
             gst.SEEK_FLAG_FLUSH, \
             gst.SEEK_TYPE_SET, self.position * gst.SECOND, \
             gst.SEEK_TYPE_NONE,-1)
        #self.reproductor.set_state(gst.STATE_PLAYING)       
      else:
        #print self.position
        #self.reproductor.set_state(gst.STATE_PLAYING)
        self.c.sinc_vista_audio_skip_reverse()
        #self.c.ir_pag_ant_callback(0, None)

  def obtener_ins_actual(self):
    """
    MÃ © everything to get the position in nanoseconds Playback of the current track
    """
    pos = self.reproductor.query_position(self.time_format, None)[0]
    return pos


  def obtener_estado(self):
    """
    MÃ © all to get the current status of playback
    """
    return self.estado


  def cambiar_volumen(self, inc):
    """
    MÃ © All to change the player volume
    inc : parameter to increase or decrease the volume
    """
    volumen_actual = self.reproductor.get_by_name("volume").get_property("volume")
    
    nuevo_volumen = None
    #if(volumen_actual == 1):
      #print "now volume is 1"
    if inc == 1 or inc == -1:
        nuevo_volumen = volumen_actual + inc
    else:
        nuevo_volumen = inc
    #print "new volume is after process in cambiar volument with : "+str(inc)
    #print nuevo_volumen
    if (nuevo_volumen >= 0) and (nuevo_volumen <= 10):
      self.reproductor.get_by_name("volume").set_property('volume', nuevo_volumen)


  def obtener_volumen(self):
    """
    MÃ © all to get the current volume level
    """
    return self.reproductor.get_by_name("volume").get_property("volume")
    
  def silenciar(self):
    """
    MÃ © all to enable or disable the sound
    """
    silencio = self.reproductor.get_by_name("volume").get_property("mute")
    if silencio == True:
      self.reproductor.get_by_name("volume").set_property("mute", False)
    else:
      self.reproductor.get_by_name("volume").set_property("mute", True)
