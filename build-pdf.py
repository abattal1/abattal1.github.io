# -*- coding: utf-8 -*-
"""Builds Abdikadir_Battal_Portfolio.pdf. Copy comes from copy.py, so the PDF
and the website can never drift. Fonts and images are embedded, so this runs
with no network. Render step is at the bottom."""
import base64, io, os, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from portfolio_copy import render

W = os.path.dirname(os.path.abspath(__file__))
def b64(p): return base64.b64encode(open(p, "rb").read()).decode()
def blk(sec, head): return '<div class="blk"><h3>%s</h3>%s</div>' % (head, render((sec, head)))
def cols(sec, heads): return '<div class="cols">%s</div>' % "".join(blk(sec, h) for h in heads)

F = W + "/node_modules/@fontsource"
def face(fam, f, wt, style="normal"):
    return ('@font-face{font-family:"%s";font-style:%s;font-weight:%d;font-display:block;'
            'src:url(data:font/woff2;base64,%s) format("woff2");}' % (fam, style, wt, b64(f)))
faces = "".join([
 face("Bricolage Grotesque", F+"/bricolage-grotesque/files/bricolage-grotesque-latin-700-normal.woff2", 700),
 face("Bricolage Grotesque", F+"/bricolage-grotesque/files/bricolage-grotesque-latin-800-normal.woff2", 800),
 face("Newsreader", F+"/newsreader/files/newsreader-latin-300-normal.woff2", 300),
 face("Newsreader", F+"/newsreader/files/newsreader-latin-400-normal.woff2", 400),
 face("Newsreader", F+"/newsreader/files/newsreader-latin-500-normal.woff2", 500),
 face("Newsreader", F+"/newsreader/files/newsreader-latin-400-italic.woff2", 400, "italic"),
 face("IBM Plex Mono", F+"/ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2", 400),
 face("IBM Plex Mono", F+"/ibm-plex-mono/files/ibm-plex-mono-latin-600-normal.woff2", 600),
])
def img(k):
    ext = "jpeg" if k in ("s5", "s6") else "png"
    return "data:image/%s;base64,%s" % (ext, b64("%s/img/%s.%s" % (W, k, ext)))

CSS = """
:root{--paper:#fff;--ink:#141D26;--ink2:#4A5860;--ink3:#7B8A8C;--line:#CFD6CB;--soft:#E3E8DF;--spine:#2B4763;}
@page{size:letter;margin:0.5in 0.55in 0.45in;}
*{box-sizing:border-box;}
html,body{margin:0;padding:0;}
body{font-family:"Newsreader",Georgia,serif;font-size:8.7pt;line-height:1.44;color:var(--ink);background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact;}
h1,h2,h3{font-family:"Bricolage Grotesque","Helvetica Neue",sans-serif;margin:0;}
.page{page-break-after:always;}
.page:last-child{page-break-after:auto;}
.eye{font-family:"IBM Plex Mono",monospace;font-size:6.4pt;font-weight:600;letter-spacing:.15em;text-transform:uppercase;color:var(--ink3);}
.mast{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;border-bottom:1.5pt solid var(--ink);padding-bottom:7px;}
.mast h1{font-size:25pt;font-weight:800;letter-spacing:-.03em;line-height:.95;}
.mast .who{font-size:7.6pt;line-height:1.4;color:var(--ink2);max-width:2.9in;text-align:right;}
.blurb{margin:7px 0 0;font-size:9.6pt;line-height:1.38;font-weight:300;max-width:6in;}
.ph{display:flex;align-items:baseline;justify-content:space-between;gap:16px;}
.ph h2{font-size:16pt;font-weight:700;letter-spacing:-.025em;line-height:1.05;}
.ph .where{font-family:"IBM Plex Mono",monospace;font-size:6.4pt;letter-spacing:.1em;text-transform:uppercase;color:var(--ink3);text-align:right;line-height:1.5;}
.tag{margin:5px 0 0;font-size:10.5pt;line-height:1.3;font-weight:300;max-width:4.6in;color:var(--ink);}
.figs{display:flex;margin:9px 0 0;border-top:.75pt solid var(--line);border-bottom:.75pt solid var(--line);}
.fig{flex:1;padding:5px 10px 5px 0;border-right:.5pt solid var(--soft);}
.fig:first-child{padding-left:0;}
.fig:last-child{border-right:0;}
.fig .k{font-family:"IBM Plex Mono",monospace;font-size:5.9pt;letter-spacing:.12em;text-transform:uppercase;color:var(--ink3);}
.fig .v{font-family:"Bricolage Grotesque",sans-serif;font-weight:700;font-size:15pt;line-height:1.1;letter-spacing:-.03em;}
.fig .v s{font-family:"IBM Plex Mono",monospace;font-size:6.2pt;font-weight:400;letter-spacing:.03em;color:var(--ink3);text-decoration:none;margin-left:3px;}
.cols{column-count:2;column-gap:0.3in;column-rule:.5pt solid var(--soft);margin-top:10px;}
.blk{break-inside:avoid;margin:0 0 9px;}
.blk h3{font-family:"Bricolage Grotesque",sans-serif;font-size:9.2pt;font-weight:700;letter-spacing:-.015em;color:var(--ink);margin-bottom:3px;padding-bottom:2px;border-bottom:1.2pt solid rgba(43,71,99,.22);}
.blk p{margin:0;color:var(--ink);font-weight:500;line-height:1.4;}
.blk p strong,.blk li strong{color:var(--ink);font-weight:500;}
.blk p em,.blk li em{color:var(--ink);font-style:italic;}
.blk ul{list-style:none;margin:5px 0 0;padding:0;}
.blk li{position:relative;padding-left:10pt;margin:0 0 3.5px;color:var(--ink);line-height:1.4;}
.blk li:last-child{margin-bottom:0;}
.blk li::before{content:"";position:absolute;left:0;top:5.2pt;width:5pt;height:.6pt;background:var(--spine);opacity:.55;}
.shots{display:flex;gap:11px;margin-top:11px;}
.shots figure{flex:1;margin:0;break-inside:avoid;page-break-inside:avoid;}
.shots img{display:block;width:100%;border:.75pt solid var(--line);}
.shots.tight img{width:auto;max-width:100%;max-height:1.3in;margin:0 auto;}
.cap{margin-top:3px;font-size:6.8pt;line-height:1.32;color:var(--ink3);}
"""

