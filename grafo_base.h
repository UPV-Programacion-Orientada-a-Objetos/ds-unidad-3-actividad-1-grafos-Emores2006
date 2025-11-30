#ifndef GRAFO_BASE_H
#define GRAFO_BASE_H

#include <vector>
#include <string>
#include <utility>

// Clase abstracta que define la interfaz del grafo
class GrafoBase {
public:
    virtual ~GrafoBase() {}
    
    // Métodos virtuales puros que deben implementarse
    virtual void cargarDatos(const std::string& archivo) = 0;
    virtual int obtenerNumNodos() const = 0;
    virtual int obtenerNumAristas() const = 0;
    virtual int obtenerGrado(int nodo) const = 0;
    virtual int obtenerNodoMayorGrado() const = 0;
    virtual std::vector<int> getVecinos(int nodo) const = 0;
    
    // BFS que retorna nodos visitados y sus conexiones
    virtual std::pair<std::vector<int>, std::vector<std::pair<int,int>>> 
        BFS(int nodoInicio, int profundidadMax) const = 0;
    
    // Información sobre memoria
    virtual size_t obtenerMemoriaUsada() const = 0;
};

#endif // GRAFO_BASE_H