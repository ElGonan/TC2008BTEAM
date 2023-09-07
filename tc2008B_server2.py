from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json

#AQUI VA EL CÓDIGO DEL ROOMBA#
from mesa import Agent, Model
from mesa.time import RandomActivation
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import heapq
import random
plt.rcParams["animation.html"] = "jshtml"
matplotlib.rcParams['animation.embed_limit'] = 2**128
import pandas as pd
from mesa.datacollection import DataCollector
from IPython.display import HTML, display
import heapq
import numpy as np
import networkx as nx


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

    return mapaREAL, mapaUNKNOWN

def traducir_mapa(mapaREAL):
    mapa_num = []
    for fila in mapaREAL:
        fila_num = []
        for celda in fila:
            if celda == "S":
                fila_num.append(-1)
            elif celda == "P":
                fila_num.append(-2)
            elif celda == "X":
                fila_num.append(-3)
            elif celda == "B":
                fila_num.append(-4)
            elif celda == "?":
                fila_num.append(-5)
            else:
                fila_num.append(int(celda))
        mapa_num.append(fila_num)
    return mapa_num

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
                
    
        # Vamos a dibujar el grafo para entenderlo:

    G = nx.DiGraph()

    # Agrega los nodos al grafo
    for nodo, vecinos in grafo.items():
        G.add_node(nodo)
        for vecino in vecinos:
            G.add_edge(nodo, vecino)
            
    # Se espejea el dibujo para que Rodri no me esté molestando
    pos = {nodo: (x, -y) for nodo, (x, y) in nx.spring_layout(G).items()}
    
    # Dibuja el grafo utilizando matplotlib
    pos = {nodo: nodo for nodo in G.nodes()}  # Definir la posición de los nodos para que se dibujen en sus coordenadas
    nx.draw(G, pos, with_labels=True, node_size=1000, font_size=10, node_color='lightblue', font_color='black')

    # Rotar el gráfico
    plt.xticks(rotation=90)  # Cambia el ángulo de las etiquetas del eje x (en grados)

    # Iguala el aspecto del gráfico para que las proporciones no se distorsionen
    plt.gca().set_aspect('equal')

    # Muestra el dibujo del grafo
