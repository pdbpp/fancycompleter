from setuptools import setup

setup(
    name='fancycompleter',
    setup_requires="setupmeta",
    versioning="devcommit",
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
        'Programming Language :: Python :: 3.8',
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Utilities",
        ],
    install_requires=[
        "pyrepl>=0.8.2",
        "pyreadline;platform_system=='Windows'",
    ]
)
