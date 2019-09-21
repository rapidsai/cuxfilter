from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

# with open('LICENSE') as f:
#     license = f.read()

setup(
    name='cuXfilter',
    version='0.2.0',
    description='Python library to do server-side cross-filtering viz dashboards using cudf, panel & bokeh',
    long_description=readme,
    author='Ajay Thorve',
    author_email='athorve@nvidia.com',
    url='https://gitlab-master.nvidia.com/athorve/cuxfilter',
    packages=find_packages(exclude=('tests', 'docs', 'notebooks'))        # license=license,
)
