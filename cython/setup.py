from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules=cythonize(Extension("ragnaroc", ["./ragnaroc.pyx"]), annotate=True), 
    include_dirs=[numpy.get_include()],
)

#https://stackoverflow.com/questions/14657375/cython-fatal-error-numpy-arrayobject-h-no-such-file-or-directory

#  python setup.py build_ext --inplace