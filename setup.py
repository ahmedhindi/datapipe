from setuptools import setup, find_packages

setup(
    name="dukto",
    version="0.1.8",
    packages=find_packages(),
    author_email="ahmedelsyd5@gmail.com",
    description="data pre-processing pipeline library.",
    url="https://github.com/ahmedhindi/dukto",
    license="MIT",
    install_requires=[
        "pandas",
        "pydantic",
    ],
)
