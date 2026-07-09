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
    package_data={
        "serbian_translit": ["data/*.yaml"],
    },
)
