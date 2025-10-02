from src.vm import VM
from src.compiler import compile_example

def test_vm_addition(capsys):
    vm = VM()
    program = compile_example()
    vm.run(program)
    out, _ = capsys.readouterr()
    assert out.strip() == "5"
