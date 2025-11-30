#include "grafo_disperso.h"
#include <algorithm>
#include <chrono>

GrafoDisperso::GrafoDisperso() : num_nodos(0), num_aristas(0) {
    std::cout << "[C++ Core] Inicializando GrafoDisperso..." << std::endl;
}

GrafoDisperso::~GrafoDisperso() {
    std::cout << "[C++ Core] Destruyendo GrafoDisperso..." << std::endl;
}

void GrafoDisperso::cargarDatos(const std::string& archivo) {
    std::cout << "[C++ Core] Cargando dataset '" << archivo << "'..." << std::endl;
    auto inicio = std::chrono::high_resolution_clock::now();
    
    std::ifstream file(archivo);
    if (!file.is_open()) {
        std::cerr << "[C++ Core] ERROR: No se pudo abrir el archivo" << std::endl;
        return;
    }
    
    std::set<int> nodos_unicos;
    std::vector<std::pair<int,int>> aristas_temp;
    std::string linea;
    
    // Primera pasada: leer todas las aristas y encontrar nodos únicos
    while (std::getline(file, linea)) {
        // Ignorar líneas de comentario
        if (linea.empty() || linea[0] == '#') continue;
        
        std::istringstream iss(linea);
        int origen, destino;
        
        if (iss >> origen >> destino) {
            nodos_unicos.insert(origen);
            nodos_unicos.insert(destino);
            aristas_temp.push_back({origen, destino});
        }
    }
    
    file.close();
    
    // Crear mapeo de nodos a índices consecutivos
    int indice = 0;
    for (int nodo : nodos_unicos) {
        nodo_a_indice[nodo] = indice;
        indice_a_nodo[indice] = nodo;
        indice++;
    }
    
    num_nodos = nodos_unicos.size();
    num_aristas = aristas_temp.size();
    
    // Crear lista de adyacencia temporal
    lista_adyacencia_temp.resize(num_nodos);
    
    for (const auto& arista : aristas_temp) {
        int idx_origen = nodo_a_indice[arista.first];
        int idx_destino = nodo_a_indice[arista.second];
        lista_adyacencia_temp[idx_origen].push_back(idx_destino);
    }
    
    // Construir estructura CSR
    construirCSR();
    
    auto fin = std::chrono::high_resolution_clock::now();
    auto duracion = std::chrono::duration_cast<std::chrono::milliseconds>(fin - inicio);
    
    std::cout << "[C++ Core] Carga completa. Nodos: " << num_nodos 
              << " | Aristas: " << num_aristas << std::endl;
    std::cout << "[C++ Core] Tiempo de carga: " << duracion.count() << "ms" << std::endl;
    std::cout << "[C++ Core] Estructura CSR construida. Memoria estimada: " 
              << obtenerMemoriaUsada() / (1024*1024) << " MB." << std::endl;
}

void GrafoDisperso::construirCSR() {
    row_ptr.resize(num_nodos + 1);
    row_ptr[0] = 0;
    
    for (int i = 0; i < num_nodos; i++) {
        // Ordenar vecinos para búsqueda eficiente
        std::sort(lista_adyacencia_temp[i].begin(), lista_adyacencia_temp[i].end());
        
        for (int vecino : lista_adyacencia_temp[i]) {
            col_indices.push_back(vecino);
            values.push_back(1);  // Peso 1 para grafos no ponderados
        }
        
        row_ptr[i + 1] = col_indices.size();
    }
    
    // Liberar memoria temporal
    lista_adyacencia_temp.clear();
    lista_adyacencia_temp.shrink_to_fit();
}

int GrafoDisperso::obtenerGrado(int nodo) const {
    auto it = nodo_a_indice.find(nodo);
    if (it == nodo_a_indice.end()) return 0;
    
    int idx = it->second;
    if (idx < 0 || idx >= num_nodos) return 0;
    
    return row_ptr[idx + 1] - row_ptr[idx];
}

