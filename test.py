# .py para poder tener un mejor debug de los algoritmos. Este .py se basa en Reto v0.0.PATO.ipynb

# Omitiré mucho del código comentado ya que solo dificulta la legibilidad de este .py

# Imports
from mesa import Agent, Model
from mesa.time import RandomActivation

# MultiGrid es una grilla que permite múltiples agentes por celda, por lo que me decantaré por 
# esta para poder tener un despliegue inicial

from mesa.space import MultiGrid
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import heapq
import random
plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128
import pandas as pd
from mesa.datacollection import DataCollector
from IPython.display import HTML
import heapq
import numpy as np
import networkx as nx

def leer_mapa(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        mapaREAL = [list(line.replace(" ", "").strip()) for line in lines[1:]]

    filas = len(mapaREAL)
    columnas = len(mapaREAL[0])

    mapa = [fila[:] for fila in mapaREAL]  # Crear una copia de mapaREAL

    for i in range(filas):
        for j in range(columnas):
            if mapaREAL[i][j] not in ['S', 'P']:
                mapa[i][j] = '?'

    
#    SE IMPRIMEN LOS MAPAS EN TERMINAL
    print("MapaREAL:")
    for fila in mapaREAL:
        print(' '.join(fila))
    
    print("Mapa:")
    for fila in mapa:
        print(' '.join(fila))
    
    return mapaREAL, mapa

# Se definen agentes

class Robot(Agent):
    def __init__(self, unique_id, model, inicio):
        super().__init__(unique_id, model)
        self.posicion = inicio
        self.capacidad = 5
        self.model.memoria[inicio] = 'S'
        self.basura_no_recogida = None
        self.destinos_pendientes = [0]

    def step(self):
        self.mapeo()
        self.moverse()
        print("Ahora estoy en la posición:")
        print(self.posicion)

    def mapeo(self):
        print("Estoy mapeando chucuchú")
        if self.model.memoria[self.posicion] == 'B':
            print("Exploro detalles VAMOOOS")
            self.explorar_detalle()

        self.model.memoria[self.posicion] = self.model.mapaREAL[self.posicion[0]][self.posicion[1]] 

        # Actualizar mapa con información del mapaREAL
        self.model.mapa[self.posicion[0]][self.posicion[1]] = self.model.mapaREAL[self.posicion[0]][self.posicion[1]]

        # Actualizar memoria con información del entorno
        vecinos = self.model.grid.get_neighborhood(self.posicion, moore=True, include_center=True)
        for vecino in vecinos:
            print(f"Analizando vecino: {vecino}")
            contenido = self.model.mapa[vecino[1]][vecino[0]]  # Corrección aquí
            print(f"Contenido: {contenido}")
            if contenido == 'X':
                self.model.memoria[vecino] = 'X'
            if contenido.isdigit() and contenido != '0':
                self.model.memoria[vecino] = 'B'
            elif contenido == '0':
                self.model.memoria[vecino] = '0'

        # Actualizar celda actual en la grid
        self.model.grid[self.posicion[0]][self.posicion[1]] = self.model.memoria[self.posicion]


    def explorar_detalle(self):
        contenido = self.model.mapa[self.posicion[0]][self.posicion[1]]
    
        if contenido.isdigit():
            print(f"Se reveló que hay {contenido} de basura en esta celda.")
            valor_basura = int(contenido)
            self.model.memoria[self.posicion] = valor_basura
            self.model.mapa[self.posicion[0]][self.posicion[1]] = str(valor_basura)  # Actualiza también en el mapa
            self.model.grid[self.posicion[0]][self.posicion[1]] = str(valor_basura)  # Actualiza también en la grid
            print(self.model.memoria)
        else:
            print("No se reveló nada nuevo en esta celda.")
        
                
    
    def obtener_vecinos_conocidos(self):
        vecinos = self.model.grid.get_neighborhood(self.posicion, moore=True, include_center=False)
        vecinos_conocidos = [vecino for vecino in vecinos if vecino in self.model.memoria and self.model.memoria[vecino] != '?']
        return vecinos_conocidos
        
    def moverse(self):
        print("Si me muevo")
        destino = self.destinos_pendientes[0]
        if self.posicion == destino:
            self.destinos_pendientes.pop(0)
            return

        ruta = self.planificar_ruta(destino)
        print("Imprimo la ruta")
        print(ruta)
        siguiente_celda = ruta[0]
        self.posicion = siguiente_celda
        
        
    def planificar_ruta(self, destino):
        pila = [(self.posicion, [])]  # Pila para el DFS
        visitados = set()

        while pila:
            celda_actual, ruta_actual = pila.pop()
            if celda_actual == destino:
                return ruta_actual

            if celda_actual in visitados:
                continue

            visitados.add(celda_actual)
            vecinos_conocidos = self.obtener_vecinos_conocidos()
            vecinos_libres = [vecino for vecino in vecinos_conocidos if self.model.memoria[vecino] != 'X']

            if not vecinos_libres:  # Si no hay vecinos libres, retrocede
                if ruta_actual:
                    retroceder = ruta_actual[-1]  # Retrocede al último punto
                    pila.append((retroceder, ruta_actual[:-1]))  # Elimina el último paso de la ruta
            else:
                siguiente_celda = vecinos_libres[0]
                pila.append((siguiente_celda, ruta_actual + [siguiente_celda]))
                
        print("Vecinos libres:")
        print(vecinos_libres)
        vecinos_libres.pop(0)

        return vecinos_libres
    
# Se importa el modelo

class LimpiezaModel(Model):
    def __init__(self, mapa_txt):
        super().__init__(self)
        self.datacollector = DataCollector(
            model_reporters={"Mapa": "mapa"},
            agent_reporters={"Posicion": "posicion"})
        self.mapa, self.mapaREAL = leer_mapa(mapa_txt)
        self.mapa = [fila[:] for fila in self.mapa]  # Copia del mapa desconocido
        self.num_robots = 1
        self.grid = MultiGrid(len(self.mapa), len(self.mapa[0]), torus=False)
        self.schedule = RandomActivation(self)
        self.bote_basura = ()
        self.basura = ()
        self.obstaculo = ()
        self.memoria = {}
        self.todas_celdas_mapeadas = 1

        # Creación de robots
        for i in range(self.num_robots):
            robot = Robot(i, self, (0, 0))
            self.schedule.add(robot)
    
            self.grid.place_agent(robot, (0, 0))
            
    def step(self):
        print("Paso")   
        self.schedule.step()
        print("La memoria que se tiene es:")
        print(self.memoria)
    
model = LimpiezaModel('mapa.txt')

steps = 4
for i in range(steps): 
    model.step()
