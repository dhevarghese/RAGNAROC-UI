import os

import numpy
from Cython.Build import cythonize
from setuptools import Extension, setup

HERE = os.path.dirname(os.path.abspath(__file__))

setup(
    ext_modules=cythonize(
        Extension(
            "ragnaroc",
            [os.path.join(HERE, "ragnaroc.pyx")],
            include_dirs=[numpy.get_include()],
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        ),
    ),
)

#  python setup.py build_ext --inplace
