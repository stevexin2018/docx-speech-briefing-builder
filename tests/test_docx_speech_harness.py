"""Compatibility entry: share the complete harness used by managed deployment."""
from pathlib import Path
import runpy

_harness = runpy.run_path(str(Path(__file__).resolve().parents[1] / 'test_docx_speech_harness.py'))
test_speech_cleaning = _harness['test_speech_cleaning']
test_si_unit_verbalizer_matrix = _harness['test_si_unit_verbalizer_matrix']
test_docx_rendering = _harness['test_docx_rendering']

if __name__ == '__main__':
    test_speech_cleaning()
    test_si_unit_verbalizer_matrix()
    test_docx_rendering()
