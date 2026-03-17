from setuptools import find_packages, setup

package_name = 'lr_ppo_baseline'

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
    description='Baseline controller (safe fallback)',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'env_node_baseline = lr_ppo_baseline.env_node:main',
        ],
    },
)
