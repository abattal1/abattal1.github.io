const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
        ImageRun, Table, TableRow, TableCell, WidthType, BorderStyle,
        ShadingType, PageBreak, LevelFormat, convertInchesToTwip } = require("docx");

const COPY = JSON.parse(fs.readFileSync("/root/work/copy.json", "utf8"));
const NAVY = "2B4763", INK = "141D26", GREY = "5A686E", AMBER = "C9A145";

// strip the <strong>/<em> markup the web copy carries and turn it into runs
function runs(html, opts = {}) {
  const out = [];
  const re = /<(strong|em)>(.*?)<\/\1>/g;
  let last = 0, m;
  while ((m = re.exec(html))) {
    if (m.index > last) out.push(new TextRun({ text: html.slice(last, m.index), ...opts }));
    out.push(new TextRun({ text: m[2], ...opts, bold: m[1] === "strong" || opts.bold,
                           italics: m[1] === "em" || opts.italics }));
    last = re.lastIndex;
  }
  if (last < html.length) out.push(new TextRun({ text: html.slice(last), ...opts }));
  return out;
}

const P = (html, o = {}) => new Paragraph({
  children: runs(html, { size: o.size || 21, color: o.color || INK, bold: o.bold, italics: o.italics }),
  spacing: { after: o.after === undefined ? 120 : o.after, line: 276 },
  alignment: o.align,
});
const H = (text, level, o = {}) => new Paragraph({
  children: [new TextRun({ text, bold: true, size: o.size || 24, color: o.color || INK })],
  heading: level, spacing: { before: o.before === undefined ? 240 : o.before, after: 100 },
  border: o.rule ? { bottom: { style: BorderStyle.SINGLE, size: 6, color: "C6D0DA", space: 3 } } : undefined,
});
const BULLET = (html) => new Paragraph({
  children: runs(html, { size: 21, color: INK }),
  numbering: { reference: "dash", level: 0 },
  spacing: { after: 90, line: 276 },
});
const LABEL = (text) => new Paragraph({
  children: [new TextRun({ text, size: 15, color: GREY, characterSpacing: 30, allCaps: true, bold: true })],
  spacing: { after: 40 },
});

function imgRun(key, widthIn, maxHIn) {
  const ext = (key === "s5" || key === "s6") ? "jpeg" : "png";
  const d = COPY.dims[key];
  let w = widthIn * 96, h = w * d[1] / d[0];
  const maxH = maxHIn * 96;
  if (h > maxH) { w = w * maxH / h; h = maxH; }
  return new ImageRun({ type: ext === "jpeg" ? "jpg" : "png",
    data: fs.readFileSync(`/root/work/img/${key}.${ext}`),
    transformation: { width: Math.round(w), height: Math.round(h) } });
}
const NOBORDER = { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
                   left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } };
// two screenshots side by side in a borderless table, so they never take a page of their own
function shotRow(shots, widthIn, maxHIn) {
  const cellW = 5328;
  const cells = shots.map(([key, cap]) => new TableCell({
    width: { size: cellW, type: WidthType.DXA }, borders: NOBORDER,
    margins: { top: 60, bottom: 60, left: 0, right: 140 },
    children: [
      new Paragraph({ children: [imgRun(key, widthIn, maxHIn)], spacing: { after: 60 } }),
      new Paragraph({ children: [new TextRun({ text: cap, size: 15, color: GREY, italics: true })] }),
    ],
  }));
  return new Table({ columnWidths: [cellW, cellW], width: { size: cellW * 2, type: WidthType.DXA },
                     borders: NOBORDER, rows: [new TableRow({ children: cells })] });
}

function project(sec, num, title, where, tagline, heads, figs, shots) {
  const c = [];
  c.push(LABEL(`Project ${num}`));
  c.push(H(title, HeadingLevel.HEADING_1, { size: 32, color: NAVY, before: 0 }));
  c.push(P(where, { size: 17, color: GREY, after: 60 }));
  c.push(P(tagline, { size: 25, after: 160 }));
  if (figs) { c.push(figs); c.push(new Paragraph({ text: "", spacing: { after: 120 } })); }
  c.push(shots);
  c.push(new Paragraph({ text: "", spacing: { after: 160 } }));
  for (const h of heads) {
    const b = COPY.blocks[sec][h];
    c.push(H(h, HeadingLevel.HEADING_2, { size: 23, rule: true }));
    c.push(P(b.lead, { bold: true, after: 100 }));
    for (const x of b.bullets) c.push(BULLET(x));
  }
  return c;
}

