# distutils: language = c++
# distutils: sources = grafo_disperso.cpp

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.pair cimport pair

# Declaración de la clase C++
cdef extern from "grafo_disperso.h":
    cdef cppclass GrafoDisperso:
        GrafoDisperso() except +
        void cargarDatos(const string& archivo) except +
        int obtenerNumNodos() except +
        int obtenerNumAristas() except +
        int obtenerGrado(int nodo) except +
        int obtenerNodoMayorGrado() except +
        vector[int] getVecinos(int nodo) except +
        pair[vector[int], vector[pair[int,int]]] BFS(int nodoInicio, int profundidadMax) except +
        size_t obtenerMemoriaUsada() except +

# Clase Python que envuelve la clase C++
cdef class PyGrafoDisperso:
    cdef GrafoDisperso* c_grafo  # Puntero a objeto C++
    
    def __cinit__(self):
        print("[Cython] Creando wrapper de GrafoDisperso...")
        self.c_grafo = new GrafoDisperso()
    
    def __dealloc__(self):
        if self.c_grafo != NULL:
            del self.c_grafo
    
    def cargar_datos(self, str archivo):
        """Carga un dataset desde un archivo"""
        print(f"[Cython] Cargando archivo: {archivo}")
        cdef string archivo_cpp = archivo.encode('utf-8')
        self.c_grafo.cargarDatos(archivo_cpp)
    
    def obtener_num_nodos(self):
        """Retorna el número de nodos del grafo"""
        return self.c_grafo.obtenerNumNodos()
    
    def obtener_num_aristas(self):
        """Retorna el número de aristas del grafo"""
        return self.c_grafo.obtenerNumAristas()
    
    def obtener_grado(self, int nodo):
        """Retorna el grado de un nodo específico"""
        return self.c_grafo.obtenerGrado(nodo)
    
    def obtener_nodo_mayor_grado(self):
        """Retorna el ID del nodo con mayor grado"""
        return self.c_grafo.obtenerNodoMayorGrado()
    
    def get_vecinos(self, int nodo):
        """Retorna lista de vecinos de un nodo"""
        cdef vector[int] vecinos_cpp = self.c_grafo.getVecinos(nodo)
        return list(vecinos_cpp)
    
    def bfs(self, int nodo_inicio, int profundidad_max):
        """
        Ejecuta BFS desde un nodo con profundidad máxima.
        Retorna: (lista_nodos, lista_aristas)
        """
        print(f"[Cython] Solicitud BFS desde nodo {nodo_inicio}, profundidad {profundidad_max}")
        
        cdef pair[vector[int], vector[pair[int,int]]] resultado
        resultado = self.c_grafo.BFS(nodo_inicio, profundidad_max)
        
        # Convertir vectores C++ a listas Python
        nodos_py = list(resultado.first)
        
        aristas_py = []
        cdef vector[pair[int,int]] aristas_cpp = resultado.second
        cdef size_t i
        for i in range(aristas_cpp.size()):
            aristas_py.append((aristas_cpp[i].first, aristas_cpp[i].second))
        
        print(f"[Cython] Retornando {len(nodos_py)} nodos y {len(aristas_py)} aristas a Python")
        return nodos_py, aristas_py
    
    def obtener_memoria_usada(self):
        """Retorna la memoria estimada usada en bytes"""
        return self.c_grafo.obtenerMemoriaUsada()
    
    def obtener_estadisticas(self):
        """Retorna un diccionario con estadísticas del grafo"""
        return {
            'nodos': self.obtener_num_nodos(),
            'aristas': self.obtener_num_aristas(),
            'memoria_mb': self.obtener_memoria_usada() / (1024 * 1024),
            'nodo_mayor_grado': self.obtener_nodo_mayor_grado()
        }