from setuptools import setup, find_packages

setup(
    name="YC HIELO",
    version="1.0.0",
    description="Sistema de gestión de costos de venta de hielo",
    author="YC HIELO",
    packages=find_packages(),
    install_requires=[
        'PyQt6==6.7.1',
        'Pillow==11.0.0',
        'qrcode==7.4.2',
        'reportlab==4.1.1',
    ],
    entry_points={
        'console_scripts': [
            'yc-hielo=main:main',
        ],
    },
    options={
        'bdist_msi': {
            'install_script': 'install_script.py',
        },
    },
)
