## Intro

You can use this repository to generate ruby runtime binaries
for running on lambda. 

OR
 
You can use `ruby-aws-lambda-runtime` python 
package to quickly get started. By default, python 
python library will use prepackaged ruby binaries
available as download packages on [releases page]
(enter url here) 

## Demo



## Why

Ruby is part of every day live for many developers, and
missing native runtime support for AWS Lambda. 

There is currently open petition on 
https://www.serverless-ruby.org/ to push for 
native ruby support. This repository does not provide
support for any other cloud provider than AWS. 

As Lambda has become 1st class citizen for many cloud
infrastructure automation tasks, this tool(library)
tries to fill in the gap until native support is released

### Why not existing solutions?

Most of the examples/existing tools for running ruby
on lambda make use of [travelling ruby] (https://github.com/phusion/traveling-ruby),
which has problems with some of the native extensions.

This solution builds ruby runtime binaries on same AMI
that runs AWS lambda, making it much more compatible with 
Lambda environment.

[OpenSSL] problems are 2nd reason I did not go with 
existing solutions - as `openssl` version in current
lambda environment is 1.0.1


## How

### Build time

At build time, an instance is spinned up in `us-east-1` from
Lambda base AMI ()


### Run time

By default, binaries are not deployed as lambda source code,
but rather downloaded on 1st lambda invocation. This makes
cold start take some time (1st invocation). As `/tmp` is only
writable location within Lambda environment, binaries are 
unpacked here

#### Bundling binaries with lambda code

### Invoking ruby from your Python lambda


## Resource requirements

From empirical observation, simple ruby scripts ran just fine with 
lowest possible memory available (128MB)

## Similar projects