#    plt.show()

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
        self.mapeoIniciado = False
        self.mapeoIniTerminado = False
        self.mapeoTerminado = False
        self.pasos = 0
        self.conteo_fin = False

    def mapeoInicial(self):
        mapaU = self.model.mapaUNKNOWN
        mapaR = self.model.mapaREAL
        columnas = len(mapaU[0])
        filas = len(mapaU)
        if columnas % 3 == 0:
            agentesIniciales = int(np.ceil(columnas / 3))
            desplazamiento = 3
        else:
            agentesIniciales = int(np.floor(columnas / 2))
            desplazamiento = 2

        posicionInicial = (0, 1)

        if self.unique_id in range(agentesIniciales) and not self.mapeoIniTerminado:
            
            if self.unique_id == 0:
                if mapaR[posicionInicial[0]][posicionInicial[1]] == 'X':
                    posicionInicial = (posicionInicial[0] + 1, posicionInicial[1])
                
                destino = (filas - 1, 1)
                if mapaR[destino[0]][destino[1]] == 'X':
                    destino = (destino[0] - 1, destino[1])
            
            else:
                posicionInicial = (posicionInicial[0], posicionInicial[1] + (desplazamiento * self.unique_id))
                if mapaR[posicionInicial[0]][posicionInicial[1]] == 'X':
                    posicionInicial = (posicionInicial[0] + 1, posicionInicial[1])

                destino = (filas - 1, posicionInicial[1])
                if mapaR[destino[0]][destino[1]] == 'X':
                    destino = (destino[0] - 1, destino[1])

            return posicionInicial, destino
        else:
            inicialesTerminados = True  # Variable para verificar si todos los agentes iniciales terminaron
            for agente in self.model.schedule.agents[:agentesIniciales]:
                if not agente.mapeoIniTerminado:  # Si el agente no ha terminado
                    inicialesTerminados = False  # Cambiamos la variable a False
                    break 
            if inicialesTerminados:
                # Si todos los agentes iniciales terminaron, se verifica que no queden ? en el mapa
                terminaMapeo = True
                camino_corto = None
                for i in range(filas): 
                    for j in range(columnas):
                        if mapaU[i][j] == '?' and mapaR[i][j] != 'X' and not any((i, j) == valor for clave, valor in self.model.pos_obj.items() if clave != self.unique_id):
                            terminaMapeo = False
                            self.mapeoTerminado = False
                            # Si hay ? se activa un agente auxiliar para que termine el mapeo
                            self.mapeoIniciado = True
                            caminoM = a_star_search(self.model.grafo, self.posicion, (i, j))
                            if caminoM is not None and (camino_corto is None or len(caminoM) < len(camino_corto)):
                                camino_corto = caminoM

                if camino_corto is None:
                    camino_corto = [self.model.Inicio]

                # Moverse hacia la ? más cercana
                if len(camino_corto) > 1:
                    self.model.pos_obj[self.unique_id] = camino_corto[-1]
                    return self.posicion, camino_corto[1]
                        
                # Si ya no hay ? se establece que el mapeo ha terminado
                if terminaMapeo:
                    self.mapeoTerminado = True
                        
            return None, None
             
    def actualizarMapa(self):
        self.model.mapaUNKNOWN[self.posicion[0]][self.posicion[1]] = self.model.mapaREAL[self.posicion[0]][self.posicion[1]]
        # Vecinos del nodo actual (Pero incluyendo nodos con obstaculos)
        pos_vecinos = []
        i, j = self.posicion
        if i - 1 >= 0: pos_vecinos.append((i-1, j))
        if i + 1 < len(self.model.mapaUNKNOWN): pos_vecinos.append((i+1, j))
        if j - 1 >= 0: pos_vecinos.append((i, j-1))
        if j + 1 < len(self.model.mapaUNKNOWN[0]): pos_vecinos.append((i, j+1))
        for pos_vecino in pos_vecinos:
            if self.model.mapaREAL[pos_vecino[0]][pos_vecino[1]] == 'X':
                self.model.mapaUNKNOWN[pos_vecino[0]][pos_vecino[1]] = 'X'

            elif self.model.mapaREAL[pos_vecino[0]][pos_vecino[1]] == '0':
                self.model.mapaUNKNOWN[pos_vecino[0]][pos_vecino[1]] = '0'

            elif self.model.mapaUNKNOWN[pos_vecino[0]][pos_vecino[1]] == '?':
                self.model.mapaUNKNOWN[pos_vecino[0]][pos_vecino[1]] = 'B'
        
    def mover(self, nueva_posicion):
        if nueva_posicion not in self.model.pos_ocupadas:
            if self.posicion in self.model.pos_ocupadas:
                self.model.pos_ocupadas.remove(self.posicion)
            if self.posicion != self.model.Inicio:
                self.model.pos_ocupadas.append(nueva_posicion)
            self.posicion = nueva_posicion
            self.pasos += 1
        else:
            for posicion_alterna in self.model.grafo[self.posicion]:
                if posicion_alterna != nueva_posicion and posicion_alterna not in self.model.pos_ocupadas:
                    self.mover(posicion_alterna)
            
        self.actualizarMapa()
            

    def recogerBasura(self):
        if self.model.mapaUNKNOWN[self.posicion[0]][self.posicion[1]].isdigit() and int(self.model.mapaUNKNOWN[self.posicion[0]][self.posicion[1]]) > 0:
            basura = min(int(self.model.mapaUNKNOWN[self.posicion[0]][self.posicion[1]]), self.capacidad)
            self.capacidad -= basura
            self.model.mapaUNKNOWN[self.posicion[0]][self.posicion[1]] = str(int(self.model.mapaUNKNOWN[self.posicion[0]][self.posicion[1]]) - basura)
            self.model.mapaREAL[self.posicion[0]][self.posicion[1]] =  self.model.mapaUNKNOWN[self.posicion[0]][self.posicion[1]]
            # if int(self.model.mapaUNKNOWN[self.posicion[0]][self.posicion[1]]) > 0:
            self.model.pos_obj[self.unique_id] = [] # Elimina la posición de la basura de la lista de posiciones objetivos
            return

    def step(self):
        self.datos()
        # Mapeo inicial
        if self.mapeoTerminado == False:
            posicionInicial, destino = self.mapeoInicial()
            if posicionInicial is not None and destino is not None:
                if self.mapeoIniciado == False:
                    recorrido = a_star_search(self.model.grafo, self.posicion, posicionInicial)
                    if len(recorrido) > 1:
                        self.mover(recorrido[1])
                    if self.posicion == posicionInicial:
                        self.mapeoIniciado = True
                elif self.posicion != destino and self.mapeoIniciado == True:
                    recorrido = a_star_search(self.model.grafo, self.posicion, destino)
                    if recorrido is not None and len(recorrido) > 1:
                        self.mover(recorrido[1])
                    if self.posicion == destino:
                        self.recogerBasura()
                        self.mapeoIniTerminado = True

        else:
            # Si la capacidad es 0, se dirige a la papelera para vaciarse
            if self.capacidad == 0:
                papelera = a_star_search(self.model.grafo, self.posicion, self.model.Papelera)
                if self.posicion != self.model.Papelera:
                    if heuristic(self.posicion, self.model.Papelera) > 5 or (self.model.Papelera == valor for valor in self.model.pos_obj[self.unique_id]):
                        self.mover(papelera[1])
                    elif not any(self.model.Papelera == valor for valor in self.model.pos_obj.items()):
                        self.model.pos_obj[self.unique_id] = self.model.Papelera
                if self.posicion == self.model.Papelera:
                    self.model.pos_obj[self.unique_id] = [] # Elimina la posición de la papelera de la lista de posiciones de objetos
                    self.capacidad = 5
                    self.mover(self.model.grafo[self.posicion][0])
                    
            else:
                # Encuentra la basura más cercana usando A*
                camino_corto = None
                for i in range(len(self.model.mapaUNKNOWN)):
                    for j in range(len(self.model.mapaUNKNOWN[0])):
                        if (self.model.mapaUNKNOWN[i][j] == 'B' or (self.model.mapaUNKNOWN[i][j].isdigit() and int(self.model.mapaUNKNOWN[i][j]) > 0)) and not any((i, j) == valor for clave, valor in self.model.pos_obj.items() if clave != self.unique_id):
                            camino = a_star_search(self.model.grafo, self.posicion, (i, j))
                            if camino is not None and (camino_corto is None or len(camino) < len(camino_corto)):
                                camino_corto = camino

                if camino_corto is None:
                    camino_corto = [self.model.Inicio]

                # Moverse hacia la basura más cercana
                if len(camino_corto) > 1:
                    self.model.pos_obj[self.unique_id] = camino_corto[-1]
                    self.mover(camino_corto[1])
                    if self.posicion == camino_corto[-1]:
                        self.recogerBasura()
                
                if not self.model.pos_obj[self.unique_id] and heuristic(self.posicion, self.model.Papelera) <= 3:
                    for posible_movimiento in self.model.grafo[self.posicion]:
                        if heuristic(posible_movimiento, self.model.Papelera) > heuristic(self.posicion, self.model.Papelera):
                            self.mover(posible_movimiento)
                            break
                


    def datos(self):
        datos = str(self.unique_id) + str(self.posicion)
        datos_basura = str(traducir_mapa(self.model.mapaUNKNOWN))
        print(datos_basura)
        print(datos)
        return datos_basura
    

