from setuptools import setup, find_packages

setup(
    name="moviepy-layout",
    version="0.1.0",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    author="Kmm Hanan",
    author_email="hanan@kmmhanan.com",
    description="Composable layout primitives for MoviePy, with RGBA gradients and asset modes",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kmmhanan/moviepy-layout",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.8",
)
