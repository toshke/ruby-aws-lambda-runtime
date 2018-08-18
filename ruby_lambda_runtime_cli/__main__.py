import logging
import sys

from ruby_lambda_runtime.binary_generator import RubyRuntimeBinaryGenerator


def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def main(args=None):
    """The main routine."""

    def print_help_end_exit():
        print("Usage:\n\truby-lambda-runtime generate-binaries [ruby_version]\n\t" +
              "ruby-lambda-runtime upload-precompiled-binaries [ruby_version]")
        sys.exit(-2)

    if args is None:
        args = sys.argv[1:]
    if len(args) < 1:
        print_help_end_exit()

    cmd = args[0]
    if cmd == 'generate-binaries':
        RubyRuntimeBinaryGenerator().generate_binaries()
    elif cmd == 'upload-precompiled-binaries':
        RubyRuntimeBinaryGenerator().upload_precompiled()
    else:
        print_help_end_exit()


if __name__ == "__main__":
    main()
