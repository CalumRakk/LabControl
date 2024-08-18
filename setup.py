from setuptools import setup, find_packages

setup(
    name="cloudAuto",
    version="0.1.0",
    description="",
    author="Leo",  # Tu nombre
    author_email="leocasti@gmail.com",  # Tu correo electrónico
    packages=find_packages(),
    install_requires=[
        "django",
        "Celery",
        "playwright",
        "lxml",
        "requests",
        "libtmux",
        "redis",
        "djangorestframework",
    ],
)
