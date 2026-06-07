export const C = {
  navy: "#081B3A",
  navy2: "#0B2454",
  blue: "#2563EB",
  blue2: "#1D4ED8",
  lightBlue: "#DBEAFE",
  paleBlue: "#EFF6FF",
  bg: "#F4F8FF",
  white: "#FFFFFF",
  ink: "#06142E",
  slate: "#475569",
  muted: "#64748B",
  line: "#CFE0F6",
  green: "#0F766E",
  amber: "#B45309",
};

export function slideShell(presentation, ctx, opts = {}) {
  const slide = presentation.slides.add();
  ctx.addShape(slide, { x: 0, y: 0, w: ctx.W, h: ctx.H, fill: opts.dark ? C.navy : C.bg });
  if (!opts.dark) {
    ctx.addShape(slide, { x: 0, y: 0, w: 1280, h: 72, fill: C.white });
    ctx.addShape(slide, { x: 0, y: 70, w: 1280, h: 2, fill: C.line });
  }
  return slide;
}

export function header(slide, ctx, eyebrow, title, subtitle = "") {
  ctx.addText(slide, {
    text: eyebrow.toUpperCase(),
    x: 72,
    y: 34,
    w: 400,
    h: 24,
    fontSize: 15,
    bold: true,
    color: C.blue,
  });
  ctx.addText(slide, {
    text: title,
    x: 72,
    y: 86,
    w: 820,
    h: 58,
    fontSize: 34,
    bold: true,
    color: C.ink,
    face: ctx.fonts.title,
  });
  if (subtitle) {
    ctx.addText(slide, {
      text: subtitle,
      x: 74,
      y: 145,
      w: 870,
      h: 42,
      fontSize: 18,
      color: C.slate,
    });
  }
}

export function footer(slide, ctx, n) {
  ctx.addText(slide, {
    text: `Enterprise Knowledge Intelligence Platform | ${String(n).padStart(2, "0")}`,
    x: 72,
    y: 674,
    w: 520,
    h: 24,
    fontSize: 13,
    color: C.muted,
  });
}

export function card(slide, ctx, x, y, w, h, title, body, opts = {}) {
  ctx.addShape(slide, {
    x,
    y,
    w,
    h,
    fill: opts.fill || C.white,
    line: { style: "solid", fill: opts.line || C.line, width: 1 },
  });
  if (opts.bar) {
    ctx.addShape(slide, { x, y, w: 7, h, fill: opts.bar });
  }
  ctx.addText(slide, {
    text: title,
    x: x + 22,
    y: y + 18,
    w: w - 44,
    h: 28,
    fontSize: opts.titleSize || 18,
    bold: true,
    color: opts.titleColor || C.ink,
  });
  ctx.addText(slide, {
    text: body,
    x: x + 22,
    y: y + 55,
    w: w - 44,
    h: h - 70,
    fontSize: opts.bodySize || 15,
    color: opts.bodyColor || C.slate,
    valign: "top",
  });
}

export function pill(slide, ctx, x, y, w, text, fill = C.lightBlue, color = C.blue) {
  ctx.addShape(slide, { x, y, w, h: 34, fill, line: { style: "solid", fill, width: 0 } });
  ctx.addText(slide, {
    text,
    x,
    y: y + 7,
    w,
    h: 20,
    align: "center",
    fontSize: 13,
    bold: true,
    color,
  });
}

export function metric(slide, ctx, x, y, w, label, value, note, color = C.blue) {
  ctx.addShape(slide, { x, y, w, h: 132, fill: C.white, line: { style: "solid", fill: C.line, width: 1 } });
  ctx.addText(slide, { text: label, x: x + 22, y: y + 20, w: w - 44, h: 24, fontSize: 15, color: C.slate });
  ctx.addText(slide, { text: value, x: x + 22, y: y + 48, w: w - 44, h: 40, fontSize: 31, bold: true, color });
  if (note) {
    ctx.addText(slide, { text: note, x: x + 22, y: y + 100, w: w - 44, h: 20, fontSize: 12, color: C.muted });
  }
}

export function flowBox(slide, ctx, x, y, w, h, label, sub = "", fill = C.white) {
  ctx.addShape(slide, { x, y, w, h, fill, line: { style: "solid", fill: C.line, width: 1 } });
  ctx.addText(slide, { text: label, x: x + 14, y: y + 14, w: w - 28, h: 26, fontSize: 16, bold: true, color: C.ink, align: "center" });
  if (sub) {
    ctx.addText(slide, { text: sub, x: x + 14, y: y + 43, w: w - 28, h: h - 50, fontSize: 12, color: C.slate, align: "center" });
  }
}

export function arrow(slide, ctx, x, y, w = 40) {
  ctx.addShape(slide, { x, y: y + 13, w, h: 4, fill: C.blue, line: { style: "solid", fill: C.blue, width: 0 } });
  ctx.addText(slide, { text: ">", x: x + w - 6, y: y + 1, w: 26, h: 30, fontSize: 24, bold: true, color: C.blue, align: "center" });
}

export function checkList(slide, ctx, x, y, items, opts = {}) {
  items.forEach((item, index) => {
    const top = y + index * (opts.gap || 48);
    ctx.addShape(slide, { x, y: top + 4, w: 20, h: 20, fill: opts.dot || C.blue, line: { style: "solid", fill: opts.dot || C.blue, width: 0 } });
    ctx.addText(slide, { text: item, x: x + 34, y: top, w: opts.w || 460, h: 34, fontSize: opts.size || 17, color: opts.color || C.ink });
  });
}