const statCells = COPY.stats.map(([k, v]) => new TableCell({
  width: { size: 2131, type: WidthType.DXA },
  margins: { top: 90, bottom: 90, left: 100, right: 100 },
  shading: { type: ShadingType.CLEAR, fill: "F2F4EF" },
  borders: { top: { style: BorderStyle.SINGLE, size: 4, color: "D8DED6" },
             bottom: { style: BorderStyle.SINGLE, size: 4, color: "D8DED6" },
             left: { style: BorderStyle.SINGLE, size: 4, color: "D8DED6" },
             right: { style: BorderStyle.SINGLE, size: 4, color: "D8DED6" } },
  children: [
    new Paragraph({ children: [new TextRun({ text: k, size: 14, color: GREY, bold: true, allCaps: true })], spacing: { after: 30 } }),
    new Paragraph({ children: [new TextRun({ text: v, size: 28, bold: true, color: NAVY })] }),
  ],
}));
const statTable = new Table({
  columnWidths: [2131, 2131, 2131, 2131, 2131],
  width: { size: 10655, type: WidthType.DXA },
  rows: [new TableRow({ children: statCells })],
});

const body = [
  new Paragraph({ children: [new TextRun({ text: "Abdikadir Battal", bold: true, size: 56, color: INK })],
    spacing: { after: 60 } }),
  P("Incoming freshman at the University of Washington, Engineering Undeclared, heading for Industrial and Systems Engineering. Data analyst intern at Kaas Tailored in Mukilteo.",
    { size: 19, color: GREY, after: 160 }),
  P(COPY.blurb, { size: 24, after: 60 }),
  new Paragraph({ text: "", border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: INK, space: 6 } }, spacing: { after: 260 } }),

  ...project("p1", "01", "Skills and Tasks Tracker", COPY.where.p1, COPY.taglines.p1,
    ["What it is", "What I did", "Challenges", "Results", "Skills learned"], statTable,
    shotRow([["s1", "Task Definitions tab, Crew Seating. Every task carries a plain definition, so a new hire can read it and know what they are supposed to learn."],
             ["s2", "Skill-Task Map. Tasks down the side, skills across the top, each cell holding the level that skill has to reach."]], 3.35, 2.3)),
  new Paragraph({ children: [new PageBreak()] }),

  ...project("p2", "02", "Daily Report-Out, Crew Seating", COPY.where.p2, COPY.taglines.p2,
    ["What it is", "What I did", "Challenges", "Results", "Skills learned"], null,
    shotRow([["s3", "Target against actual earned hours, then every production line ranked by how far over the expected time it ran."],
             ["s4", "Rework carries its own panel, measured against a target of zero hours. Underneath, the day opens from line to part to individual job."]], 3.35, 2.6)),
  new Paragraph({ children: [new PageBreak()] }),

  ...project("p3", "03", "Sales Forecast Tool", COPY.where.p3, COPY.taglines.p3,
    ["What it is", "What I did", "Skills learned"], null,
    shotRow([["s5", "Prototype v8, page 1. The monthly grid for one projection group, with the 24 month lock, Capacity Total and open orders side by side. Customer names are anonymized in the prototype."],
             ["s6", "Page 2. The annual totals beyond the window, the legend for what is frozen against what is editable, and the formula self-test."]], 3.35, 2.9)),
];

const doc = new Document({
  creator: "Abdikadir Battal",
  title: "Abdikadir Battal, project portfolio",
  numbering: { config: [{ reference: "dash", levels: [{
      level: 0, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 300, hanging: 200 } },
               run: { color: AMBER, bold: true } } }] }] },
  styles: { default: { document: { run: { font: "Calibri", size: 21, color: INK } } } },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 },
      margin: { top: 900, right: 900, bottom: 900, left: 900 } } },
    children: body,
  }],
});

Packer.toBuffer(doc).then(b => {
  fs.writeFileSync("/root/work/Abdikadir_Battal_Portfolio.docx", b);
  console.log("written", b.length, "bytes");
});
