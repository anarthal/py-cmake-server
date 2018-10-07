import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycmakeserver",
    version="0.0.2",
    author="Anarthal (Ruben Perez)",
    author_email="rubenperez038@gmail.com",
    description="Client for cmake-server protocol",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anarthal/py-cmake-server",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
    ],
)