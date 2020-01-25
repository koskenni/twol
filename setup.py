import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twol", # of the PyPI project and package
    version="0.0.22",
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
            "twol-aligner = twolalign.aligner:main",
            "twol-metric = twolalign.metric:main",
            "twol-multialign = twolalign.multialign:main",
            "twol-table2words = twolalign.table2words:step1",
            "twol-words2zerofilled = twolalign.words2zerofilled:main",
            "twol-zerofilled2raw = twolalign.zerofilled2raw:main",
            "twol-raw2named = twolalign.raw2named:main",
            "twol-comp = twol.twolcomp:main",
            "twol-examples2fst = twol.twexamp:main",
            "twol-discov =  twol.twdiscov:main"
        ]
    },
    include_package_data=True,
    python_requires='>=3.6',
        install_requires=[
        'hfst',
        'TatSu',
        'grapheme'
    ]

)

