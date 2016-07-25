	# -*- coding: iso-8859-15 -*-

import pickle
import os

from dbr_i18n import _          #For i18n support

class Registro:
  """
  GestiÃ³n class for the saved , manipulation and saving the configuration and trademarks of books
  """

  def __init__(self):
    """
    MÃ © everything to get the configuration of DBR
    """
    home = os.path.expanduser('~')
    self.fichero_configuracion = home + "/" + ".dbr"
    #self.recent_books = home + "/" + ".recent_books"
    if os.path.exists(self.fichero_configuracion):
      f = open(self.fichero_configuracion, "r")
      self.registro = pickle.load(f)
      f.close()
    else:
      self.crear_fichero_configuracion()


  def escribir_configuracion(self, informacion):
    """
    MÃ © all to write to the configuration data configuration and the position last book reader ultimate in reproduction
    information and configuration information of the last book reproduced
    """
    self.registro[0] = informacion
    f = open(self.fichero_configuracion, "w")
    pickle.dump(self.registro, f)
    f.close()


  def obtener_configuracion(self):
    """
    MÃ © all for the configuration of the DBR and The newest libroleÃdo and reading position
    """
    return self.registro[0]


  def crear_fichero_configuracion(self):
    """
    Ã © everything to create the configuration & recent_book file of DBR if there
    """
    self.registro = [0]
    #self.registro_recent_books = [0]
    configuracion = [None, None, [0, 0, 0], 1]
    self.registro[0] = configuracion
    f = open(self.fichero_configuracion, "w")
    pickle.dump(self.registro, f)
    f.close()
    #g = open(self.recent_books, "w")
    #pickle.dump(self.registro_recent_books,g)
    #g.close()

  def crear_marca(self, marca):
    """
    MÃ © everything to create or update a mark of a book and store it in the configuration file
    Brand: data needed to create brand
    """
    aux = [0]
    # We check if there is a stored book
    if len(self.registro) > 1:
      # We check if the book that will put the brand HATH stored and
      i = 0
      encontrado = 0
      while (i < (len(self.registro)-1)) and encontrado == 0:
        i = i + 1
        if self.registro[i][0] == marca[0]:
          encontrado = 1
      if encontrado == 1:
        # The book HATH stored
        # We check if the book is marked with the name of the new brand
        j = 1
        terminado = 0
        while (j < (len(self.registro[i])-1)) and (terminado == 0):
          j = j + 1
          if self.registro[i][j][0] == marca[5]:
            terminado = 1
        if terminado == 1:
          # There is a mark of that name
          self.registro[i][j][1:4] = marca[2:5]
        else:
          # There is no brand that name
          aux[0] = marca[5]
          aux = aux + marca[2:5]
          self.registro[i].append(aux)
      else:
        # There is no book with that name stored
        self.registro.append(marca[0:2])
        aux[0] = marca[5]
        aux = aux + marca[2:5]
        self.registro[i+1].append(aux)
    else:
      # There is no stored book
      self.registro.append(marca[0:2])
      aux[0] = marca[5]
      aux = aux + marca[2:5]
      pos = len(self.registro) - 1
      self.registro[pos].append(aux)
    #print self.registro
    f = open(self.fichero_configuracion, "w")
    pickle.dump(self.registro, f)
    f.close()


  def obtener_marcas_libro_actual(self, nombre_libro):
    """
    MÃ © all for book marks currently in reproduction
    """
    # Comprobamos si hay algun libro con marcas
    if len(self.registro) > 1:
      i = 0
      encontrado = 0
      while (i < (len(self.registro)-1)) and encontrado == 0:
        i = i + 1
        if self.registro[i][0] == nombre_libro:
          encontrado = 1
      if encontrado == 1:
        # Obtenemos las marcas disponibles
        marcas = []
        j = 2
        while (j < len(self.registro[i])):
          marcas.append(self.registro[i][j])
          j = j + 1
      else:
        marcas = []
    else:
      marcas = []
    return marcas


  def borrar_marca(self, nombre_libro, pos_marca):
    """
    MÃ©todo para borrar una marca en el libro actualmente en reproducciÃ³n
    """
    i = 0
    encontrado = 0
    while (i < len(self.registro)) and (encontrado == 0):
      i = i + 1
      if nombre_libro == self.registro[i][0]:
        encontrado = 1
    if len(self.registro[i]) == 3:
      self.registro.pop(i)
    else:
      self.registro[i].pop(pos_marca+2)
    f = open(self.fichero_configuracion, "w")
    pickle.dump(self.registro, f)
    f.close()


  def buscar_libros(self): #look for books
    """
    MÃ © all looking for books stored in the configuration file
    """
    libros = []
    if len(self.registro) > 1:
    
      i = 0
      while (i < (len(self.registro)-1)):
        i = i + 1
        if os.path.exists(self.registro[i][1]):
          libros.append(self.registro[i][0:2])
    return libros

  def recent_books(self): #look for recent books
    """
    MÃ © all looking for books stored in the configuration file (.recent_books)
    """
    libros = []
    num_lines = 0
    #with open('testfile', 'r') as f:
    with open(os.path.expanduser("~/.recent_books"), 'a+') as f:
      for line in f: 
        num_lines += 1
       
   
    #print num_lines
    
    if num_lines > 0:
      with open(os.path.expanduser("~/.recent_books"), 'a+') as f:
        #data = f.readlines()[-5:]
        data = set(open(os.path.expanduser("~/.recent_books")).readlines()[-5:])
        alist = []
        i=0;
        for line in data:
          alist.insert(i,line.split('--')[0])
          alist.insert(i+1,line.split('--')[1].rstrip())
        return alist

