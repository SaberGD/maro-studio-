"""Regression coverage for mixing a new landing page with cached old CSS/JS."""
import re
import tempfile
import unittest
from pathlib import Path
from prepare_download import prepare


class LandingAssetsTest(unittest.TestCase):
    def test_changed_content_changes_only_its_asset_url(self):
        with tempfile.TemporaryDirectory() as work:
            directory = Path(work)
            (directory / "index.html").write_text(
                '<head><link href="styles.css?v=one"><script src="script.js?v=one"></script></head>'
            )
            (directory / "styles.css").write_text("body{color:red}")
            (directory / "script.js").write_text("console.log(1)")
            prepare(directory, "same-build")
            first = (directory / "index.html").read_text()
            first_css = re.search(r'styles\.[a-f0-9]{16}\.css', first)[0]
            first_js = re.search(r'script\.[a-f0-9]{16}\.js', first)[0]
            # Rebuilding the same input is deterministic.
            prepare(directory, "same-build")
            self.assertEqual(first, (directory / "index.html").read_text())
            (directory / "styles.css").write_text("body{color:blue}")
            prepare(directory, 'next&"build')
            second = (directory / "index.html").read_text()
            second_css = re.search(r'styles\.[a-f0-9]{16}\.css', second)[0]
            self.assertNotEqual(first_css, second_css)
            self.assertIn(first_js, second)
            self.assertEqual((directory / second_css).read_bytes(), (directory / "styles.css").read_bytes())
            self.assertEqual(second.count('name="horix-build"'), 1)
            self.assertIn('next&amp;&quot;build', second)


if __name__ == "__main__":
    unittest.main()
