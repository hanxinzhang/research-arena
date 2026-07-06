# Bundled Inter Font

Research Arena vendors Inter so every run has a known open-source manuscript and
figure font without depending on system font installation.

Source: Inter release `4.1` from `rsms/inter`.

Included files:

- `Inter-Regular.ttf`
- `Inter-Bold.ttf`
- `Inter-Italic.ttf`
- `Inter-BoldItalic.ttf`
- `LICENSE.txt`

Use `agents/templates/figure_style.py` to register these files with Matplotlib
before creating figures or Matplotlib-rendered manuscript PDFs.

For XeLaTeX manuscripts, use the bundled files with `fontspec` when Inter is not
installed locally.
