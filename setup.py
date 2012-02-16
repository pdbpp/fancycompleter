import sys
import os.path
from setuptools import setup, find_packages

readme = os.path.join(os.path.dirname(__file__), 'README')
long_description = open(readme).read()

if sys.version_info < (3,):
    install_requires=["pyrepl>=0.8.2"]
else:
    install_requires=[]


setup(
    name='fancycompleter',
    version='0.3',
    author='Antonio Cuni',
    author_email='anto.cuni@gmail.com',
    py_modules=['fancycompleter'],
    url='http://bitbucket.org/antocuni/fancycompleter',
    license='BSD',
    description='colorful TAB completion for Python prompt',
    long_description=long_description,
    keywords='rlcompleter prompt tab color completion',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Topic :: Utilities",
        ],
    install_requires=install_requires,
)
