"""Focused regression checks for natural versus strict engineering formula speech."""
import os
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from speech_structure import speak_math, SpeechMathError
from clean_speech_text import clean_speech_text

CASES=[
 (r'\frac{2}{3}', '三分之二'),
 (r'\frac{1}{4}', '四分之一'),
 (r'\frac{3}{2}', '二分之三'),
 (r'\frac{1}{100}', '百分之一'),
 (r'\frac{12}{25}', '二十五分之十二'),
 (r'\frac{R_m}{3.5}', '除以三点五'),
 (r'\frac{2}{3}R_{p0.2}', '三分之二'),
 (r'\frac{2}{3}S_y', '三分之二'),
 (r'R_m', 'R、m'),
 (r'S_y', 'S、y'),
 (r'P_d', 'P、d'),
 (r'x_1', 'x、一'),
 (r'R_{p0.2}', '下标'),
 (r'x_{12}', '下标'),
 (r'x_1^2', '下标'),
 (r'x^2', '平方'),
 (r'x^3', '立方'),
 (r'\sqrt{3}', '根号'),
 (r'\sqrt[3]{x}', '根号'),
 (r'\min(a,b)', '最小值'),
 (r'\max(a,b)', '最大值'),
 (r'\frac{a+b}{c}', '除以'),
 (r'\frac{a}{b+c}', '除以'),
 (r'\frac{a+b}{c+d}', '除以'),
 (r'\frac{3}{5}+\frac{2}{7}', '五分之三'),
 (r'x_{i+1}', '下标'),
 (r'\alpha+\beta', '阿尔法'),
 (r'\frac{\sigma_y}{2}', '除以二'),
 (r'\frac{R_m}{S_y}', '除以'),
 (r'R_m+S_y', 'R、m'),
]
class SmartMathTests(unittest.TestCase):
 def setUp(self):
  self.previous=os.environ.get('ENGINEERING_MATH_SPEECH_MODE')
  os.environ['ENGINEERING_MATH_SPEECH_MODE']='smart'
 def tearDown(self):
  if self.previous is None:
   os.environ.pop('ENGINEERING_MATH_SPEECH_MODE',None)
  else:
   os.environ['ENGINEERING_MATH_SPEECH_MODE']=self.previous
 def test_thirty_engineering_formula_cases(self):
  self.assertEqual(len(CASES),30)
  for source,expected in CASES:
   with self.subTest(source=source):
    actual=speak_math(source)
    self.assertIn(expected,actual)
 def test_repeated_complex_subscript_shorthand(self):
  actual=speak_math(r'R_{p0.2}+R_{p0.2}')
  self.assertEqual(actual.count('下标'),1,actual)
  self.assertIn('、',actual)
 def test_ambiguous_numeric_and_superscript_do_not_shorten(self):
  self.assertIn('下标',speak_math(r'x_{12}'))
  self.assertIn('下标',speak_math(r'x_1^2'))
 def test_strict_all_subscripts(self):
  actual=speak_math(r'R_m+S_y+R_{p0.2}',mode='strict')
  self.assertEqual(actual.count('下标'),3,actual)
 def test_doc_level_seen_context(self):
  actual=clean_speech_text('$$R_{p0.2}$$\n$$R_{p0.2}$$')
  self.assertEqual(actual.count('下标'),1,actual)
 def test_alternative_does_not_automatically_multiply_or(self):
  formula=r'\min\left(\frac{R_m}{3.5},\frac{2}{3}R_{p0.2}\;\left(\text{或}\;\frac{2}{3}S_y\right)\right)'
  spoken=speak_math(formula)
  self.assertIn('三分之二',spoken)
  self.assertIn('或',spoken)
  self.assertNotIn('乘以 或',spoken)
 def test_division_by_zero_is_blocked(self):
  with self.assertRaises(SpeechMathError):speak_math(r'\frac{2}{0}')
if __name__=='__main__':
 unittest.main()
