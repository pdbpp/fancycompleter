from setuptools import setup

setup(
    name='fancycompleter-pdbpp',
    setup_requires="setupmeta",
    maintainer="Daniel Hahler",
    url='https://github.com/pdbpp/fancycompleter',
    author='Antonio Cuni',
    author_email='anto.cuni@gmail.com',
    py_modules=['fancycompleter'],
    license='BSD',
    description='colorful TAB completion for Python prompt',
    keywords='rlcompleter prompt tab color completion',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Utilities",
        ],
    install_requires=[
        "pyrepl @ git+https://github.com/pdbpp/pyrepl@master#egg=pyrepl",
        "pyreadline;platform_system=='Windows'",
    ]
)
