import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os

try:
    import grafo_wrapper
    import networkx as nx
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de tener instalado: networkx matplotlib")
    exit(1)


class NeuroNetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NeuroNet - Análisis de Grafos Masivos")
        self.root.geometry("1200x800")
        
        self.grafo = None
        self.archivo_cargado = None
        
        self.crear_interfaz()
    
    def crear_interfaz(self):
        # Frame principal dividido en 3 secciones
        
        # ============ SECCIÓN SUPERIOR: Controles ============
        frame_controles = ttk.LabelFrame(self.root, text="Controles", padding=10)
        frame_controles.pack(fill=tk.X, padx=10, pady=5)
        
        # Botón cargar archivo
        btn_cargar = ttk.Button(
            frame_controles, 
            text="📂 Cargar Dataset",
            command=self.cargar_archivo
        )
        btn_cargar.grid(row=0, column=0, padx=5, pady=5)
        
        # Label del archivo actual
        self.lbl_archivo = ttk.Label(frame_controles, text="Ningún archivo cargado")
        self.lbl_archivo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Botón nodo crítico
        btn_critico = ttk.Button(
            frame_controles,
            text="🎯 Identificar Nodo Crítico",
            command=self.identificar_nodo_critico,
            state=tk.DISABLED
        )
        btn_critico.grid(row=0, column=2, padx=5, pady=5)
        self.btn_critico = btn_critico
        
        # Separador
        ttk.Separator(frame_controles, orient=tk.HORIZONTAL).grid(
            row=1, column=0, columnspan=4, sticky=tk.EW, pady=10
        )
        
        # Controles BFS
        ttk.Label(frame_controles, text="Nodo inicio:").grid(row=2, column=0, padx=5, sticky=tk.E)
        self.entry_nodo = ttk.Entry(frame_controles, width=15)
        self.entry_nodo.grid(row=2, column=1, padx=5, sticky=tk.W)
        
        ttk.Label(frame_controles, text="Profundidad:").grid(row=2, column=2, padx=5, sticky=tk.E)
        self.entry_prof = ttk.Entry(frame_controles, width=10)
        self.entry_prof.insert(0, "2")
        self.entry_prof.grid(row=2, column=3, padx=5, sticky=tk.W)
        
        btn_bfs = ttk.Button(
            frame_controles,
            text="🔍 Ejecutar BFS",
            command=self.ejecutar_bfs,
            state=tk.DISABLED
        )
        btn_bfs.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        self.btn_bfs = btn_bfs
        
        # ============ SECCIÓN MEDIA: Estadísticas ============
        frame_stats = ttk.LabelFrame(self.root, text="Estadísticas del Grafo", padding=10)
        frame_stats.pack(fill=tk.X, padx=10, pady=5)
        
        self.txt_stats = scrolledtext.ScrolledText(
            frame_stats,
            height=6,
            font=("Courier", 10),
            state=tk.DISABLED
        )
        self.txt_stats.pack(fill=tk.BOTH, expand=True)
        
        # ============ SECCIÓN INFERIOR: Visualización ============
        frame_viz = ttk.LabelFrame(self.root, text="Visualización", padding=10)
        frame_viz.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Figura de matplotlib
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Subgrafo resultante del BFS")
        self.ax.axis('off')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_viz)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
    
    def actualizar_stats(self, texto):
        """Actualiza el área de estadísticas"""
        self.txt_stats.config(state=tk.NORMAL)
        self.txt_stats.delete(1.0, tk.END)
        self.txt_stats.insert(tk.END, texto)
        self.txt_stats.config(state=tk.DISABLED)
    
    def cargar_archivo(self):
        """Carga un archivo de dataset"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar dataset",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not archivo:
            return
        
        self.progress.start()
        self.lbl_archivo.config(text="Cargando...")
        
        # Cargar en hilo separado para no bloquear GUI
        thread = threading.Thread(target=self._cargar_datos_thread, args=(archivo,))
        thread.start()
    
    def _cargar_datos_thread(self, archivo):
        """Thread para cargar datos sin bloquear GUI"""
        try:
            self.grafo = grafo_wrapper.PyGrafoDisperso()
            self.grafo.cargar_datos(archivo)
            self.archivo_cargado = os.path.basename(archivo)
            
            stats = self.grafo.obtener_estadisticas()
            
            # Actualizar GUI en el hilo principal
            self.root.after(0, self._mostrar_stats_cargados, stats)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", f"Error al cargar archivo:\n{str(e)}"
            ))
        finally:
            self.root.after(0, self.progress.stop)
    
    def _mostrar_stats_cargados(self, stats):
        """Muestra estadísticas después de cargar"""
        self.lbl_archivo.config(text=f"✓ {self.archivo_cargado}")
        
        texto_stats = f"""
═══════════════════════════════════════════════════════════
  DATASET CARGADO: {self.archivo_cargado}
