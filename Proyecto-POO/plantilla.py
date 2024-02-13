"""Aplicativo gráfico de tipo CRUD (Create, Read, Update, Delete) en Python 3 asociado a la base de datos SQLite3.
  
  Información general:

  El programa utiliza la librería Tkinter para generar una interfaz gráfica interactiva de tipo CRUD, es decir,
  permite la creación, lectura, edición y eliminación de datos. Algunas de estas funciones asociadas a un Botón
  generado con ttk ("themed Tkinter"), un módulo de la librería Tkinter de Python.
  A través de la base de datos SQLite3 se crean dos tablas de datos llamadas "Proveedores" e "Inventario" con
  las siguientes estructuras:
  1. Tabla "Proveedores":
   - IdNit (VARCHAR(15)): IdNit del proveedor.
   - Codigo (VARCHAR(15)): Código del producto.
   - Descripcion (VARCHAR): Descripción del producto.
   - Und (VARCHAR(10)): Unidad del producto.
   - Cantidad (DOUBLE): Cantidad del producto.
   - Precio (DOUBLE): Precio del producto.
   - Fecha (DATE): Fecha de producto.
   - PRIMARY KEY (IdNit, Codigo): Llave de primaria de la tabla.
  
  2. Tabla "Inventario":
   - IdNitProv (VARCHAR PRIMARY KEY UNIQUE NOT NULL): IdNit del proveedor.
   - Razon_Social (VARCHAR): Razón social (nombre) del proveedor.
   - Ciudad (VARCHAR): Ciudad del proveedor.
  
  Se permite la interacción del usuario con parte del contenido guardado en la base de datos, a través de una grilla
  llamada "TreeView", por medio de esta el usuario puede acceder a funciones como eliminar producto/proveedor de la
  base de datos o editar los anteriores.  

  Integrantes:
  __Autor__= ["Ángel David Beltrán García", 
              "Paula Vanessa Garzón Parada", 
              "Kevin Sebastian Ovalle Chacon", 
              "Juan Camilo Rosero Santisteban", 
              "Justin David Vargas Vasquez"]

  Este código se modifico por última vez:
  __date__ = 27/11/2023
"""

# !/usr/bin/python3
# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mssg
from tkinter import font
import sqlite3
import os.path as path
from re import sub
from datetime import date, datetime

class Ventana_De_Pregunta:
  def __init__(self, master): 
    self.master = master
    self.result = None
    self.popup = tk.Toplevel(master)
    self.popup.title("Eliminar!!")
    self.popup.protocol("WM_DELETE_WINDOW", self.cerrar_Ventana)  # Se ejecutará al cerrar la ventana
    self.popup.grab_set() # Convierte la ventana "Eliminar¡¡" en una ventana modal, bloquea el acceso a otras ventanas
    self.popup.resizable(False, False) # Impide la redimensionalización de la ventana tanto en horizontal (primer False), como vertical (segundo False)
    self.path = str(path.dirname(__file__)) # Obtiene la dirección de acceso del archivo "plantilla.py" y lo convierte a string.
    self.valida_Icono() # Valida la existencia de los iconos.
    self.popup.grab_set() # Convierte la ventana "Eliminar¡¡" en una ventana modal, bloquea el acceso a otras ventanas
    
    ancho = 250; alto = 160

    """ centra las ventanas en la pantalla """ 
    x = self.popup.winfo_screenwidth() // 2 - ancho // 2 
    y = self.popup.winfo_screenheight() // 2 - alto // 2 
    self.popup.geometry(f'{ancho}x{alto}+{x}+{y}')  
    self.popup.deiconify() # Se usa para restaurar la ventana 
    
    '''Crear ventana emergente al eliminar un producto con sus respectivas opciones'''     
    label = tk.Label(self.popup, text="¿Desea eliminar un proveedor o un producto?")
    label.pack(pady=10)
    btn_Proveedor = ttk.Button(self.popup, text="Proveedor", command=self.select_Proveedor)   
    btn_Proveedor.pack(padx=10, pady=5)
    btn_Producto = ttk.Button(self.popup, text="Producto", command=self.select_Producto)
    btn_Producto.pack(padx=10, pady=5)
    btn_Cancelar = ttk.Button(self.popup, text="Cancelar", command=self.select_Cancelar)
    btn_Cancelar.pack(padx=10, pady=5)

  # Validar existencia de un icono
  def valida_Icono (self):
    icono_Kirby = self.path + "/imgs/kirby.ico"
    if path.exists(icono_Kirby): # Si existe "kirby.ico" lo asocia como el icono del programa.
      self.popup.iconbitmap(self.path + "/imgs/kirby.ico")
    else: # Si no existe ninguno de los dos iconos, no hace nada, es decir, mantiene el icono por defecto de "tkinter".
      pass   
  def select_Proveedor(self):
    self.result = "proveedor"
    self.popup.destroy()
  def select_Producto(self):
    self.result = "producto"
    self.popup.destroy()
  def select_Cancelar(self):
    self.result = "cancelar"
    self.popup.destroy()
  def cerrar_Ventana(self):
    self.popup.destroy()

