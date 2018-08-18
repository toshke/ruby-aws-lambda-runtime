import boto3
import subprocess
import os

INITIALIZED_MARKER = 'RUBY_RUNTIME_INITIALIZED'


class RubyLambdaRuntime:

    def __init__(self, RUBY_VERSION='2.5', initialize_runtime=True):
        self.RUBY_VERSION = RUBY_VERSION
        if initialize_runtime:
            self.initialize_runtime()

    def initialize_runtime(self):
        if not self._is_initialized():
            self._download_from_s3()
            self._unpack()
            self._setup_environ()
            self._mark_initialized()

    def shell_exec(self, sh_script):
        """
        Execute command with ruby available
        """
        p = subprocess.run(sh_script,  shell=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        print(p.stderr.decode('utf-8'))
        print(p.stdout.decode('utf-8'))

    def setup_bundler_context(self, gem_file_location='/var/task/Gemfile'):
        """
        Installs gems in given Gemfile
        :param gem_file_location:
        :return:
        """
        subprocess.run(f"bundle install --gemfile={gem_file_location}", shell=True)

    def run_script(self, with_bundler_context=False):
        """
        Runs given ruby script.
        AWS_LAMBDA_EVENT is available as variable in this script
        :return:
        """
        pass

    def install_gems(self, gems):
        for gem in gems:
            subprocess.run(f"gem install {gem}", shell=True)

    def _download_from_s3(self):
        """
        Download ruby runtime binaries
        """
        account_id = boto3.client('sts').get_caller_identity()['Account']
        region = boto3.session.Session().region_name
        source_bucket = f"{account_id}.{region}.lambda-ruby-runtime"
        object_name = f"ruby-{self.RUBY_VERSION}.zip"
        boto3.resource('s3').Bucket(source_bucket).download_file(
            object_name,
            f"/tmp/{object_name}"
        )

    def _is_initialized(self):
        return f"{INITIALIZED_MARKER}{self.RUBY_VERSION}" in os.environ and os.environ[
            f"{INITIALIZED_MARKER}{self.RUBY_VERSION}"] == 'true'

    def _mark_initialized(self):
        os.environ[f"{INITIALIZED_MARKER}{self.RUBY_VERSION}"] = 'true'

    def _unpack(self):
        """
        Unpack ruby runtime binaries
        """
        # unzip iz available
        subprocess.run(f"cd /tmp && unzip /tmp/ruby-{self.RUBY_VERSION}.zip -d ruby-{self.RUBY_VERSION}", shell=True)

    def _setup_environ(self):
        """
        Setup environment so ruby binaries are available on PATH"
        """
        os.environ['PATH'] = os.environ['PATH'] + ':' + f"/tmp/ruby-{self.RUBY_VERSION}/ruby/bin"