═══════════════════════════════════════════════════════════
  • Número de nodos:        {stats['nodos']:,}
  • Número de aristas:      {stats['aristas']:,}
  • Memoria estimada:       {stats['memoria_mb']:.2f} MB
  • Nodo con mayor grado:   {stats['nodo_mayor_grado']} 
    (Grado: {self.grafo.obtener_grado(stats['nodo_mayor_grado'])})
═══════════════════════════════════════════════════════════
        """
        
        self.actualizar_stats(texto_stats)
        
        # Habilitar botones
        self.btn_critico.config(state=tk.NORMAL)
        self.btn_bfs.config(state=tk.NORMAL)
    
    def identificar_nodo_critico(self):
        """Identifica y muestra el nodo con mayor grado"""
        if not self.grafo:
            messagebox.showwarning("Aviso", "Primero carga un dataset")
            return
        
        nodo_critico = self.grafo.obtener_nodo_mayor_grado()
        grado = self.grafo.obtener_grado(nodo_critico)
        vecinos = self.grafo.get_vecinos(nodo_critico)
        
        mensaje = f"""
🎯 NODO MÁS CRÍTICO IDENTIFICADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID del Nodo:        {nodo_critico}
Grado (conexiones): {grado}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Este nodo tiene el mayor número de conexiones
en todo el grafo, lo que lo convierte en el
punto más crítico de la red.

Primeros 10 vecinos: {vecinos[:10]}
        """
        
        messagebox.showinfo("Nodo Crítico", mensaje)
        
        # Opcional: Establecer este nodo en el campo de BFS
        self.entry_nodo.delete(0, tk.END)
        self.entry_nodo.insert(0, str(nodo_critico))
    
    def ejecutar_bfs(self):
        """Ejecuta BFS y visualiza resultado"""
        if not self.grafo:
            messagebox.showwarning("Aviso", "Primero carga un dataset")
            return
        
        try:
            nodo_inicio = int(self.entry_nodo.get())
            profundidad = int(self.entry_prof.get())
            
            if profundidad < 1:
                messagebox.showerror("Error", "La profundidad debe ser >= 1")
                return
            
        except ValueError:
            messagebox.showerror("Error", "Ingresa valores numéricos válidos")
            return
        
        self.progress.start()
        
        # Ejecutar en thread separado
        thread = threading.Thread(
            target=self._ejecutar_bfs_thread, 
            args=(nodo_inicio, profundidad)
        )
        thread.start()
    
    def _ejecutar_bfs_thread(self, nodo_inicio, profundidad):
        """Thread para ejecutar BFS"""
        try:
            nodos, aristas = self.grafo.bfs(nodo_inicio, profundidad)
            
            # Visualizar en el thread principal
            self.root.after(0, self._visualizar_subgrafo, nodos, aristas, nodo_inicio)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", f"Error en BFS:\n{str(e)}"
            ))
        finally:
            self.root.after(0, self.progress.stop)
    
    def _visualizar_subgrafo(self, nodos, aristas, nodo_inicio):
        """Visualiza el subgrafo resultante"""
        # Limpiar figura anterior
        self.ax.clear()
        
        if len(nodos) == 0:
            self.ax.text(
                0.5, 0.5, 
                'No se encontraron nodos\n(verifica que el nodo exista)', 
                ha='center', va='center',
                fontsize=14
            )
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.canvas.draw()
            return
        
        # Crear grafo de NetworkX solo para visualización
        G = nx.DiGraph()
        G.add_edges_from(aristas)
        
        # Layout
        pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
        
        # Colores: nodo inicio en rojo, demás en azul
        colores = ['red' if n == nodo_inicio else 'lightblue' for n in G.nodes()]
        
        # Dibujar
        nx.draw_networkx_nodes(
            G, pos, 
            node_color=colores, 
            node_size=300, 
            alpha=0.8,
            ax=self.ax
        )
        
        nx.draw_networkx_edges(
            G, pos,
            edge_color='gray',
            arrows=True,
            arrowsize=10,
            alpha=0.5,
            ax=self.ax
        )
        
        # Etiquetas solo si no son muchos nodos
        if len(nodos) < 50:
            nx.draw_networkx_labels(
                G, pos,
                font_size=8,
                font_weight='bold',
                ax=self.ax
            )
        
        self.ax.set_title(
            f'Subgrafo BFS desde nodo {nodo_inicio}\n'
            f'{len(nodos)} nodos, {len(aristas)} aristas',
            fontsize=12,
            fontweight='bold'
        )
        self.ax.axis('off')
        
        self.canvas.draw()
        
        # Actualizar estadísticas
        info = f"""
BFS COMPLETADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Nodo inicio:      {nodo_inicio}
  Nodos visitados:  {len(nodos)}
  Aristas en subgrafo: {len(aristas)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Nodos: {nodos[:20]}{'...' if len(nodos) > 20 else ''}
        """
        self.actualizar_stats(info)


def main():
    root = tk.Tk()
    app = NeuroNetGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()