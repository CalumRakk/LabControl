from setuptools import find_packages, setup

setup(
    name="labcontrol",
    version="0.2",
    description="",
    author="Leo",
    author_email="leocasti@gmail.com",
    packages=["labcontrol","labcontrol.browser"]+find_packages(),
    install_requires=["lxml", "requests", "pydantic", "selenium","webdriver-manager"],
)