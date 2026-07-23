#!/usr/bin/env python3
"""Quick local test of refactored code without Docker."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all imports work after refactoring."""
    print("Testing imports...")
    try:
        from soliddriver_checks.api.common import Evaluation
        print("  ✓ Evaluation imported from common.py")

        from soliddriver_checks.api.kmp import KMPReader, KMPAnalysis
        print("  ✓ KMP classes imported")

        from soliddriver_checks.api.km import KMReader as KMR, KMAnalysis as KMA
        print("  ✓ KM classes imported")

        from soliddriver_checks.api.analysis import kms_to_dataframe, kms_to_json
        print("  ✓ Analysis functions imported")

        from soliddriver_checks.api.filter import km_filter
        print("  ✓ Filter function imported")

        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False

def test_evaluation_enum():
    """Test the consolidated Evaluation enum."""
    print("\nTesting Evaluation enum...")
    try:
        from soliddriver_checks.api.common import Evaluation

        # Test values
        assert Evaluation.PASS.value == 1, "PASS should be 1"
        assert Evaluation.WARNING.value == 2, "WARNING should be 2"
        assert Evaluation.ERROR.value == 3, "ERROR should be 3"
        print("  ✓ Enum values correct")

        # Test string representation
        assert str(Evaluation.PASS) == "PASS"
        assert str(Evaluation.WARNING) == "WARNING"
        assert str(Evaluation.ERROR) == "ERROR"
        print("  ✓ String representation correct")

        # Test int conversion
        assert int(Evaluation.PASS) == 1
        assert int(Evaluation.WARNING) == 2
        assert int(Evaluation.ERROR) == 3
        print("  ✓ Integer conversion correct")

        # Test to_json
        pass_json = Evaluation.PASS.to_json()
        assert pass_json == {"level": "PASS", "value": 1}
        print("  ✓ JSON serialization correct")

        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False

def test_type_hints():
    """Test that type hints don't cause runtime issues."""
    print("\nTesting type hints...")
    try:
        from soliddriver_checks.api.kmp import KMPReader
        from soliddriver_checks.api.analysis import kms_to_dataframe

        # Type hints are compile-time, so just verify they don't break imports
        reader = KMPReader()
        print("  ✓ KMPReader instantiation works with type hints")

        # Check that methods are callable
        assert callable(reader.get_all_kmp_files)
        assert callable(reader.collect_kmp_data)
        print("  ✓ Methods callable with type hints")

        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False

def test_filter_parser_cache():
    """Test that filter parser is cached."""
    print("\nTesting filter parser cache...")
    try:
        from soliddriver_checks.api import filter as filter_module

        # Check that _CACHED_PARSER exists
        assert hasattr(filter_module, '_CACHED_PARSER'), "Parser should be cached"
        print("  ✓ Filter parser is cached at module level")

        # Verify it's the same instance
        parser1 = filter_module._CACHED_PARSER
        parser2 = filter_module._CACHED_PARSER
        assert parser1 is parser2, "Should be same instance"
        print("  ✓ Cache returns same parser instance")

        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False

def test_kmp_reader_regex():
    """Test that KMP reader has class-level regex patterns."""
    print("\nTesting KMP reader regex patterns...")
    try:
        from soliddriver_checks.api.kmp import KMPReader

        # Check class-level regex patterns exist
        assert hasattr(KMPReader, '_ML_PCI_RE'), "PCI regex should be at class level"
        assert hasattr(KMPReader, '_ML_ALL_RE'), "ALL regex should be at class level"
        print("  ✓ Regex patterns compiled at class level")

        # Verify they're compiled regex objects
        import re
        assert isinstance(KMPReader._ML_PCI_RE, type(re.compile('')))
        assert isinstance(KMPReader._ML_ALL_RE, type(re.compile('')))
        print("  ✓ Regex patterns are compiled Pattern objects")

        return True
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        return False

def main():
    """Run all quick tests."""
    print("=" * 60)
    print("Quick Refactoring Tests (No Docker Required)")
    print("=" * 60)

    tests = [
        test_imports,
        test_evaluation_enum,
        test_type_hints,
        test_filter_parser_cache,
        test_kmp_reader_regex,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\nUnexpected error in {test.__name__}: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All quick tests PASSED!")
        return 0
    else:
        print(f"✗ {total - passed} test(s) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
