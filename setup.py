from pathlib import Path

from setuptools import find_packages, setup

setup(
    name="serbian-translit",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "PyYAML>=6.0",
    ],
    python_requires=">=3.10",
    author="Apakabarlabs",
    description="Deterministic Serbian and Montenegrin script conversion (Cyrillic ↔ Latin).",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/apakabarlabs/serbian-translit-python",
    license="MIT",
    keywords="serbian montenegrin transliteration script conversion cyrillic latin bcms",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Serbian",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Text Processing :: Linguistic",
    ],
    package_data={
        "serbian_translit": ["data/*.yaml"],
    },
)
