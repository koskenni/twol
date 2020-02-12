import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twol", # of the PyPI project and package
    version="0.5.1",
    author="Kimmo Koskenniemi",
    author_email="koskenni@gmail.com",
    description="Tools for simplified two-level morphology",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/koskenni/twol",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "twol-aligner = twol.aligner:main",
            "twol-metric = twol.metric:main",
            "twol-multialign = twol.multialign:main",
            "twol-table2words = twol.table2words:step1",
            "twol-words2zerofilled = twol.words2zerofilled:main",
            "twol-zerofilled2raw = twol.zerofilled2raw:main",
            "twol-raw2named = twol.raw2named:main",
            "twol-comp = twol.twolcomp:main",
            "twol-examples2fst = twol.twexamp:main",
            "twol-discov =  twol.discover:main"
        ]
    },
    include_package_data=True,
    python_requires='==3.6,==3.7',
    ##python_requires='>=3.6',
        install_requires=[
            'grapheme',
            'orderedset',
            'hfst',
            ##'hfst==3.15.0.0b0',
            'TatSu==4.4.0',
    ]

)

