DEFAULT_RUBY_251_LOCATION = 'https://'
DEFAULT_RUBY24_LOCATION = 'https://'


class RubyRuntime:
    
    def __init__(self, RUNTIME_ZIP_LOCATION=DEFAULT_RUBY_251_LOCATION):
        pass
    
    def shell_exec(self, sh_script):
        """
        Execute command with ruby available
        """
        pass
    
    def setup_bundler_context(self, gem_file_location='/var/task/Gemfile'):
        """
        Installs gems in given Gemfile
        :param gem_file_location:
        :return:
        """
        pass
    
    def run_script(self, with_bundler_context=False):
        """
        Runs given ruby script.
        AWS_LAMBDA_EVENT is available as variable in this script
        :return:
        """
        pass
    
    def install_gems(self, gems):
        pass
    
    def _download(self):
        """
        Download ruby runtime binaries
        """
        pass
    
    def _unpack(self):
        """
        Unpack ruby runtime binaries
        """
        pass
    
    def _setup_environ(self):
        """
        Setup environment so ruby binaries are available on PATH"
        """
        pass
