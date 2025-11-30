from setuptools import setup, Extension
from Cython.Build import cythonize
import sys

# Configuración específica según el sistema operativo
extra_compile_args = []
extra_link_args = []

if sys.platform == 'win32':
    extra_compile_args = ['/std:c++17', '/O2']
else:  # Linux/Mac
    extra_compile_args = ['-std=c++17', '-O3', '-Wall']
    extra_link_args = ['-std=c++17']

# Definir la extensión
extensions = [
    Extension(
        name="grafo_wrapper",
        sources=[
            "grafo_wrapper.pyx",
            "grafo_disperso.cpp"
        ],
        include_dirs=["."],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )
]

setup(
    name="NeuroNet",
    version="1.0",
    description="Sistema híbrido C++/Python para análisis de grafos masivos",
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'embedsignature': True
        }
    ),
    zip_safe=False,
)