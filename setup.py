from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read().replace(".. include:: toc.rst\n\n", "")

# The line below is parsed by `docs/conf.py`.
version = "2.0.0"

setup(
    name="are",
    version=version,
    packages=["are",],
    install_requires=["reiter~=0.2", "nfa~=3.0",],
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