def update(num, model):
    model.step()

class LimpiezaModel(Model):
    def __init__(self, mapa_txt):
        self.num_robots = 5
        self.schedule = RandomActivation(self)
        self.mapaREAL, self.mapaUNKNOWN = leer_mapa(mapa_txt)
        self.grafo = construir_grafo(self.mapaREAL)
        self.pos_ocupadas = []
        self.pos_obj = {}
        # Variables para ejecución
        self.steps = 0   
        self.running = True
        for i in range(len(self.mapaREAL)):
            for j in range(len(self.mapaREAL[0])):
                if self.mapaREAL[i][j] == 'S':
                    self.Inicio = (i, j)
                elif self.mapaREAL[i][j] == 'P':
                    self.Papelera = (i, j)

        # Establecer el tamaño de la figura
        self.fig, self.ax = plt.subplots(figsize=(25, 25))

         # Desactivar los ejes
        self.ax.axis('off')
        self.datos = []
        self.datos_basura = []

        # Creación de robots
        for i in range(self.num_robots):
            robot = Robot(i, self, self.Inicio)
            self.schedule.add(robot)
            self.pos_obj[i] = []

            

#    def draw_map(self):
#        self.ax.clear()
#        self.ax.set_xlim(0, len(self.mapaREAL[0]))  # Ajustar límites del eje X
#        self.ax.set_ylim(len(self.mapaREAL), 0)  # Ajustar límites del eje Y
#        for i, row in enumerate(self.mapaUNKNOWN):
#            for j, cell in enumerate(row):
#                if cell == 'X':
#                    self.ax.text(j, i, cell, ha='center', va='center', fontsize=60, color='black')
#                else:
#                    self.ax.text(j, i, cell, ha='center', va='center', fontsize=60, color='blue')
#        for agent in self.schedule.agents:
#            self.ax.text(agent.posicion[1], agent.posicion[0], 'R'+ str(agent.unique_id), ha='center', va='center', fontsize=40, color='red')
    
    def step(self):
        self.schedule.step()
        self.ax.set_title(f'Paso: {self.steps}', fontsize=35)
        self.running = False
        for i in range(len(self.mapaUNKNOWN)):
            for j in range(len(self.mapaUNKNOWN[0])):
                if (self.mapaUNKNOWN[i][j].isdigit() and int(self.mapaUNKNOWN[i][j]) > 0) or self.mapaUNKNOWN[i][j] == '?' or self.mapaUNKNOWN[i][j] == 'B':
                    print(f'Aún hay basura en {i, j}')
                    self.running = True
                    break
        self.steps += 1
        self.datos = [robot.datos() for robot in self.schedule.agents]



