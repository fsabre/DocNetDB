import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="docnetdb",
    version="0.6.1",
    license="MIT",
    author="fsabre",
    author_email="fabien.sabre@gmail.com",
    description="A pure Python document and graph database engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fsabre/DocNetDB",
    packages=setuptools.find_packages(),
    keywords=["document", "graph", "database", "nosql", "pure python"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)
