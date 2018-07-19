## Intro

You can use this repository to generate ruby runtime binaries
in order to run Ruby serverless, on AWS Lambda.

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

1. Natively compiled vs travelling ruby

Most of the examples/existing tools for running ruby
on lambda make use of [travelling ruby] (https://github.com/phusion/traveling-ruby),
which has problems with some of the native extensions.

This solution builds ruby runtime binaries on same AMI
that runs AWS lambda, making it much more compatible with 
Lambda environment. As travelling ruby [README](https://github.com/phusion/traveling-ruby) states

> 
> Native extensions:
>
> Traveling Ruby only supports native extensions when creating Linux and OS X packages. Native extensions are currently not supported when creating Windows packages.
> Traveling Ruby only supports a number of popular native extension gems, and only in some specific versions. You cannot use just any native extension gem.
> Native extensions are covered in tutorial 3.

## Demo

TBD

## Usage
 
You can use `ruby-aws-lambda-runtime` python 
package to quickly get started. To deploy prebuilt
lambda binaries

```
pip install 
ruby-aws-lambda-runtime init-default
```

By default, python 
python library will use prepackaged ruby binaries
available as download packages on [releases page]
(enter url here). They get deployed to your S3 bucket, 
and downloaded at lambda runtime

```

```

### To compile binaries


### To use precompiled binaries 


### To bundle binaries with LambdaCode


## Requirements

To build your own binaries you'll need

 - python3.6
 - openssl
 - ssh (scp)
 - aws cli
 - aws credentials (create iam role, create keypair, run instances)
 - shell 
 - default subnets wtih MapPublicIpOnLaunch=True set - this is how public
   subnets are discovered

2. 
[OpenSSL] problems are 2nd reason I did not go with 
existing solutions - as `openssl` version in current
lambda environment is 1.0.1 - [php-serverless](https://github.com/ZeroSharp/serverless-php/issues/8)
has similar issues. I got this error when trying to download 
git repository over https within ruby code running on lambda. 
This repository/package resolves this by compiling OpenSSL 1.1.0
altogether with Ruby (that is - compiling Ruby against compiled OpenSSL
on same AMI). This results in large package unfortunately. 

3. 
Ruby runtimes are being downloaded during lambda invocation, rather 
than being bundled with lambda (which is also possible). This makes build-deploy-test
cycle much faster, and avoids bloated lambda code zip file. 


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


