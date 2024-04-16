from setuptools import setup, find_packages

NAME = "Onsenpi"
VERSION = "0.1.0"
PYTHON_REQUIRES = ">=3.7"
INSTALL_REQUIRES = ["sp-api>=1.0.0", "requests>=2.31.0"]

AUTHOR = "tbshiki"
AUTHOR_EMAIL = "info@tbshiki.com"
URL = "https://github.com/tbshiki/" + NAME

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    description="A Python library to simplify the use of Amazon Selling Partner API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=PYTHON_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="Onsenpi, sp-api, spapi, amazon",
)
