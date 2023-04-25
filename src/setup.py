from setuptools import setup, find_packages

data = dict(
    name="my_custom_package",
    version="0.0.3",
    packages=find_packages(),
)

if __name__ == '__main__':
    setup(**data)