int GrafoDisperso::obtenerNodoMayorGrado() const {
    int max_grado = 0;
    int nodo_max = -1;
    
    for (int i = 0; i < num_nodos; i++) {
        int grado = row_ptr[i + 1] - row_ptr[i];
        if (grado > max_grado) {
            max_grado = grado;
            nodo_max = indice_a_nodo.at(i);
        }
    }
    
    return nodo_max;
}

std::vector<int> GrafoDisperso::getVecinos(int nodo) const {
    std::vector<int> vecinos;
    
    auto it = nodo_a_indice.find(nodo);
    if (it == nodo_a_indice.end()) return vecinos;
    
    int idx = it->second;
    if (idx < 0 || idx >= num_nodos) return vecinos;
    
    int inicio = row_ptr[idx];
    int fin = row_ptr[idx + 1];
    
    for (int i = inicio; i < fin; i++) {
        vecinos.push_back(indice_a_nodo.at(col_indices[i]));
    }
    
    return vecinos;
}

std::pair<std::vector<int>, std::vector<std::pair<int,int>>> 
GrafoDisperso::BFS(int nodoInicio, int profundidadMax) const {
    
    std::cout << "[C++ Core] Ejecutando BFS desde nodo " << nodoInicio 
              << ", profundidad máxima " << profundidadMax << std::endl;
    
    auto inicio_tiempo = std::chrono::high_resolution_clock::now();
    
    std::vector<int> nodos_visitados;
    std::vector<std::pair<int,int>> aristas_subgrafo;
    
    auto it = nodo_a_indice.find(nodoInicio);
    if (it == nodo_a_indice.end()) {
        std::cout << "[C++ Core] Nodo no encontrado" << std::endl;
        return {nodos_visitados, aristas_subgrafo};
    }
    
    int idx_inicio = it->second;
    std::queue<std::pair<int, int>> cola; // (índice, profundidad)
    std::vector<bool> visitado(num_nodos, false);
    
    cola.push({idx_inicio, 0});
    visitado[idx_inicio] = true;
    nodos_visitados.push_back(nodoInicio);
    
    while (!cola.empty()) {
        auto [idx_actual, prof_actual] = cola.front();
        cola.pop();
        
        if (prof_actual >= profundidadMax) continue;
        
        int inicio = row_ptr[idx_actual];
        int fin = row_ptr[idx_actual + 1];
        
        for (int i = inicio; i < fin; i++) {
            int idx_vecino = col_indices[i];
            
            int nodo_actual_original = indice_a_nodo.at(idx_actual);
            int nodo_vecino_original = indice_a_nodo.at(idx_vecino);
            
            aristas_subgrafo.push_back({nodo_actual_original, nodo_vecino_original});
            
            if (!visitado[idx_vecino]) {
                visitado[idx_vecino] = true;
                nodos_visitados.push_back(nodo_vecino_original);
                cola.push({idx_vecino, prof_actual + 1});
            }
        }
    }
    
    auto fin_tiempo = std::chrono::high_resolution_clock::now();
    auto duracion = std::chrono::duration_cast<std::chrono::microseconds>(fin_tiempo - inicio_tiempo);
    
    std::cout << "[C++ Core] Nodos encontrados: " << nodos_visitados.size() 
              << ". Tiempo ejecución: " << duracion.count() / 1000.0 << "ms." << std::endl;
    
    return {nodos_visitados, aristas_subgrafo};
}

size_t GrafoDisperso::obtenerMemoriaUsada() const {
    size_t memoria = 0;
    
    memoria += row_ptr.capacity() * sizeof(int);
    memoria += col_indices.capacity() * sizeof(int);
    memoria += values.capacity() * sizeof(int);
    
    // Mapas aproximados
    memoria += nodo_a_indice.size() * (sizeof(int) * 2 + 32);
    memoria += indice_a_nodo.size() * (sizeof(int) * 2 + 32);
    
    return memoria;
}

int GrafoDisperso::obtenerIndice(int nodo_original) const {
    auto it = nodo_a_indice.find(nodo_original);
    return (it != nodo_a_indice.end()) ? it->second : -1;
}

int GrafoDisperso::obtenerNodoOriginal(int indice) const {
    auto it = indice_a_nodo.find(indice);
    return (it != indice_a_nodo.end()) ? it->second : -1;
}