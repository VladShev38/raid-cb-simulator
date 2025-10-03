from setuptools import setup, find_packages

# Read requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="raid-cb-simulator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.9",
    author="Vladimir Shevyakov",
    description="RHacky simulator for Clan Boss in Raid: Shadow Legends",
    url="https://github.com/yourusername/raid-cb-simulator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
