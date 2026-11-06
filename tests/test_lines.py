from provenance.trace.lines import logic_lines

PYTHON = b"""'''Module docstring here.'''
import os
from a import b

# a comment line here
def f(x, y):
    '''Doc string line.'''
    if x > y:
        return x + y
    return None
"""

C = b"""#include <stdio.h>
/* comment words here */
int f(int a) {
    if (a > 1) {
        return a + 1;
    }
    return 0;
}
"""


def test_python_keeps_code_only():
    assert logic_lines(PYTHON, "python") == {6, 8, 9}


def test_c_keeps_code_only():
    assert logic_lines(C, "c") == {3, 4, 5, 7}
