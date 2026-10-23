import sys, tempfile, unittest, zipfile
from pathlib import Path
from lxml import etree
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from omml_adapter import latex_to_omml, M_NS
from render_docx import create_docx_document

class NativeMathTests(unittest.TestCase):
    def test_relational_xml_escaping(self):
        for tex in ('x < y','a > b',r'\text{A\&B}'):
            root=etree.fromstring(latex_to_omml(tex).encode())
            self.assertEqual(root.tag,'{'+M_NS+'}oMath')
    def test_roots_and_matrix(self):
        ns={'m':M_NS}
        root=etree.fromstring(latex_to_omml(r'\sqrt[3]{x}+\begin{pmatrix}a&b\\c&d\end{pmatrix}').encode())
        self.assertEqual(len(root.xpath('.//m:rad/m:deg',namespaces=ns)),1)
        self.assertEqual(root.xpath('string(.//m:rad/m:deg)',namespaces=ns),'3')
        self.assertEqual(len(root.xpath('.//m:m/m:mr',namespaces=ns)),2)
        self.assertEqual(len(root.xpath('.//m:m/m:mr/m:e',namespaces=ns)),4)
    def test_word_structure(self):
        md=r'''## 原生公式验证

行内 $x < y$ 与 $\sqrt[3]{x}$。

$$\tau_c=\sqrt{\left(\frac{V}{A_w}\right)^2+\left(\frac{M_v}{Z_w}\right)^2}$$

| 参数 | 数值 |
| --- | --- |
| 温度 | 20 ℃ |
'''
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'原生公式.docx'; create_docx_document('原生公式','QA',md,str(p))
            with zipfile.ZipFile(p) as z:
                for name in z.namelist():
                    if name.endswith('.xml'): etree.fromstring(z.read(name))
                root=etree.fromstring(z.read('word/document.xml'))
                ns={'m':M_NS,'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                for expr,n in [('.//m:oMath',3),('.//m:f',2),('.//m:rad',2),('.//m:sSub',2),('.//m:sSup',2)]:
                    self.assertGreaterEqual(len(root.xpath(expr,namespaces=ns)),n,expr)
                self.assertTrue(root.xpath('.//w:tblHeader',namespaces=ns))
                self.assertTrue(root.xpath('.//w:keepNext',namespaces=ns))
                self.assertNotIn('\\frac',''.join(root.xpath('.//w:t/text()',namespaces=ns)))

if __name__=='__main__':unittest.main()
