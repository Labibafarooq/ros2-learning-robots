from setuptools import find_packages, setup

package_name = 'lr_ppo'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hproc03',
    maintainer_email='Labibafarooq23@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'env_node = lr_ppo.env_node:main',
        'ppo_trainer = lr_ppo.ppo_trainer:main',
    ],
},
)
