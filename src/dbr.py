# -*- coding: iso-8859-15 -*-

import pygtk
pygtk.require('2.0')
import gtk
import vista, controlador, reproductor, registro
from dbr_i18n import _          #for i18n support

def main():
  """
 MÃ © all principal of the application
  """
  r = reproductor.Reproductor()
  reg = registro.Registro()
  c = controlador.Controlador(r, reg)
  v = vista.Vista(c)
  r.setControlador(c)

  gtk.main()
  return 0

main()


if __name__ == "__main__":
      pass
