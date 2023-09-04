from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from matplotlib import animation
import heapq
import random
import networkx as nx
from IPython.display import HTML, display
import numpy as np
import matplotlib.pyplot as plt


# Función para leer el mapa desde un archivo de texto.
def leer_mapa(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        mapa = [list(line.replace(" ", "").strip()) for line in lines[1:]]
    return mapa

def construir_grafo(mapa):
    grafo = {}
    filas = len(mapa)
    columnas = len(mapa[0])

    for i in range(filas):
        for j in range(columnas):
            if mapa[i][j] != 'X':  # Si la celda no es un obstáculo.
                nodo = (i, j)
                vecinos = []  # Lista para almacenar vecinos accesibles.

                # Verifica y agrega vecinos accesibles.
                if i - 1 >= 0 and mapa[i-1][j] != 'X': vecinos.append((i-1, j))
                if i + 1 < filas and mapa[i+1][j] != 'X': vecinos.append((i+1, j))
                if j - 1 >= 0 and mapa[i][j-1] != 'X': vecinos.append((i, j-1))
                if j + 1 < columnas and mapa[i][j+1] != 'X': vecinos.append((i, j+1))

                grafo[nodo] = vecinos  # Asigna los vecinos al nodo en el grafo.

    # Vamos a dibujar el grafo para entenderlo:

    G = nx.DiGraph()

    # Agrega los nodos al grafo
    for nodo, vecinos in grafo.items():
        G.add_node(nodo)
        for vecino in vecinos:
            G.add_edge(nodo, vecino)

    # Dibuja el grafo utilizando matplotlib
    pos = {nodo: nodo for nodo in G.nodes()}  # Definir la posición de los nodos para que se dibujen en sus coordenadas
    nx.draw(G, pos, with_labels=True, node_size=1000, font_size=10, node_color='lightblue', font_color='black')

    # Muestra el dibujo del grafo
    plt.show()

    return grafo


def leer_mapa(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        mapa = [list(line.replace(" ", "").strip()) for line in lines[1:]]
    return mapa

def construir_grafo(mapa):
    grafo = {}
    filas = len(mapa)
    columnas = len(mapa[0])

    for i in range(filas):
        for j in range(columnas):
            if mapa[i][j] != 'X':
                nodo = (i, j)
                vecinos = []

                if i - 1 >= 0 and mapa[i-1][j] != 'X': vecinos.append((i-1, j))
                if i + 1 < filas and mapa[i+1][j] != 'X': vecinos.append((i+1, j))
                if j - 1 >= 0 and mapa[i][j-1] != 'X': vecinos.append((i, j-1))
                if j + 1 < columnas and mapa[i][j+1] != 'X': vecinos.append((i, j+1))

                grafo[nodo] = vecinos

    return grafo

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Implementación del algoritmo A*
def a_star_search(graph, start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for next in graph[current]:
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                heapq.heappush(frontier, (priority, next))
                came_from[next] = current

    # Reconstruct path
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path

class Robot(Agent):
    def __init__(self, unique_id, model, inicio):
        super().__init__(unique_id, model)
        self.posicion = inicio
        self.capacidad = 5
        self.memoria = {}
        self.basura_no_recogida = None

    def step(self):
        grafo = self.model.grafo
        mapa = self.model.mapa

        # Encuentra la basura más cercana usando A*
        basura_cercana = None
        camino_corto = None
        for i in range(len(mapa)):
            for j in range(len(mapa[0])):
                if mapa[i][j].isdigit() and int(mapa[i][j]) > 0:
                    camino = a_star_search(grafo, self.posicion, (i, j))
                    if camino_corto is None or len(camino) < len(camino_corto):
                        camino_corto = camino
                        basura_cercana = (i, j)

        if camino_corto is None:  # Añadido para manejar el caso cuando no hay camino a ninguna basura
            print("No se encontró un camino a ninguna basura.")
            return  # Salir del método step

        # Moverse hacia la basura más cercana
        if len(camino_corto) > 1:
            nueva_posicion = camino_corto[1]
            self.posicion = nueva_posicion

            # Recoger basura
            if mapa[nueva_posicion[0]][nueva_posicion[1]].isdigit() and int(mapa[nueva_posicion[0]][nueva_posicion[1]]) > 0:
                basura = min(int(mapa[nueva_posicion[0]][nueva_posicion[1]]), self.capacidad)
                self.capacidad -= basura
                mapa[nueva_posicion[0]][nueva_posicion[1]] = str(int(mapa[nueva_posicion[0]][nueva_posicion[1]]) - basura)

                # Si no pudo recoger toda la basura, almacena la posición
                if int(mapa[nueva_posicion[0]][nueva_posicion[1]]) > 0:
                    self.basura_no_recogida = nueva_posicion

        # Comunicación entre robots
        for agent in self.model.schedule.agents:
            if isinstance(agent, Robot) and agent != self:
                self.memoria.update(agent.memoria)
                agent.memoria.update(self.memoria)

                # Comparte la posición de basura no recogida
                if self.basura_no_recogida:
                    agent.memoria[self.basura_no_recogida] = 'basura_no_recogida'

def update(num, model):
    model.step()

class LimpiezaModel(Model):
    def __init__(self, mapa_txt):
        self.num_robots = 5
        self.schedule = RandomActivation(self)
        self.mapa = leer_mapa(mapa_txt)
        self.grafo = construir_grafo(self.mapa)
        
        # Establecer el tamaño de la figura
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        
        # Desactivar los ejes
        self.ax.axis('off')
        
        # Establecer los límites de los ejes
        self.ax.set_xlim(0, len(self.mapa[0]))
        self.ax.set_ylim(0, len(self.mapa))

        # Creación de robots
        for i in range(self.num_robots):
            robot = Robot(i, self, (0, 0))
            self.schedule.add(robot)

    def step(self):
        self.schedule.step()
        self.draw_map()

    def draw_map(self):
      self.ax.clear()
      self.ax.set_xlim(0, len(self.mapa[0]))  # Ajustar límites del eje X
      self.ax.set_ylim(len(self.mapa), 0)  # Ajustar límites del eje Y
      for i, row in enumerate(self.mapa):
          for j, cell in enumerate(row):
              if cell == 'X':
                  self.ax.text(j, i, cell, ha='center', va='center', fontsize=12, color='black')
              else:
                  self.ax.text(j, i, cell, ha='center', va='center', fontsize=12, color='blue')
      for agent in self.schedule.agents:
          self.ax.text(agent.posicion[1], agent.posicion[0], 'R', ha='center', va='center', fontsize=12, color='red')

def main():
    model = LimpiezaModel('mapa.txt')
    ani = animation.FuncAnimation(model.fig, update, fargs=(model,), frames=100)
    plt.show()

    # Para mostrar la animación como HTML
    html = HTML(ani.to_jshtml())
    display(html)
    

if __name__ == "__main__":
    main()