class Inventario:
  def __init__(self, master=None):
    self.path = str(path.dirname(__file__))
    self.db_Name = self.path + r'/BD/Inventario.db'
    
    ancho=830;alto=570 # Dimensiones de la pantalla
    self.actualiza = None
    self.buscando = None

    # Crea ventana principal
    self.win = tk.Tk() 
    self.win.geometry(f"{ancho}x{alto}")
    self.valida_Icono()
    self.win.resizable(False, False)
    self.win.title("Manejo de Proveedores") 

    #Centra la pantalla
    self.centra(self.win,ancho,alto)

    # Contenedor de widgets   
    self.win = tk.LabelFrame(master)
    self.win.configure(background="#e0e0e0",font="{Arial} 12 {bold}",
    height=ancho,labelanchor="n",width=alto)
    self.tabs = ttk.Notebook(self.win)
    self.tabs.configure(height=535, width=799) # CAMBIAR HEIGHT A 800

    #Frame de datos
    self.frm1 = ttk.Frame(self.tabs)
    self.frm1.configure(height=200, width=200)

    #Etiqueta IdNit del Proveedor
    self.lbl_Id_Nit = ttk.Label(self.frm1)
    self.lbl_Id_Nit.configure(text='Id/Nit', width=6)
    self.lbl_Id_Nit.place(anchor="nw", x=10, y=40)

    #Captura IdNit del Proveedor
    self.control_Caracteres_Id_Nit = tk.StringVar()
    """Se utiliza "StringVar()" para almacenar la cadena de caracteres asociados al label "Código", 
    la ventaja de "Stringvar()" es que permite rastrear y modificar la cadena en tiempo real."""
    self.id_Nit = ttk.Entry(self.frm1, textvariable=self.control_Caracteres_Id_Nit) # Enlaza la variable "self.control_Caracteres_Id_Nit" al widget "self.id_Nit"
    self.id_Nit.configure(takefocus=True) # Habilita la posibilidad de enfocar
    self.id_Nit.place(anchor="nw", x=50, y=40)
    self.id_Nit.bind("<Control-v>", self.deshabilitar_Pegado) # Asocia el evento "Control+V" con la función "deshabilitar_Pegado" impidiendo que se pueda pegar contenido en los Entry.
    self.control_Caracteres_Id_Nit.trace_add('write', self.valida_Id_Nit) # Permite mostrar los cambios en la variable en tiempo de ejecución
    self.id_Nit.focus() # Incia el foco en el label "idNit" desde el inicio

    #Etiqueta razón social del Proveedor
    self.lbl_Razon_Social = ttk.Label(self.frm1)
    self.lbl_Razon_Social.configure(text='Razón social', width=12)
    self.lbl_Razon_Social.place(anchor="nw", x=210, y=40)
    
    #Captura razón social del Proveedor
    self.control_Caracteres_Razon_Social = tk.StringVar()
    self.razon_Social = ttk.Entry(self.frm1, textvariable= self.control_Caracteres_Razon_Social) # Enlaza la variable "self.control_Caracteres_Razon_Social" al widget "self.razon_Social"
    self.razon_Social.configure(width=36)
    self.razon_Social.place(anchor="nw", x=290, y=40)
    self.razon_Social.bind("<Control-v>", self.deshabilitar_Pegado) # Asocia el evento "Control+V" con la función "deshabilitar_Pegado"
    self.control_Caracteres_Razon_Social.trace_add('write', self.valida_Razon_Social) # Permite mostrar los cambios en la variable en tiempo de ejecución

    #Etiqueta ciudad del Proveedor
    self.lbl_Ciudad = ttk.Label(self.frm1)
    self.lbl_Ciudad.configure(text='Ciudad', width=7)
    self.lbl_Ciudad.place(anchor="nw", x=540, y=40)

    #Captura ciudad del Proveedor
    self.control_Caracteres_Ciudad = tk.StringVar()
    self.ciudad = ttk.Entry(self.frm1, textvariable= self.control_Caracteres_Ciudad) # Enlaza la variable "self.control_Caracteres_Ciudad" al widget "self.ciudad"
    self.ciudad.configure(width=30)
    self.ciudad.place(anchor="nw", x=590, y=40)
    self.ciudad.bind("<Control-v>", self.deshabilitar_Pegado) # Asocia el evento "Control+V" con la función "deshabilitar_Pegado"
    self.control_Caracteres_Ciudad.trace_add('write', self.valida_Ciudad) # Permite mostrar los cambios en la variable en tiempo de ejecución

    #Separador
    self.separador1 = ttk.Separator(self.frm1)
    self.separador1.configure(orient="horizontal")
    self.separador1.place(anchor="nw", width=800, x=0, y=79)

    #Etiqueta Código del Producto
    self.lbl_Codigo = ttk.Label(self.frm1)
    self.lbl_Codigo.configure(text='Código', width=7)
    self.lbl_Codigo.place(anchor="nw", x=10, y=120)

    #Captura el código del Producto
    self.control_Caracteres_Codigo = tk.StringVar() # Control de caracteres en labels
    self.codigo = ttk.Entry(self.frm1, textvariable=self.control_Caracteres_Codigo) # Enlaza la variable "self.control_Caracteres_Codigo" al widget "self.codigo"
    self.codigo.configure(width=13)
    self.codigo.place(anchor="nw", x=60, y=120)
    self.codigo.bind("<Control-v>", self.deshabilitar_Pegado) # Asocia el evento "Control+V" con la función "deshabilitar_Pegado"
    self.control_Caracteres_Codigo.trace_add('write', self.valida_Codigo) # Permite mostrar los cambios en la variable en tiempo de ejecución

    #Etiqueta descripción del Producto
    self.lbl_Descripcion = ttk.Label(self.frm1)
    self.lbl_Descripcion.configure(text='Descripción', width=11)
    self.lbl_Descripcion.place(anchor="nw", x=220, y=120)

    #Captura la descripción del Producto
    self.control_Caracteres_Descripcion = tk.StringVar() # Control de caracteres en labels
    self.descripcion = ttk.Entry(self.frm1, textvariable=self.control_Caracteres_Descripcion) # Enlaza la variable "self.control_Caracteres_Descripcion" al widget "self.descripcion"
    self.descripcion.configure(width=36)
    self.descripcion.place(anchor="nw", x=290, y=120)
    self.descripcion.bind("<Control-v>", self.deshabilitar_Pegado) # Asocia el evento "Control+V" con la función "deshabilitar_Pegado"
    self.control_Caracteres_Descripcion.trace_add('write', self.valida_Descripcion) # Permite mostrar los cambios en la variable en tiempo de ejecución

    #Etiqueta unidad o medida del Producto
    self.lbl_Und = ttk.Label(self.frm1)
    self.lbl_Und.configure(text='Unidad', width=7)
    self.lbl_Und.place(anchor="nw", x=540, y=120)

    #Captura la unidad o medida del Producto
    self.control_Caracteres_Unidad = tk.StringVar()
    self.unidad = ttk.Entry(self.frm1, textvariable= self.control_Caracteres_Unidad) # Enlaza la variable "self.control_Caracteres_Unidad" al widget "self.unidad"
    self.unidad.configure(width=10)
    self.unidad.place(anchor="nw", x=590, y=120)
    self.unidad.bind("<Control-v>", self.deshabilitar_Pegado) # Asocia el evento "Control+V" con la función "deshabilitar_Pegado"
    self.control_Caracteres_Unidad.trace_add('write', self.valida_Unidad) # Permite mostrar los cambios en la variable en tiempo de ejecución

    #Etiqueta cantidad del Producto
    self.lbl_Cantidad = ttk.Label(self.frm1)
    self.lbl_Cantidad.configure(text='Cantidad', width=8)
    self.lbl_Cantidad.place(anchor="nw", x=10, y=170)

    #Captura la cantidad del Producto
    self.control_Caracteres_Cantidad = tk.StringVar()
    self.cantidad = ttk.Entry(self.frm1, textvariable= self.control_Caracteres_Cantidad) # Enlaza la variable "self.control_Caracteres_Cantidad" al widget "self.cantidad"
    self.cantidad.configure(width=12)
    self.cantidad.place(anchor="nw", x=70, y=170)
    self.cantidad.bind("<Control-v>", self.deshabilitar_Pegado) # Asocia el evento "Control+V" con la función "deshabilitar_Pegado"
    self.control_Caracteres_Cantidad.trace_add('write', self.valida_Cantidad) # Permite mostrar los cambios en la variable en tiempo de ejecución

    #Etiqueta precio del Producto
    self.lbl_Precio = ttk.Label(self.frm1)
    self.lbl_Precio.configure(text='Precio $', width=8)
    self.lbl_Precio.place(anchor="nw", x=170, y=170)

    #Captura el precio del Producto
    self.control_Caracteres_Precio =  tk.StringVar()
    self.precio = ttk.Entry(self.frm1, textvariable= self.control_Caracteres_Precio) # Enlaza la variable "self.control_Caracteres_Cantidad" al widget "self.cantidad"
    self.precio.configure(width=15)
    self.precio.place(anchor="nw", x=220, y=170)
    self.precio.bind("<Control-v>", self.deshabilitar_Pegado) # Asocia el evento "Control+V" con la función "deshabilitar_Pegado"
    self.control_Caracteres_Precio.trace_add('write', self.valida_Precio) # Permite mostrar los cambios en la variable en tiempo de ejecución

    #Etiqueta fecha de compra del Producto
    self.lbl_Fecha = ttk.Label(self.frm1)
    self.lbl_Fecha.configure(text='Fecha', width=6)
    self.lbl_Fecha.place(anchor="nw", x=350, y=170)

    #Captura la fecha de compra del Producto
    self.control_Caracteres_Dia= tk.StringVar()
    self.control_Caracteres_Mes= tk.StringVar()
    self.control_Caracteres_Anio= tk.StringVar()
    self.dia = ttk.Entry(self.frm1, textvariable= self.control_Caracteres_Dia) # Enlaza la variable "self.control_Caracteres_Dia" al widget "self.dia"
    self.mes = ttk.Entry(self.frm1, textvariable= self.control_Caracteres_Mes)
    self.anio = ttk.Entry(self.frm1, textvariable= self.control_Caracteres_Anio)
    self.dia.configure(width=3)
    self.mes.configure(width=4)
    self.anio.configure(width=5)
    self.dia.place(anchor="nw", x=390, y=170)
    self.mes.place(anchor="nw", x=420, y=170)
    self.anio.place(anchor="nw", x=455, y=170)
    self.dia.configure(foreground="gray") # Cambia el color de letra del label
    self.mes.configure(foreground="gray")
    self.anio.configure(foreground="gray")
    self.dia.insert(0, "dd") # Agregar el placeholder
    self.mes.insert(0, "mm")    
    self.anio.insert(0, "yyyy")
    self.dia.bind("<FocusIn>", self.limpiar_Placeholder_Dia) # Cuando el label es enfocado ejecuta la función "limpiar_Placeholder"
    self.dia.bind("<FocusOut>", self.restore_Placeholder_Dia) # Cuando el label es desenfocado ejecuta la función "restore_Placeholder"
    self.dia.bind("<Right>", self.right_Dia)
    self.mes.bind("<FocusIn>", self.limpiar_Placeholder_Mes)
    self.mes.bind("<FocusOut>", self.restore_Placeholder_Mes)
    self.mes.bind("<Right>", self.right_Mes)
    self.mes.bind("<Left>", self.left_Mes)
    self.mes.bind("<BackSpace>", self.backspace_Mes)
    self.anio.bind("<FocusIn>", self.limpiar_Placeholder_Anio)
    self.anio.bind("<FocusOut>", self.restore_Placeholder_Anio)
    self.anio.bind("<Left>", self.left_Anio)
    self.anio.bind("<BackSpace>", self.backspace_Anio)
    self.anio.bind("<Return>", self.adiciona_Registro)
    self.control_Caracteres_Dia.trace_add('write', self.valida_Tamanio_Dia) # Permite mostrar los cambios en la variable en tiempo de ejecución
    self.control_Caracteres_Mes.trace_add('write', self.valida_Tamanio_Mes)
    self.control_Caracteres_Anio.trace_add('write', self.valida_Tamanio_Anio)

    #Separador
    self.separador2 = ttk.Separator(self.frm1)
    self.separador2.configure(orient="horizontal")
    self.separador2.place(anchor="nw", width=800, x=0, y=220)

    #tabla_Tree_View
    self.style=ttk.Style()
    self.style.configure("estilo.Treeview", highlightthickness=0, bd=0, background="#F1F6F9", foreground= "#394867", font=('Calibri Light',10))
    self.style.configure("estilo.Treeview.Heading", background='#F1F6F9', foreground= "#394867", font=('Calibri Light', 10,'bold')) 
    self.style.layout("estilo.Treeview", [('estilo.Treeview.treearea', {'sticky': 'nswe'})]) #el widget debe expandirse en todas las direcciones (norte, sur, oeste y este)
    
    #Árbol para mosrtar los datos de la B.D.
    self.tree_Productos = ttk.Treeview(self.frm1, style="estilo.Treeview")
    self.tree_Productos.configure(selectmode="browse") #con este modo solo se puede seleccionar un elemento a la vez y no más de uno

    # Etiquetas de las columnas para el TreeView
    self.tree_Productos["columns"]=("Codigo","Descripcion","Und","Cantidad","Precio","Fecha")
    # Características de las columnas widget Treeview con alineación a la izquierda, la columna se puede estirar para llenar el espacio disponible.
    self.tree_Productos.column ("#0",         anchor="w",stretch=True,width=3)
    self.tree_Productos.column ("Codigo",      anchor="w",stretch=True,width=3)
    self.tree_Productos.column ("Descripcion", anchor="w",stretch=True,width=150)
    self.tree_Productos.column ("Und",        anchor="w",stretch=True,width=3)
    self.tree_Productos.column ("Cantidad",    anchor="w",stretch=True,width=3)
    self.tree_Productos.column ("Precio",      anchor="w",stretch=True,width=8)
    self.tree_Productos.column ("Fecha",       anchor="w",stretch=True,width=3)

    # Etiquetas de columnas con los nombres que se mostrarán por cada columna con alineación en el centro
    self.tree_Productos.heading("#0",         anchor="center", text='ID / Nit')
    self.tree_Productos.heading("Codigo",      anchor="center", text='Código')
    self.tree_Productos.heading("Descripcion", anchor="center", text='Descripción')
    self.tree_Productos.heading("Und",        anchor="center", text='Unidad')
    self.tree_Productos.heading("Cantidad",    anchor="center", text='Cantidad')
    self.tree_Productos.heading("Precio",      anchor="center", text='Precio')
    self.tree_Productos.heading("Fecha",       anchor="center", text='Fecha')

    #Carga los datos en treeProductos y alinea el contenido en la esquina superior izquierda.
    self.lee_Tree_Productos() 
    self.tree_Productos.place(anchor="nw", height=250, width=790, x=2, y=230)

    #Scrollbar en el eje Y de treeProductos
    self.scrollbary=ttk.Scrollbar(self.tree_Productos, orient='vertical', command=self.tree_Productos.yview)
    self.tree_Productos.configure(yscroll=self.scrollbary.set)
    self.scrollbary.place(anchor='nw', x=773, y=24, height=223)

    #Frame 2 para contener los botones

    self.frm2 = ttk.Frame(self.win)
    self.frm2.configure(height=100, width=800)

    # Título de la pestaña Ingreso de Datos
    self.frm1.pack(side="top")
    self.tabs.add(self.frm1, compound="center", text='Ingreso de datos')
    self.tabs.pack(side="top")

    #Frame 2 para contener los botones
    self.frm2 = ttk.Frame(self.win)
    self.frm2.configure(height=70, width=800)

    #Botón para Buscar un Proveedor
    self.btnBuscar = ttk.Button(self.frm2)
    self.btnBuscar.configure(text='Buscar', command = self.buscarPorIdNit_Codigo)
    self.btnBuscar.place(anchor="nw", width=70, x=200, y=10)

    #Botón para Guardar los datos
    self.btnGrabar = ttk.Button(self.frm2)
    self.btnGrabar.configure(text='Grabar', command = self.adiciona_Registro)
    self.btnGrabar.place(anchor="nw", width=70, x=275, y=10)

    #Botón para Editar los datos
    self.btnEditar = ttk.Button(self.frm2)
    self.btnEditar.configure(text='Editar', command = self.edita_Tree_Proveedores)
    self.btnEditar.place(anchor="nw", width=70, x=350, y=10)

    #Botón para Eliminar datos
    self.btnEliminar = ttk.Button(self.frm2)
    self.btnEliminar.configure(text='Eliminar', command = self.elimina_Registro)
    self.btnEliminar.place(anchor="nw", width=70, x=425, y=10)

    #Botón para cancelar una operación
    self.btnCancelar = ttk.Button(self.frm2)
    self.btnCancelar.configure(text='Cancelar', width=80, command = self.limpia_Campos)
    self.btnCancelar.place(anchor="nw", width=70, x=500, y=10)

    #Ubicación del Frame 2
    self.frm2.place(anchor="nw", height=60, relwidth=1, y=500) # CAMBIAR y=755
    self.win.pack(anchor="center", side="top")

    # widget Principal del sistema
    self.mainwindow = self.win

  #Fución de manejo de eventos del sistema
  def run(self):
      self.mainwindow.mainloop()

  ''' ......... Métodos utilitarios del sistema .............'''
  #Rutina de centrado de pantalla
  def centra(self,win,ancho,alto): 
      """ centra las ventanas en la pantalla """ 
      x = win.winfo_screenwidth() // 2 - ancho // 2 
      y = win.winfo_screenheight() // 2 - alto // 2 
      win.geometry(f'{ancho}x{alto}+{x}+{y}') 
      win.deiconify() # Se usa para restaurar la ventana

  # Validaciones del sistema
  def valida_Id_Nit(self, *args):
    if len(self.control_Caracteres_Id_Nit.get()) <= 15:
      self.contenido_Id_Nit = self.control_Caracteres_Id_Nit.get() # Si la cantidad de carácteres es menor igual a 15 guarda la cadena
    elif len(self.control_Caracteres_Id_Nit.get()) > 15: # Cuenta la cantidad de caracteres ingresados ejecutandose cuando supera los 15 carácteres
      self.control_Caracteres_Id_Nit.set(self.contenido_Id_Nit) # Asigna la cadena guardada al momento de completar 15 carácteres
      self.id_Nit.icursor(int(self.id_Nit.index(tk.INSERT) - 1)) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve
      self.id_Nit.bell() # Al cumplirse la condición genera el sonido de una campana
    
    if " " in self.control_Caracteres_Id_Nit.get(): # Verifica la exitencia de un espacio (" ") en la cadena.
      self.control_Caracteres_Id_Nit.set(self.control_Caracteres_Id_Nit.get().replace(" ", "")) # Elimina el espacio, reemplazandolo por un vacio ("")
      self.id_Nit.icursor(self.id_Nit.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve
      self.id_Nit.bell() # Al cumplirse la condición genera el sonido de una campana

  def valida_Codigo(self, *args):
    if len(self.control_Caracteres_Codigo.get()) <= 15:
      self.contenido_Codigo = self.control_Caracteres_Codigo.get() # Si la cantidad de carácteres es menor igual a 15 guarda la cadena
    elif len(self.control_Caracteres_Codigo.get()) > 15: # Cuenta la cantidad de caracteres ingresados
      self.control_Caracteres_Codigo.set(self.contenido_Codigo) # Asigna al Entry la cadena anteriormente guardada
      self.codigo.icursor(self.codigo.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve.
      self.codigo.bell() # Al cumplirse la condición genera el sonido de una campana

  def valida_Descripcion(self, *args):
    if len(self.control_Caracteres_Descripcion.get()) <= 40:
      self.contenido_Descripcion = self.control_Caracteres_Descripcion.get() # Si la cantidad de carácteres es menor igual a 40 guarda la cadena
    elif len(self.control_Caracteres_Descripcion.get()) > 40: # Cuenta la cantidad de caracteres ingresados
      self.control_Caracteres_Descripcion.set(self.contenido_Descripcion) # Asigna al Entry la cadena anteriormente guardada
      self.descripcion.icursor(self.descripcion.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve.
      self.descripcion.bell() # Al cumplirse la condición genera el sonido de una campana

  def valida_Unidad(self, *args):
    if len(self.control_Caracteres_Unidad.get()) <= 10:
      self.contenido_Unidad = self.control_Caracteres_Unidad.get() # Si la cantidad de carácteres es menor igual a 10 guarda la cadena
    elif len(self.control_Caracteres_Unidad.get()) > 10: # Cuenta la cantidad de caracteres ingresados
      self.control_Caracteres_Unidad.set(self.contenido_Unidad) # Asigna al Entry la cadena anteriormente guardada
      self.unidad.icursor(self.unidad.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve.
      self.unidad.bell() # Al cumplirse la condición genera el sonido de una campana

  def valida_Cantidad(self, *args):
    if len(self.control_Caracteres_Cantidad.get()) <= 15:
      self.contenido_Cantidad = self.control_Caracteres_Cantidad.get() # Si la cantidad de carácteres es menor igual a 15 guarda la cadena
    elif len(self.control_Caracteres_Cantidad.get()) > 15: # Cuenta la cantidad de caracteres ingresados
      self.control_Caracteres_Cantidad.set(self.contenido_Cantidad) # Asigna al Entry la cadena anteriormente guardada
      self.cantidad.icursor(self.cantidad.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve
      self.cantidad.bell() # Al cumplirse la condición genera el sonido de una 
      
    if any((char.isalpha() or not char.isalnum()) and char != '.' for char in self.control_Caracteres_Cantidad.get()): # Impide que el usuario ingrese un carácter no numérico.
      self.control_Caracteres_Cantidad.set(sub(r'[^\d.]', '', self.control_Caracteres_Cantidad.get())) # Actualiza el Entry sin incluir el carácter no numérico.
      self.cantidad.bell() # Al cumplirse la condición genera el sonido de una campana
      if self.cantidad.index(tk.INSERT) != 'end': # Retrocede el cursor cuando no está al final del Entry.
        self.cantidad.icursor(self.cantidad.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve       
      
    if ".." in self.control_Caracteres_Cantidad.get(): # Verifica la exitencia de un doble punto ("..") en la cadena.
      self.control_Caracteres_Cantidad.set(self.control_Caracteres_Cantidad.get().replace("..", ".")) # Elimina el segundo punto, reemplazandolo por un vacio ("")
      self.cantidad.icursor(self.cantidad.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve
      self.cantidad.bell() # Al cumplirse la condición genera el sonido de una campana
      
  def valida_Precio(self, *args):
    if len(self.control_Caracteres_Precio.get()) <= 15:
      self.contenido_Precio = self.control_Caracteres_Precio.get() # Si la cantidad de carácteres es menor igual a 15 guarda la cadena
    elif len(self.control_Caracteres_Precio.get()) > 15: # Cuenta la cantidad de caracteres ingresados
      self.control_Caracteres_Precio.set(self.contenido_Precio) # Asigna al Entry la cadena anteriormente guardada
      self.precio.icursor(self.precio.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve
      self.precio.bell() # Al cumplirse la condición genera el sonido de una campana
    
    if any((char.isalpha() or not char.isalnum()) and char != '.' for char in self.control_Caracteres_Precio.get()): # Impide que el usuario ingrese un carácter no numérico.
      self.control_Caracteres_Precio.set(sub(r'[^\d.]', '', self.control_Caracteres_Precio.get())) # Actualiza el Entry sin incluir el carácter no numérico.
      self.precio.bell() # Al cumplirse la condición genera el sonido de una campana
      if self.precio.index(tk.INSERT) != 'end': # Retrocede el cursor cuando no está al final del Entry.
        self.precio.icursor(self.precio.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve  
    if ".." in self.control_Caracteres_Precio.get(): # Verifica la exitencia de un doble punto ("..") en la cadena.
      self.control_Caracteres_Precio.set(self.control_Caracteres_Precio.get().replace("..", ".")) # Elimina el segundo punto, reemplazandolo por un vacio ("")
      self.precio.icursor(self.precio.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve
      self.precio.bell() # Al cumplirse la condición genera el sonido de una campana
      
  def valida_Razon_Social(self, *args):
    if len(self.control_Caracteres_Razon_Social.get()) <= 40:
      self.contenido_Razon_Social = self.control_Caracteres_Razon_Social.get() # Si la cantidad de carácteres es menor igual a 40 guarda la cadena
    elif len(self.control_Caracteres_Razon_Social.get()) > 40: # Cuenta la cantidad de caracteres ingresados
      self.control_Caracteres_Razon_Social.set(self.contenido_Razon_Social) # Asigna al Entry la cadena anteriormente guardada
      self.razon_Social.icursor(self.razon_Social.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve
      self.razon_Social.bell() # Al cumplirse la condición genera el sonido de una campana

  def valida_Ciudad(self, *args):
    if len (self.control_Caracteres_Ciudad.get()) <= 20:
      self.contenido_Ciudad = self.control_Caracteres_Ciudad.get() # Si la cantidad de carácteres es menor igual a 20 guarda la cadena
    elif len(self.control_Caracteres_Ciudad.get()) > 20: # Cuenta la cantidad de caracteres ingresados
      self.control_Caracteres_Ciudad.set(self.contenido_Ciudad) # Asigna al Entry la cadena anteriormente guardada
      self.ciudad.icursor(self.ciudad.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve
      self.ciudad.bell() # Al cumplirse la condición genera el sonido de una campana
      
  def valida_Tamanio_Dia(self, *args): # Evita el ingreso de carácteres no numéricos en el Entry.
    self.dia.configure(foreground ='black') # Establece el color de letra a negro.
    if self.control_Caracteres_Dia.get() == 'dd': # Si la cadena ingresada es el "Placeholder" no hace nada.
      return "break"
    elif len(self.control_Caracteres_Dia.get()) <=2 :# Si la cadena ingresada tiene menos de 3 carácteres los guarda
      self.contenido_Dia = self.control_Caracteres_Dia.get()
    elif len(self.control_Caracteres_Dia.get()) > 2:
      self.control_Caracteres_Dia.set(self.contenido_Dia) # Si la cadena tiene más de dos carácteres carga la cadena guardada previamente.
      self.dia.icursor(self.dia.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve
      self.dia.bell() # Al cumplirse la condición genera el sonido de una campana
    
    if any(char.isalpha() or not char.isalnum() for char in self.control_Caracteres_Dia.get()): #Impide que el usuario ingrese un carácter no numérico.
      self.control_Caracteres_Dia.set(sub(r'\D', '', self.control_Caracteres_Dia.get())) # Actualiza el Entry sin incluir el carácter no numérico.
      self.dia.bell() # Al cumplirse la condición genera el sonido de una campana
    
    if len(self.control_Caracteres_Dia.get()) == 2 and self.control_Caracteres_Dia.get() != 'dd' and self.dia.index(tk.INSERT) == 2: # Cuando la cadena alcanza el límite indicado establece el foco en otro Widget.
      if self.mes == "": # Si el Entry "mes" está vacio solo realiza el focus()
        self.mes.focus() # Enfoca el indicador del teclado al Entry "mes"
      else:
        self.mes.focus() # Si el Entry "mes" tiene algún contenido realiza el focus() y luego ubica al puntero se inserción en el inicio.
        self.mes.icursor(0)

  def valida_Tamanio_Mes(self, *args): # Cuenta la cantidad de caracteres ingresados
    self.mes.configure(foreground='black') # Establece el color de letra a negro.
    if self.control_Caracteres_Mes.get() == 'mm': # Si la cadena ingresada es el "Placeholder" no hace nada.
      return "break"
    elif len(self.control_Caracteres_Mes.get()) <= 2: # Si la cadena ingresada tiene menos de 3 carácteres los guarda
      self.contenido_Mes = self.control_Caracteres_Mes.get()
    elif len (self.control_Caracteres_Mes.get()) > 2:
      self.control_Caracteres_Mes.set(self.contenido_Mes) # Si la cadena tiene más de dos carácteres carga la cadena guardada previamente.
      self.mes.icursor(self.mes.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve
      self.mes.bell() # Al cumplirse la condición genera el sonido de una campana
    
    if any(char.isalpha() or not char.isalnum() for char in self.control_Caracteres_Mes.get()): #Impide que el usuario ingrese un carácter no numérico.
      self.control_Caracteres_Mes.set(sub(r'\D', '', self.control_Caracteres_Mes.get())) # Actualiza el Entry sin incluir el carácter no numérico.
      self.mes.bell() # Al cumplirse la condición genera el sonido de una campana
    
    # Cuando la cadena alcanza el límite indicado y cumple la condición de tener el cursor en la posición 2 establece el foco en otro Widget.
    if len(self.control_Caracteres_Mes.get()) == 2 and self.control_Caracteres_Mes.get() != 'mm' and self.mes.index(tk.INSERT) == 2: 
      if self.anio == "": # Si el Entry "anio" está vacio solo realiza el focus().
        self.anio.focus() # Enfoca el indicador del teclado al Entry "anio"
      else:
        self.anio.focus() # Si el Entry "anio" tiene algún contenido realiza el focus() y luego ubica al puntero se inserción en el inicio.
        self.anio.icursor(0)

  def valida_Tamanio_Anio(self, *args): # Cuenta la cantidad de caracteres ingresados
    self.anio.configure(foreground = 'black') # Establece el color de letra a negro.
    if self.control_Caracteres_Anio.get() == 'yyyy': # Si la cadena ingresada es el "Placeholder" no hace nada.
      return "break"
    elif len (self.control_Caracteres_Anio.get()) <= 4: # Si la cadena ingresada tiene menos de 5 carácteres los guarda
      self.contenido_Anio = self.control_Caracteres_Anio.get()
    elif len (self.control_Caracteres_Anio.get()) > 4: # Si la cadena tiene más de 4 carácteres carga la cadena guardada previamente.
      self.control_Caracteres_Anio.set(self.contenido_Anio)
      self.anio.icursor(self.anio.index(tk.INSERT) - 1) # Coloca el cursor en la posición inmediatamente anterior, dando la aparencia de que no se mueve
      self.anio.bell() # Al cumplirse la condición genera el sonido de una campana

    if any(char.isalpha() or not char.isalnum() for char in self.control_Caracteres_Anio.get()): #Impide que el usuario ingrese un carácter no numérico.
      self.control_Caracteres_Anio.set(sub(r'\D', '', self.control_Caracteres_Anio.get())) # Actualiza el Entry sin incluir el carácter no numérico.
      self.anio.bell() # Al cumplirse la condición genera el sonido de una campana
  
  def valida_Fecha(self, fecha_texto):
    partes = fecha_texto.split('/')

    if len(partes) != 3:
      return False  # La fecha no tiene el formato correcto
    
    try:
      partes_Enteras = [int(elemento) for elemento in partes]
      fecha = datetime(partes_Enteras[2], partes_Enteras[1], partes_Enteras[0]).date()
      if(date.today() < fecha):
        return False
      
      dia = partes_Enteras[0]
      mes = partes_Enteras[1]
      anio = partes_Enteras[2]

      if anio <= 2015:
        return False

      # Validar el año
      if not (str(dia).isdigit() and str(mes).isdigit() and str(anio).isdigit()):
          return False  # Los componentes no son números

      if mes < 1 or mes > 12:
        return False  # Mes fuera de rango

      dias_Por_Mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

      # Verificar si es año bisiesto
      if mes == 2 and ((anio % 4 == 0 and anio % 100 != 0) or (anio % 400 == 0)):
        dias_Por_Mes[1] = 29

      if dia < 1 or dia > dias_Por_Mes[mes - 1]:
        return False  # Día fuera de rango para el mes dado

      return True  # La fecha es válida
    except:
       return False

  # Validar existencia de un icono
  def valida_Icono (self):
    icono_Kirby = self.path + "/imgs/kirby.ico"
    if path.exists(icono_Kirby): # Si existe "kirby.ico" lo asocia como el icono del programa.
      self.win.iconbitmap(self.path + "/imgs/kirby.ico")
    else: # Si no existe ninguno de los dos iconos, no hace nada, es decir, mantiene el icono por defecto de "tkinter".
      pass  

  # Eventos
  def limpiar_Placeholder_Dia(self, event):
    if self.dia.get() == "dd":
      self.dia.delete(0, 'end')
      self.dia.configure(foreground="black")

  def restore_Placeholder_Dia(self, event):
    if self.dia.get() == "":
      self.dia.insert(0, "dd")
      self.dia.configure(foreground="gray")

  def limpiar_Placeholder_Mes(self, event):
    if self.mes.get() == "mm":
      self.mes.delete(0, 'end')
      self.mes.configure(foreground="black")

  def restore_Placeholder_Mes(self, event):
    if self.mes.get() == "":
      self.mes.insert(0, "mm")
      self.mes.configure(foreground="gray")

  def limpiar_Placeholder_Anio(self, event):
    if self.anio.get() == "yyyy":
      self.anio.delete(0, 'end')
      self.anio.configure(foreground="black")

  def restore_Placeholder_Anio(self, event):
    if self.anio.get() == "":
      self.anio.insert(0, "yyyy")
      self.anio.configure(foreground="gray")

  def backspace_Anio(self, event):
    if self.control_Caracteres_Anio.get() == "" and self.control_Caracteres_Mes.get() == "mm": # Cuando "anio" queda vacio y "mes" es igual a "mm", solo enfoca en el Entry "mes".
      self.mes.focus() # Al cumplirse la condición genera el sonido de una campana
    elif self.control_Caracteres_Anio.get() == "" and self.control_Caracteres_Mes.get() != 'mm': # Cuando "anio" queda vacio y "mes" es diferente a "mm" elimina el último carácter en el Entry "mes"
      self.control_Caracteres_Mes.set(self.control_Caracteres_Mes.get()[:-1])
      self.mes.focus() # Al cumplirse la condición genera el sonido de una campana

  def backspace_Mes(self, event):
    if self.control_Caracteres_Mes.get() == "" and self.control_Caracteres_Dia.get() == "dd": # Cuando "mes" queda vacio y "dia" es igual a "dd", solo enfoca en el Entry "dia".
      self.dia.focus() # Al cumplirse la condición genera el sonido de una campana
    elif self.control_Caracteres_Mes.get() == "" and self.control_Caracteres_Dia.get() != "dd": # Cuando "mes" queda vacio y "dia" es diferente a "dd" elimina el último carácter en el Entry "dia"
      self.control_Caracteres_Dia.set(self.control_Caracteres_Dia.get()[:-1])
      self.dia.focus() # Al cumplirse la condición genera el sonido de una campana
        
  def right_Dia (self, event):
    if self.dia.get() == "": # Si el Entry se encuentra vacio, salta al siguiente Entry.
      self.mes.focus()
      self.mes.select_range(0, tk.END) # Selecciona un rango, de manera que el usuario puede eliminar todo el contenido.
    elif len(self.dia.get()) == 1: # Si el Entry solo tiene un carácter, salta al siguiente Entry.
      self.mes.focus()
      self.mes.select_range(0, tk.END) # Selecciona un rango, de manera que el usuario puede eliminar todo el contenido.
    elif self.dia.index(tk.INSERT) == 2: # Si el cursor se encuentra en la posición 2, enfoca el sigueinte Entry.
      self.mes.focus()
      self.mes.select_range(0, tk.END) # Selecciona un rango, de manera que el usuario puede eliminar todo el contenido.

  def right_Mes (self, event):
    if self.mes.get() == "": # Si el Entry se encuentra vacio, salta al siguiente Entry.
      self.anio.focus()
      self.anio.select_range(0, tk.END) # Selecciona un rango, de manera que el usuario puede eliminar todo el contenido.
    elif len(self.mes.get()) == 1: # Si el Entry solo tiene un carácter, salta al siguiente Entry.
      self.anio.focus()
      self.anio.select_range(0, tk.END) # Selecciona un rango, de manera que el usuario puede eliminar todo el contenido.
    elif self.mes.index(tk.INSERT) == 2: # Si el cursor se encuentra en la posición 2, enfoca el sigueinte Entry.
      self.anio.focus()
      self.anio.select_range(0, tk.END) # Selecciona un rango, de manera que el usuario puede eliminar todo el contenido.

  def left_Mes (self, event):
    if self.mes.index(tk.INSERT) == 0:
      self.dia.focus()
      self.dia.select_range(0, tk.END) # Selecciona un rango, de manera que el usuario puede eliminar todo el contenido.

  def left_Anio (self, event):
    if self.anio.index(tk.INSERT) == 0:
      self.mes.focus()
      self.mes.select_range(0, tk.END) # Selecciona un rango, de manera que el usuario puede eliminar todo el contenido.
        
  #Deshabilitar de Ctr+V
  def deshabilitar_Pegado (self, event):
    return "break" #Cuando el evento se cumple, anula la acción de pegado.

  #Rutina de limpieza de datos
  def limpia_Campos(self):
      ''' Limpia todos los campos de captura'''
      self.actualiza = False
      self.id_Nit.config(state='normal')
      self.codigo.config(state='normal')
      self.razon_Social.config(state = 'normal')
      self.ciudad.config(state = 'normal')
      self.descripcion.config(state = 'normal')
      self.unidad.config(state = 'normal')
      self.cantidad.config(state = 'normal')
      self.precio.config(state = 'normal')
      self.dia.config(state = 'normal', foreground="gray")
      self.mes.config(state = 'normal', foreground="gray")
      self.anio.config(state = 'normal', foreground="gray")
      self.id_Nit.delete(0,'end')
      self.razon_Social.delete(0,'end')
      self.ciudad.delete(0,'end')
      self.id_Nit.delete(0,'end')
      self.codigo.delete(0,'end')
      self.descripcion.delete(0,'end')
      self.unidad.delete(0,'end')
      self.cantidad.delete(0,'end')
      self.precio.delete(0,'end')
      self.dia.delete(0,'end')
      self.mes.delete(0,'end')
      self.anio.delete(0,'end')

      if self.buscando:
        tabla_Tree_View = self.tree_Productos.get_children()
        for linea in tabla_Tree_View:
           self.tree_Productos.delete(linea)
        self.lee_Tree_Productos()
        self.buscando = False
      
      self.control_Caracteres_Dia.set("dd") # Inserta el fórmato después de limpiar todos los campos
      self.dia.configure(foreground= "gray")
      self.control_Caracteres_Mes.set("mm")
      self.mes.configure(foreground= "gray")
      self.control_Caracteres_Anio.set("yyyy")
      self.anio.configure(foreground= "gray")
      self.id_Nit.focus()
    
  #Rutina para cargar los datos en el árbol  
  def carga_Datos(self):
    self.id_Nit.insert(0,self.tree_Productos.item(self.tree_Productos.selection())['text'])
    self.id_Nit.configure(state = 'readonly')
    self.razon_Social.insert(0,self.tree_Productos.item(self.tree_Productos.selection())['values'][0])
    self.unidad.insert(0,self.tree_Productos.item(self.tree_Productos.selection())['values'][3])

  # Operaciones con la base de datos
  def run_Query(self, query, parametros = ()):
    ''' Función para ejecutar los Querys a la base de datos '''
    with sqlite3.connect(self.db_Name) as conn:
        cursor = conn.cursor()
        result = cursor.execute(query, parametros)
        conn.commit()
    return result
  
  # Función que valida si existe la tabla Inventario
  def verificar_Existencia_Tabla_Inventario(self, ruta_base_datos):
    try:
        # Conectar a la base de datos
        conexion = sqlite3.connect(ruta_base_datos)
        cursor = conexion.cursor()

        # Consulta para verificar la existencia de la tabla "Inventario"
        consulta = "SELECT name FROM sqlite_master WHERE type='table' AND name='Inventario'"

        # Ejecutar la consulta
        cursor.execute(consulta)
        resultado = cursor.fetchone()

        # Verificar el resultado
        if resultado:
          return True
        else:
          return False

    except sqlite3.Error as error:
        mssg.showerror("Error", f"Error al conectar a la base de datos: {error}")

    finally:
        # Cerrar la conexión
        if conexion:
          conexion.close()

  def lee_Tree_Productos(self):
    ''' Carga los datos y Limpia la Tabla tabla_Tree_View '''
    tabla_TreeView = self.tree_Productos.get_children()
    for linea in tabla_TreeView:
        self.tree_Productos.delete(linea) # Límpia la filas del TreeView
    
    if self.verificar_Existencia_Tabla_Inventario(self.db_Name) == False:
        # Si la tabla no existe, la creamos y ejecutamos el query
        query_Create_Table = '''
           CREATE TABLE Inventario (
              IdNit VARCHAR(15),
              Codigo VARCHAR(15) NOT NULL,
              Descripcion VARCHAR,
              Und VARCHAR(10),
              Cantidad DOUBLE,
              Precio DOUBLE,
              Fecha DATE,
              PRIMARY KEY (IdNit, Codigo)
          )
        '''
        db_Rows = self.run_Query(query_Create_Table)

        query_Create_Table = '''CREATE TABLE "Proveedores" (
             IdNitProv VARCHAR PRIMARY KEY UNIQUE NOT NULL,
             Razon_Social VARCHAR,
             Ciudad VARCHAR
        )'''

        db_Rows = self.run_Query(query_Create_Table).fetchall()

        query_Select = "SELECT * FROM Inventario"
        db_Rows = self.run_Query(query_Select).fetchall()
    else:
        # Si la tabla ya existe, ejecutamos el query y almacenamos los resultados
        query_Select = '''SELECT * FROM Inventario'''
        db_Rows = self.run_Query(query_Select).fetchall()
      
    # Insertando los datos de la BD en treeProductos de la pantalla

    # Seleccionando los datos de la BD
    query = '''SELECT * from Proveedores INNER JOIN Inventario WHERE idNitProv = idNit ORDER BY idNitProv'''
    db_Rows = self.run_Query(query).fetchall()

    for row in db_Rows:
      self.tree_Productos.insert('',0, text = row[0], values = [row[4],row[5],row[6],row[7],row[8],row[9]])
      ''' Al final del for row queda con la última tupla
        y se usan para cargar las variables de captura
      '''

  def adiciona_Registro(self, event=None):
    '''Adiciona un producto a la BD si la validación es True'''
    query_Buscar_Cod_Producto = "SELECT COUNT(*) FROM inventario WHERE codigo = ? AND idNit = ?"
    validacion_Codigo = self.run_Query(query_Buscar_Cod_Producto, (self.codigo.get(),self.id_Nit.get())).fetchone()[0] # Valida si existe un registro con el código del producto

    # Parámetros a insertar (producto)
    valor_Id_Nit = self.id_Nit.get().strip()
    valor_Codigo = self.codigo.get().strip()
    valor_Descripcion = self.descripcion.get().strip()
    valor_Und = self.unidad.get().strip()
    valor_Cantidad = self.cantidad.get().strip()
    valor_Precio = self.precio.get().strip()
    valor_Fecha = f'{self.dia.get().strip()}/{self.mes.get().strip()}/{self.anio.get().strip()}'
    valor_Razon_Social = self.razon_Social.get().strip()
    valor_Ciudad = self.ciudad.get().strip()
             
    if not(valor_Codigo and valor_Descripcion and valor_Und and valor_Cantidad and valor_Precio and valor_Fecha):
       if (valor_Id_Nit  and valor_Razon_Social and valor_Ciudad) and not(valor_Codigo or valor_Descripcion or valor_Und or valor_Cantidad or valor_Precio or valor_Fecha != "dd/mm/yyyy"):
          consulta = f"SELECT COUNT(*) FROM Proveedores WHERE idNitProv = ?"
          if self.run_Query(consulta, (valor_Id_Nit,)).fetchone()[0]:
            query_Actualizar_Proveedor = '''
            UPDATE Proveedores
            SET Razon_Social = ?, Ciudad = ?
            WHERE IdNitProv = ?
            '''
            self.run_Query(query_Actualizar_Proveedor, (valor_Razon_Social, valor_Ciudad, valor_Id_Nit))
            mssg.showinfo("Información", f"El proveedor {valor_Id_Nit} fue actualizado exitosamente")
            self.limpia_Campos()
            return
          else:
             consulta = '''INSERT INTO Proveedores (IdNitProv, Razon_Social, Ciudad)
                        VALUES (?, ?, ?)
                        '''
             self.run_Query(consulta, (valor_Id_Nit, valor_Razon_Social, valor_Ciudad))
             mssg.showinfo("Información", "El proveedor fue creado exitosamente")
             self.limpia_Campos()
             return
       else:
        mssg.showerror('Error', 'Ningún campo puede estar vacío')
        return
    
    if not(self.valida_Fecha(valor_Fecha)):
        mssg.showerror('Error', 'La fecha ingresada es inválida.')
        return
    
    if(valor_Codigo.isdigit() and valor_Codigo.startswith('0')):
      mssg.showerror("Error", "El código no puede ser un número e iniciar en 0")
      return

    if(valor_Id_Nit.isdigit() and valor_Id_Nit.startswith('0')):
      mssg.showerror("Error", "El Id/Nit no puede ser un número e iniciar en 0")
      return
    
    if(validacion_Codigo == 1):

       if self.actualiza:
        # Actualizar el registro existente en la base de datos
        query_Actualizar_Producto = '''
        UPDATE Inventario
        SET Descripcion = ?, Und = ?, Cantidad = ?, Precio = ?, Fecha = ?
        WHERE Codigo = ?
        '''
        parametros_Actualizar_Producto = (valor_Descripcion, valor_Und, valor_Cantidad, valor_Precio, valor_Fecha, valor_Codigo)
        self.run_Query(query_Actualizar_Producto, parametros_Actualizar_Producto)

        # Actualizar el proveedor si es necesario
        valor_Razon_Social = self.razon_Social.get()
        valor_Ciudad = self.ciudad.get()
        query_Actualizar_Proveedor = '''
        UPDATE Proveedores
        SET Razon_Social = ?, Ciudad = ?
        WHERE IdNitProv = ?
        '''
        parametros_Actualizar_Proveedor = (valor_Razon_Social, valor_Ciudad, valor_Id_Nit)

        self.run_Query(query_Actualizar_Proveedor, parametros_Actualizar_Proveedor)

        # Actualiza la fila correspondiente en el TreeView
        fila_seleccionada = self.tree_Productos.selection()
        if fila_seleccionada:
            self.tree_Productos.item(fila_seleccionada, values=(valor_Codigo, valor_Descripcion, valor_Und, valor_Cantidad, valor_Precio, valor_Fecha))
        
        mssg.showinfo("Información", "El registro fue actualizado exitosamente")
      
       else:
         mssg.showerror('Error', 'El código del producto debe ser único')
         return
    else:

      query_Crear_Producto = '''
      INSERT INTO Inventario (IdNit, Codigo, Descripcion, Und, Cantidad, Precio, Fecha)
      VALUES (?, ?, ?, ?, ?, ?, ?)
      '''
      parametros_Producto = (valor_Id_Nit, valor_Codigo, valor_Descripcion, valor_Und, valor_Cantidad, valor_Precio, valor_Fecha)

      self.run_Query(query_Crear_Producto, parametros_Producto)

      # Parámetros a insertar (proveedor)

      query_Buscar_Cod_Proveedor = "SELECT COUNT(*) FROM Proveedores WHERE IdNitProv = ?"
      validacion_Proveedor = self.run_Query(query_Buscar_Cod_Proveedor, (self.id_Nit.get(),)).fetchone()[0] # Valida si existe un registro con el código del producto

      if(validacion_Proveedor == 0): # Valida si existe el proveedor. Si no existe, lo crea
        valor_Razon_Social = self.razon_Social.get().strip()
        valor_Ciudad = self.ciudad.get().strip()

        query_Crear_Proveedor = '''
        INSERT INTO Proveedores (IdNitProv, Razon_Social, Ciudad)
        VALUES (?, ?, ?)
        '''

        parametros_Proveedor = (valor_Id_Nit, valor_Razon_Social, valor_Ciudad)

        self.run_Query(query_Crear_Proveedor, parametros_Proveedor)

      self.tree_Productos.insert('',0, text = valor_Id_Nit, values = [valor_Codigo,valor_Descripcion,valor_Und,valor_Cantidad,valor_Precio,valor_Fecha])
      mssg.showinfo("Información", "El registro fue creado exitosamente")
    
    self.limpia_Campos() # Limpia todos los campos de los Entry
    self.id_Nit.focus() # Vuelve a inicializar el foco en el Entre "Id/Nit"
    
  def edita_Tree_Proveedores(self, event=None):
    ''' Edita una tupla del TreeView'''
    seleccion = self.tree_Productos.selection()
    if seleccion:
        self.actualiza = True
        # Obtener los datos de la fila seleccionada
        fila = self.tree_Productos.item(seleccion)
        id_Nit = fila['text']
        codigo = fila["values"][0]

        self.id_Nit.config(state="normal")
        # Cargar los datos en los campos de entrada
        self.id_Nit.delete(0, 'end')
        self.id_Nit.insert(0, id_Nit)

        
        self.razon_Social.config(state = 'normal')
        self.ciudad.config(state = 'normal')
        self.descripcion.config(state = 'normal')
        self.unidad.config(state = 'normal')
        self.cantidad.config(state = 'normal')
        self.precio.config(state = 'normal')
        self.dia.config(state = 'normal', foreground="black")
        self.mes.config(state = 'normal', foreground="black")
        self.anio.config(state = 'normal', foreground="black")

        # Obtener los datos de Razón Social y Ciudad desde la tabla de Proveedores
        query_Proveedor = "SELECT Razon_Social, Ciudad FROM Proveedores WHERE IdNitProv = ?"
        datos_Proveedor = self.run_Query(query_Proveedor, (id_Nit,)).fetchone()
        query_Producto = "SELECT Codigo, Descripcion, Und, Cantidad, Precio, Fecha FROM Inventario WHERE Codigo = ? AND IdNit = ?"
        datos_Producto = self.run_Query(query_Producto, (codigo, id_Nit)).fetchone()

        if datos_Proveedor:
           razon_social, ciudad = datos_Proveedor
           self.razon_Social.delete(0, 'end')
           self.razon_Social.insert(0, razon_social)
           self.ciudad.delete(0, 'end')
           self.ciudad.insert(0, ciudad)

        if datos_Producto:
           self.codigo.config(state="normal")
           codigo, descripcion, und, cantidad, precio, fecha = datos_Producto
           self.codigo.delete(0, 'end')
           self.codigo.insert(0, codigo)
           self.descripcion.delete(0, 'end')
           self.descripcion.insert(0, descripcion)
           self.unidad.delete(0, 'end')
           self.unidad.insert(0, und)
           self.cantidad.delete(0, 'end')
           self.cantidad.insert(0, cantidad)
           self.precio.delete(0, 'end')
           self.precio.insert(0, precio)
           self.dia.delete(0, 'end')
           self.mes.delete(0, 'end')
           self.anio.delete(0, 'end')
           self.dia.insert(0, fecha.split("/")[0])
           self.mes.insert(0, fecha.split("/")[1])
           self.anio.insert(0, fecha.split("/")[2])
        self.id_Nit.config(state="disabled")
        self.codigo.config(state="disabled")
        self.razon_Social.focus() # Carga la información del producto y enfoca el cursor en el Entry "razon_Social"      
        self.razon_Social.icursor(0) # Ubica el cursor en la posición 0 del Entry.
    else:
       mssg.showerror("Error", "Ningún registro seleccionado")
  
  def elimina_Registro(self, event=None):
    '''Elimina un Registro en la BD'''
    seleccion = self.tree_Productos.selection()
    if seleccion:
      fila = self.tree_Productos.item(seleccion)
      custom_Ask = Ventana_De_Pregunta(self.win)
      self.win.wait_window(custom_Ask.popup)
      if custom_Ask.result == "proveedor":
        proveedor = fila['text']
        opcion = mssg.askquestion("Eliminar", f"¿Desea eliminar el proveedor con el ID/NIT: {proveedor}?")
        if opcion == "yes":
          delete_Products_Query = f"DELETE FROM inventario WHERE IdNit = ?"
          self.run_Query(delete_Products_Query, (proveedor,))
          delete_Prov_Query = f"DELETE FROM proveedores WHERE IdNitProv = ?"
          self.run_Query(delete_Prov_Query, (proveedor,))
          for child in self.tree_Productos.get_children():
            if self.tree_Productos.item(child)['text'] == proveedor:
              self.tree_Productos.delete(child)
              self.limpia_Campos() # Limpia todos los campos de los Entry.
          mssg.showinfo("Información", "El proveedor fue eliminado exitosamente.")

      elif custom_Ask.result == "producto":
        producto_seleccionado = fila['values'][1]
        codigo = fila['values'][0]
        opcion = mssg.askquestion("Eliminar", f"¿Desea eliminar el producto: {producto_seleccionado}?")
        if opcion ==  "yes":
            self.tree_Productos.delete(seleccion)
            query_Delete = "DELETE FROM Inventario WHERE Codigo = ?"
            self.run_Query(query_Delete, (codigo,))
            self.limpia_Campos() # Limpia todos los campos de los Entry.
            mssg.showinfo("Información", "El producto fue eliminado exitosamente.")
            return
    else:
      mssg.showerror("Error", "Ningún registro seleccionado")
      self.id_Nit.focus()
        
  def buscarPorIdNit_Codigo(self, event=None):

    ''' Busca productos por el IdNit ingresado '''
    id_Nit = self.id_Nit.get()
    codigo = self.codigo.get()
    self.limpia_Campos()
    self.buscando = True
    self.id_Nit.insert(0, str(id_Nit))
    self.codigo.insert(0, str(codigo))

    if id_Nit == "" and codigo == "":
       mssg.showerror("Error", "Debes ingresar un Id/Nit o un Código")
       return
    
    else:
      if id_Nit != "" and codigo != "":
        query = "SELECT * FROM Inventario WHERE IdNit LIKE ? AND Codigo LIKE ?"
        resultados = self.run_Query(query, ('%'+id_Nit+'%', '%'+codigo+'%')).fetchall()

        if not resultados:
            mssg.showinfo("Información", "No se encontró ningún proveedor con ese IdNit y código especificados")
            return

        '''Deshabilitar la opción de escribir'''
        self.descripcion.config(state="disabled")
        self.unidad.config(state="disabled")
        self.cantidad.config(state="disabled")
        self.precio.config(state="disabled")
        self.dia.config(state="disabled")
        self.mes.config(state="disabled")
        self.anio.config(state="disabled")
        self.razon_Social.config(state="disabled")
        self.ciudad.config(state="disabled")

        ''' Limpia la tabla de productos '''
        tabla_Tree_View = self.tree_Productos.get_children()
        for linea in tabla_Tree_View:
            self.tree_Productos.delete(linea)
        for row in resultados:
            self.tree_Productos.insert('', 0, text=row[0], values=[row[1], row[2], row[3], row[4], row[5], row[6]])
      
      elif id_Nit != "":
        query = "SELECT * FROM Inventario WHERE IdNit LIKE ?"    
        resultados = self.run_Query(query, ('%'+id_Nit+'%',)).fetchall()

        if not resultados: 
          mssg.showinfo("Información", "No se encontro ningún proveedor con ese IdNit")
          return

        '''Deshabilitar la opción de escribir'''
        self.codigo.config(state="disabled")
        self.descripcion.config(state="disabled")
        self.unidad.config(state="disabled")
        self.cantidad.config(state="disabled")
        self.precio.config(state="disabled")
        self.dia.config(state="disabled")
        self.mes.config(state="disabled")
        self.anio.config(state="disabled")
        self.razon_Social.config(state="disabled")
        self.ciudad.config(state="disabled")

        ''' Limpia la tabla de productos '''
        tabla_Tree_View = self.tree_Productos.get_children()
        for linea in tabla_Tree_View:
            self.tree_Productos.delete(linea)

        for row in resultados:
          self.tree_Productos.insert('',0, text = row[0], values = [row[1],row[2],row[3],row[4],row[5],row[6]])

      elif codigo != "":
        query = "SELECT * FROM Inventario WHERE Codigo LIKE ?"    
        resultados = self.run_Query(query, ('%'+codigo+'%',)).fetchall()

        if not resultados: 
          mssg.showinfo("Información", "No se encontro ningún producto con ese Código")
          return

        '''Deshabilitar la opción de escribir'''
        self.id_Nit.config(state="disabled")
        self.descripcion.config(state="disabled")
        self.unidad.config(state="disabled")
        self.cantidad.config(state="disabled")
        self.precio.config(state="disabled")
        self.dia.config(state="disabled")
        self.mes.config(state="disabled")
        self.anio.config(state="disabled")
        self.razon_Social.config(state="disabled")
        self.ciudad.config(state="disabled")

        ''' Limpia la tabla de productos '''
        tabla_Tree_View = self.tree_Productos.get_children()
        for linea in tabla_Tree_View:
            self.tree_Productos.delete(linea)

        for row in resultados:
          self.tree_Productos.insert('',0, text = row[0], values = [row[1],row[2],row[3],row[4],row[5],row[6]])


if __name__ == "__main__":
    app = Inventario()
    app.run()