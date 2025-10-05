from setuptools import setup, find_packages

setup(
    name="goalpredictor-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.9",
    author="Andrii Pylypchuk",
    description="AI-powered football match predictions for top 5 European leagues",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/pilipandr770/GoalPredictor.AI",
    license="MIT",
)
