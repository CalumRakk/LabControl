from setuptools import setup, find_packages

setup(
    name="labcontrol",
    version="0.2",
    description="",
    author="Leo",
    author_email="leocasti@gmail.com",
    packages=find_packages(),
    install_requires=["playwright", "lxml", "requests", "redis"],
)
