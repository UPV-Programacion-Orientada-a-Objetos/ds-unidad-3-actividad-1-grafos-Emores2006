#ifndef GRAFO_DISPERSO_H
#define GRAFO_DISPERSO_H

#include "grafo_base.h"
#include <vector>
#include <map>
#include <iostream>
#include <fstream>
#include <sstream>
#include <queue>
#include <set>
#include <ctime>

// Implementación de grafo usando formato CSR (Compressed Sparse Row)
class GrafoDisperso : public GrafoBase {
private:
    // Estructura CSR: 3 vectores para representar matriz dispersa
    std::vector<int> row_ptr;      // Punteros a inicio de cada fila
    std::vector<int> col_indices;  // Índices de columnas (nodos destino)
    std::vector<int> values;       // Valores (pueden ser pesos, aquí 1s)
    
    int num_nodos;
    int num_aristas;
    
    // Mapa para renumerar nodos si no son consecutivos
    std::map<int, int> nodo_a_indice;
    std::map<int, int> indice_a_nodo;
    
    // Para construir la estructura antes de comprimirla
    std::vector<std::vector<int>> lista_adyacencia_temp;

public:
    GrafoDisperso();
    ~GrafoDisperso();
    
    void cargarDatos(const std::string& archivo) override;
    int obtenerNumNodos() const override { return num_nodos; }
    int obtenerNumAristas() const override { return num_aristas; }
    int obtenerGrado(int nodo) const override;
    int obtenerNodoMayorGrado() const override;
    std::vector<int> getVecinos(int nodo) const override;
    
    std::pair<std::vector<int>, std::vector<std::pair<int,int>>> 
        BFS(int nodoInicio, int profundidadMax) const override;
    
    size_t obtenerMemoriaUsada() const override;
    
private:
    void construirCSR();
    int obtenerIndice(int nodo_original) const;
    int obtenerNodoOriginal(int indice) const;
};

#endif // GRAFO_DISPERSO_H