WHERE = 'Kaas Tailored, Mukilteo WA<br>Data Analyst Intern &middot; 2026, %s'
def phead(num, title, where):
    return ('<div class="ph"><div><span class="eye">Project %s</span><h2>%s</h2></div>'
            '<div class="where">%s</div></div>' % (num, title, WHERE % where))
def shots(items, cls=""):
    f = "".join('<figure><img src="%s"><figcaption class="cap">%s</figcaption></figure>' % (img(k), c)
                for k, c in items)
    return '<div class="shots %s">%s</div>' % (cls, f)

HEAD = ('<div class="mast"><h1>Abdikadir Battal</h1><div class="who">'
        'Incoming freshman at the University of Washington, Engineering Undeclared, heading for '
        'Industrial and Systems Engineering.<br>Data analyst intern at Kaas Tailored in Mukilteo.'
        '</div></div>'
        '<p class="blurb">Three projects, all of them the same problem in different clothing. A plant '
        'knows something in a form nobody can use, and somebody has to turn that into a thing a lead '
        'can actually open in the morning.</p>')

FIGS1 = ('<div class="figs">'
 '<div class="fig"><div class="k">Departments completed</div><div class="v">15</div></div>'
 '<div class="fig"><div class="k">Leads met with</div><div class="v">14</div></div>'
 '<div class="fig"><div class="k">Tasks defined</div><div class="v">440</div></div>'
 '<div class="fig"><div class="k">Skill-task links</div><div class="v">1,123</div></div>'
 '<div class="fig"><div class="k">Shared library</div><div class="v">362<s>129 cross-dept</s></div></div>'
 '</div>')

P1 = ('<div style="margin-top:13px">'
 + phead("01", "Skills and Tasks Tracker", "completed")
 + '<p class="tag">Finding the jobs that only one person in the department can do.</p>'
 + FIGS1
 + cols("p1", ["What it is", "What I did", "Challenges", "Results", "Skills learned"])
 + shots([("s1", "Task Definitions tab, Crew Seating. Every task carries a plain definition, so a new hire can read it and know what they are supposed to learn."),
          ("s2", "Skill-Task Map. Tasks down the side, skills across the top, each cell holding the level that skill has to reach. The names are formulas pulling from the shared library.")], "tight")
 + '</div>')

P2 = (phead("02", "Daily Report-Out, Crew Seating", "completed")
 + '<p class="tag">One page a lead can read in the first five minutes of the day.</p>'
 + shots([("s3", "Target against actual earned hours, then every production line ranked by how far over the expected time it ran. The ten-week trend underneath separates a bad day from a bad standard."),
          ("s4", "Rework carries its own panel because it is measured against a target of zero, so every minute on it is pure loss. Underneath, the day opens from line to part to individual job.")])
 + cols("p2", ["What it is", "What I did", "Challenges", "Results", "Skills learned"]))

P3 = (phead("03", "Sales Forecast Tool", "prototype v8")
 + '<p class="tag">A hand-entered forecast sitting next to a predicted one, so neither has to be taken on faith.</p>'
 + cols("p3", ["What it is", "What I did", "Skills learned"])
 + shots([("s5", "Prototype v8, page 1. The monthly grid for one projection group, with the 24 month lock, Capacity Total and open orders side by side, and the Horizon column marking whether a month sits within 3, 12 or 24 months. Customer names are anonymized in the prototype."),
          ("s6", "Page 2. The annual totals beyond the window, the legend for what is frozen against what is editable, and the formula self-test the prototype runs against a worked example.")]))

html = ('<!doctype html><html><head><meta charset="utf-8">'
        '<title>Abdikadir Battal, project portfolio</title><style>' + faces + CSS + '</style></head><body>'
        '<div class="page">' + HEAD + P1 + '</div>'
        '<div class="page">' + P2 + '</div>'
        '<div class="page">' + P3 + '</div></body></html>')

io.open(W + "/portfolio-print.html", "w", encoding="utf-8").write(html)
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
out = W + "/Abdikadir_Battal_Portfolio.pdf"
subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
                "--print-to-pdf=" + out, "--virtual-time-budget=12000",
                "file://" + W + "/portfolio-print.html"],
               capture_output=True)
import re as _re
d = open(out, "rb").read()
print("pages:", len(_re.findall(rb"/Type\s*/Page[^s]", d)), "bytes:", len(d))
