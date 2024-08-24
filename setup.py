from setuptools import setup, find_packages

setup(
    name="cloudAuto",
    version="0.1.0",
    description="",
    author="Leo",
    author_email="leocasti@gmail.com",
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
