from setuptools import setup

setup(name='ruby-aws-lambda-runtime', version='0.1.0', author='Nikola Tosic',
      author_email='tosicnikola10@gmail.clom',
      url='http://github.com/toshke/ruby-aws-lambda-runtime',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3.6',
          'Intended Audience :: Information Technology',
          'License :: OSI Approved :: MIT License',
          'Topic :: Development :: Serverless',
      ],
      keywords='aws lambda ruby',
      packages=['boto3'],
      install_requires=['boto3'],
      python_requires='>=3.6',
      description='Generate and use ruby binaries on AWS Lambda',
      entry_points={
          'console_scripts': ['ruby-aws-lambda-runtime = cli.__main__:main'],
      })
