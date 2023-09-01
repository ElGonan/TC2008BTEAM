from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import heapq
import random
import os

# Obtener la ubicación del directorio actual del script
script_dir = os.path.dirname(__file__)

# Construir la ruta completa al archivo 'mapa.txt'
mapa_file = os.path.join(script_dir, 'mapa.txt')
plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128
import pandas as pd
from mesa.datacollection import DataCollector
from IPython.display import HTML
import heapq
import numpy as np
import networkx as nx

# ESTE COMANDO ES PARA LOS PRINTS, PARA VER QUE SALGAN CORRECTO Y ASÍ, ELIMINAR AL FINALIZAR
from IPython.display import display

def leer_mapa(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        mapaREAL = [list(line.replace(" ", "").strip()) for line in lines[1:]]

    filas = len(mapaREAL)
    columnas = len(mapaREAL[0])

    mapaUNKNOWN = [fila[:] for fila in mapaREAL]  # Crear una copia de mapaREAL

    for i in range(filas):
        for j in range(columnas):
            if mapaREAL[i][j] not in ['S', 'P']:
                mapaUNKNOWN[i][j] = '?'
    
    
#    SE IMPRIMEN LOS MAPAS EN TERMINAL
#
#    print("MapaREAL:")
#    for fila in mapaREAL:
#        print(' '.join(fila))
#    
#    print("MapaUNKNOWN:")
#    for fila in mapaUNKNOWN:
#        print(' '.join(fila))
    
    return mapaREAL, mapaUNKNOWN


class Robot(Agent):
    def __init__(self, unique_id, model, inicio, mapaREAL, mapaUNKNOWN):
        super().__init__(unique_id, model)
        self.posicion = inicio
        self.capacidad = 5
        self.memoria = {}
        self.memoria[inicio] = 'S'
        self.basura_no_recogida = None
        self.destinos_pendientes = [0]


    def step(self):
        self.mapeo()
        self.moverse()
        print("Ahora estoy en la posición:")
        print(self.posicion)
        print("Mi memoria es:")
        print(self.memoria)

    def mapeo(self):
        print("Estoy mapeando chucuchú")
        if self.memoria[self.posicion] == 'B':
            print("Exploro detalles VAMOOOS")
            self.explorar_detalle()

        self.memoria[self.posicion] = self.model.mapaREAL[self.posicion[0]][self.posicion[1]] 

        # Actualizar mapaUNKNOWN con información del mapaREAL
        self.model.mapaUNKNOWN[self.posicion[0]][self.posicion[1]] = self.model.mapaREAL[self.posicion[0]][self.posicion[1]]

        # Actualizar memoria con información del entorno
        vecinos = self.model.grid.get_neighborhood(self.posicion, moore=True, include_center=True)
        for vecino in vecinos:
        #    print(f"Analizando vecino: {vecino}")
            contenido = self.model.mapaUNKNOWN[vecino[1]][vecino[0]]  # Corrección aquí
        #    print(f"Contenido: {contenido}")
            if contenido == 'X':
                self.memoria[vecino] = 'X'
            if contenido == '0':
                self.memoria[vecino] = '0'
            if contenido.isdigit():
                self.memoria[vecino] = 'B'
            else:
                self.memoria[vecino] = contenido

        # Actualizar celda actual en la grid
        self.model.grid[self.posicion[0]][self.posicion[1]] = self.memoria[self.posicion]


    def explorar_detalle(self):
        contenido = self.model.mapa[self.posicion[0]][self.posicion[1]]
    
        if contenido == 'X':
            print("Se reveló que hay un obstáculo en esta celda.")
            self.memoria[self.posicion] = 'X'
        elif contenido.isdigit():
            print(f"Se reveló que hay {contenido} de basura en esta celda.")
            valor_basura = int(contenido)
            self.memoria[self.posicion] = valor_basura
            self.model.mapa[self.posicion[0]][self.posicion[1]] = str(valor_basura)  # Actualiza también en el mapa
            self.model.grid[self.posicion[0]][self.posicion[1]] = str(valor_basura)  # Actualiza también en la grid
            print(self.memoria)
        else:
            print("No se reveló nada nuevo en esta celda.")
                
    
    def obtener_vecinos_conocidos(self):
        vecinos = self.model.grid.get_neighborhood(self.posicion, moore=True, include_center=False)
        vecinos_conocidos = [vecino for vecino in vecinos if vecino in self.memoria and self.memoria[vecino] != '?']
        return vecinos_conocidos
        
    def moverse(self):
        print("Si me muevo")
        destino = self.destinos_pendientes[0]
        if self.posicion == destino:
            self.destinos_pendientes.pop(0)
            return

        ruta = self.planificar_ruta(destino)
        siguiente_celda = ruta[0]
        self.posicion = siguiente_celda
        self.model.grid.move_agent(self, siguiente_celda)
        
    def planificar_ruta(self, destino):
        cola = [(self.posicion, [])]  # Cola para el BFS
        print("Imprimo la cola")
        print(cola)
        visitados = set()

        while cola != []:
            celda_actual, ruta_actual = cola.pop(0)
            if celda_actual == destino:
                print("Imprimo la ruta_actual")
                print(ruta_actual)
                return ruta_actual

            if celda_actual in visitados:
                continue

            visitados.add(celda_actual)
            vecinos_conocidos = self.obtener_vecinos_conocidos()
            vecinos_libres = [vecino for vecino in vecinos_conocidos if self.memoria[vecino] != 'X']

            for vecino in vecinos_libres:
                cola.append((vecino, ruta_actual + [vecino]))
                
        return ruta_actual

class LimpiezaModel(Model):
    def __init__(self, mapa_txt):
        super().__init__(self)
        self.datacollector = DataCollector(
            model_reporters={"Mapa": "mapa"},
            agent_reporters={"Posicion": "posicion"})
        self.num_robots = 1
        self.schedule = RandomActivation(self)
        self.mapaUNKNOWN, self.mapaREAL = leer_mapa(mapa_txt)
        self.grid = SingleGrid(len(self.mapaUNKNOWN), len(self.mapaUNKNOWN[0]), torus=False)
        self.bote_basura = ()
        self.basura = ()
        self.obstaculo = ()
        self.memoria_mapa = {}
        self.todas_celdas_mapeadas = 1

        # self.fig, self.ax = plt.subplots()

        # Creación de robots
        for i in range(self.num_robots):
            robot = Robot(i, self, (0, 0), self.mapaREAL, self.mapaUNKNOWN)
            self.schedule.add(robot)
    
            self.grid.place_agent(robot, (0, 0))

    def step(self):
        print("Paso")   
        self.schedule.step()
        print("MapaUNKNOWN:")
        for fila in self.model.mapaUNKNOWN:
            print(' '.join(fila))
        
model = LimpiezaModel(mapa_file)

steps = 4
for i in range(steps): 
    model.step()