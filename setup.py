import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SQLGenerator-by-dropout",
    version="0.0.3",
    author="drop-out",
    author_email="drop-out@foxmail.com",
    description="Generate SQL script with Pandas-like Python code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/drop-out/SQL-Generator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)