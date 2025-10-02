from vm import VM
from compiler import compile_file
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/run.py examples/fib.mvm")
        sys.exit(1)

    filename = sys.argv[1]
    program = compile_file(filename)
    vm = VM()
    vm.run(program)
