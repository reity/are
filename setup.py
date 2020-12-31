from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="are",
    version="0.1.0",
    packages=["are",],
    install_requires=[],
    license="MIT",
    url="https://github.com/reity/are",
    author="Andrei Lapets",
    author_email="a@lapets.io",
    description="Library for defining and working with abstract " +\
                "regular expressions that work with any symbol type.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    test_suite="nose.collector",
    tests_require=["nose"],
)
