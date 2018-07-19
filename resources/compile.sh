#!/bin/bash -x

WORKDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

#Ruby version
if [ -z "${RUBY_VERSION}" ];then
    RUBY_VERSION=2.5.1
fi

if [ -z "${RUBY_VERSION_MINOR}" ];then
    RUBY_VERSION_MINOR=2.5
fi

# Runtime name
RUNTIME_NAME=ruby-${RUBY_VERSION_MINOR}

# default install location, can be supplied from outside
if [ -z "$INSTALL_LOCATION" ]; then
    INSTALL_LOCATION=/tmp/$RUNTIME_NAME
fi


# default distribution bucket, can be supplied from outside
if [ -z "$DIST_BUCKET" ]; then
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --out text)
    EC2_AVAIL_ZONE=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone`
    REGION="`echo \"$EC2_AVAIL_ZONE\" | sed 's/[a-z]$//'`"
    DIST_BUCKET=s3://${ACCOUNT_ID}.${REGION}.lambda-ruby-runtime
    set +e
    aws s3 mb ${DIST_BUCKET}
    set -e
fi


#Ruby gems to install
if [ -z "${RUBY_GEMS}" ];then
    RUBY_GEMS='rake bundler'
fi

OPENSSL_LOCATION="${INSTALL_LOCATION}/openssl"
RUBY_LOCATION="${INSTALL_LOCATION}/ruby"


#Packages required to compile Ruby
COMPILE_PACKAGES='zlib zlib-devel openssl openssl-devel readline-devel'


mkdir -p $INSTALL_LOCATION

yum -y group install 'Development Tools' && \
yum -y install $COMPILE_PACKAGES

# Opens SSL compilation
mkdir /build
cd /build
git clone git://git.openssl.org/openssl.git openssl-src && \
cd openssl-src && \
./config --prefix=${OPENSSL_LOCATION} \
 --openssldir=${OPENSSL_LOCATION} && \
make && \
make install

# required for openssl to have some certs to work with
cp /etc/pki/tls/cert.pem ${OPENSSL_LOCATION}/cert.pem

# Ruby compilation
cd /build
wget https://cache.ruby-lang.org/pub/ruby/$RUBY_VERSION_MINOR/ruby-$RUBY_VERSION.tar.gz &&  \
tar -xf ruby-$RUBY_VERSION.tar.gz && \
cd ruby-$RUBY_VERSION && \
export CXXFLAGS="$CXXFLAGS -fPIC" && \
./configure --prefix=$RUBY_LOCATION --disable-werror \
    --with-openssl-dir=${OPENSSL_LOCATION} \
    --disable-largefile --disable-install-doc --disable-install-rdoc \
    --disable-install-capi --without-gmp --without-valgrind --enable-shared && \
    make install && \
$RUBY_LOCATION/bin/gem install $RUBY_GEMS

# remove documentation
rm -rf $INSTALL_LOCATION/openssl/share/man
rm -rf $INSTALL_LOCATION/openssl/share/doc


# generate metadata
cd $INSTALL_LOCATION
DESTINATION="${DIST_BUCKET}/${RUNTIME_NAME}_`date +%Y-%m-%d_%H%M`.zip"
printf "ruby: ${RUBY_VERSION}\npath:${RUBY_LOCATION}/bin\ngems:${RUBY_GEMS}\nsource:${DESTINATION}" > ruby_meta.yaml
printf "openssl: ${OPENSSL_LOCATION}" >> ruby_meta.yaml
# create and upload package
cd $INSTALL_LOCATION && zip -r --symlinks -0 /tmp/$RUNTIME_NAME.zip . && \
aws s3 cp /tmp/$RUNTIME_NAME.zip $DESTINATION

echo "rubydestination: $DESTINATION"
# shut down ec2 instance
halt
