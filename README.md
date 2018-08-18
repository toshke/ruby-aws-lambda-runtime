## Intro

You can use this repository to generate ruby runtime binaries
in order to run Ruby on AWS Lambda FaaS. Alternatively, you 
can use precompiled binaries attache to releases page on Github.

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

> Native extensions:
>
> Traveling Ruby only supports native extensions when creating Linux and OS X packages. 
> Native extensions are currently not supported when creating Windows packages.
> Traveling Ruby only supports a number of popular native extension gems, and only in some specific versions.
> You cannot use just any native extension gem. Native extensions are covered in tutorial 3.

2. Packaging

This package is designed to download ruby binaries from pre-defined
location at runtime, rather than bloating Lambda package with ruby binaries.

3. *OpenSSL* problems are 2nd reason I did not go with 
existing solutions - as `openssl` version in current
lambda environment is 1.0.1 - [php-serverless](https://github.com/ZeroSharp/serverless-php/issues/8)
has similar issues. I got this error when trying to download 
git repository over https within ruby code running on lambda. 
This repository/package resolves this by compiling OpenSSL 1.1.0
altogether with Ruby (that is - compiling Ruby against compiled OpenSSL
on same AMI). This results in large package unfortunately. 

> 
> Native extensions:
>
> Traveling Ruby only supports native extensions when creating Linux and OS X packages. Native extensions are currently not supported when creating Windows packages.
> Traveling Ruby only supports a number of popular native extension gems, and only in some specific versions. You cannot use just any native extension gem.
> Native extensions are covered in tutorial 3.

## Performance impact and memory considerations

Starting the lambda cold will take less than 10 seconds to download and unpack
binaries from S3 bucket with 512MB of memory allocated for runtime
This changes up to 30 seconds with 128MB of lambda memory.

Simple printing ruby version, using `ruby -v`, once Lambda is warmed up takes
less than 50ms on average with 512MB memory configured. 

Consider running with at least 512MB lambda runtime memory allowed. 

## Demo

TBD

## Usage

### 1 - Prepare binaries in your local account
 
To prepare for library for consumption on Lambda, ruby binaries
need be deployed to S3. You can either compile your own,
or use prebuilt binaries.

#### To use prebuilt libraries

```
pip install ruby-aws-lambda-runtime
ruby-aws-lambda-runtime upload-precompiled-binaries
```

#### To compile your own

```
pip install ruby-aws-lambda-runtime
ruby-aws-lambda-runtime generate-binaries
```

### Consume

To consume ruby libraries, deploy this package to AWS Lambda
configured with Ptyhon3.6 runtime, and consume as follows

```
from ruby_lambda_runtime.ruby_runtime import RubyLambdaRuntime

def lambda_handler(event, context):
    runtime = RubyLambdaRuntime()
    # execute ruby binary
    runtime.execute('ruby --version')
    runtime.execute('ruby -e 'puts "heelo world!!"')
    
    # package ruby 
    runtime.execute('ruby my_packaged_ruby_script.rb')
    
    # 
    runtime.execute('bundler install')



```


### To bundle binaries with LambdaCode

TBD. Pull requests are appreciated. 

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


## How it works

Currently, binaries are created during boot time of ec2 instance. Orchestartion 
of running this instance, waiting for compile completion etc, and removal of created
resources is done through raw API calls. There is idea/plan to move this to cloudformation
using troposhpere library. 

### Build time

At build time, an instance is spinned up in `us-east-1` from
Lambda base AMI (`ami-4fffc834`)

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


