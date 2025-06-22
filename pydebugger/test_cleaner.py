import pytest
from cleaner import DebugCleaner

@pytest.fixture
def manager():
    return DebugCleaner()

@pytest.mark.parametrize("input_line, expected_line", [
    # Simple cases
    ("debug(a=1, debug=1)", "debug(a=1)"),
    ("debug(debug=1)", "debug()"),
    ("debug(a=1, debug=1, b=2)", "debug(a=1, b=2)"),
    
    # Variants with spacing
    ("debug(a = 1 ,debug =1)", "debug(a = 1)"),
    ("debug( foo = bar , debug=1 )", "debug(foo = bar)"),
    ("debug( debug = 1 , )", "debug()"),
    ("debug(debug = 1,)", "debug()"),
    ("debug(a=1,debug = 1,)", "debug(a=1)"),
    
    # No debug=1 present
    ("debug(a=1)", "debug(a=1)"),
    ("debug(foo=bar, debug=verbose)", "debug(foo=bar, debug=verbose)"),

    # Multi-line call should be ignored in this implementation
    ("debug(\n  a=1,\n  debug=1\n)", "debug(\n  a=1,\n  debug=1\n)"),
])
def test_clean_action(manager, input_line, expected_line):
    output_line, changed = manager.process_line(input_line, action="clean")
    assert output_line.strip() == expected_line.strip()

if __name__ == '__main__':
    import sys
    sys.exit(pytest.main([__file__]))