model = LimpiezaModel('mapa.txt') 


# ani = animation.FuncAnimation(model.fig, update, fargs=(model,), frames=50)
# ani.save('animation.gif', writer='imagemagick', fps=1)
# html = HTML(ani.to_jshtml())
# display(html)


class Server(BaseHTTPRequestHandler):

    # ... (Código del servidor Python, como en tu ejemplo original) ...
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    def do_GET(self):
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
        

    def do_POST(self):
        model.step()
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')        
        
        response_data = model.datos
        

        self._set_response()
        self.wfile.write(str(response_data).encode('utf-8'))


class Server2(BaseHTTPRequestHandler):

    # ... (Código del servidor Python, como en tu ejemplo original) ...
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    def do_GET(self):
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
        

    def do_POST(self):
        model.step()
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')        
        
        response_data = model.datos_basura
        

        self._set_response()
        self.wfile.write(str(response_data).encode('utf-8'))



def run(server_class=HTTPServer, handler_class=Server, port=8586):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info("Starting httpd...\n")  # HTTPD is HTTP Daemon!
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:  # CTRL+C stops the server
        pass
    httpd.server_close()
    logging.info("Stopping httpd...\n")


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
        
        
                # Aquí deberías procesar el JSON que recibes del cliente y usarlo para controlar tu simulación.
        # Puedes enviar la respuesta de vuelta al cliente en formato JSON.

        # Procesa el JSON recibido del cliente (post_data) y controla tu simulación según sea necesario.
        # Por ejemplo, podrías ajustar los parámetros de tu simulación o avanzar un número específico de pasos.

        # ... (Control de la simulación con base en el JSON recibido) ...

        # Genera una respuesta con los resultados de la simulación (esto es solo un ejemplo, ajusta según tus necesidades).
        
        # Ahora necesito que el response.data mande el valor de datos del Robot