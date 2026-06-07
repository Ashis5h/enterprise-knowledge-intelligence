import { C, slideShell, pill } from "./common.mjs";

export async function slide01(presentation, ctx) {
  const slide = slideShell(presentation, ctx, { dark: true });
  ctx.addShape(slide, { x: 0, y: 0, w: 1280, h: 720, fill: C.navy });
  ctx.addShape(slide, { x: 760, y: 0, w: 520, h: 720, fill: C.blue2 });
  ctx.addShape(slide, { x: 805, y: 92, w: 350, h: 350, fill: "#FFFFFF18", line: { style: "solid", fill: "#FFFFFF40", width: 1 } });
  ctx.addShape(slide, { x: 865, y: 152, w: 230, h: 72, fill: "#FFFFFF", line: { style: "solid", fill: "#FFFFFF", width: 0 } });
  ctx.addShape(slide, { x: 865, y: 256, w: 230, h: 72, fill: "#DBEAFE", line: { style: "solid", fill: "#DBEAFE", width: 0 } });
  ctx.addShape(slide, { x: 865, y: 360, w: 230, h: 72, fill: "#FFFFFF", line: { style: "solid", fill: "#FFFFFF", width: 0 } });
  ctx.addText(slide, { text: "Enterprise Docs", x: 890, y: 176, w: 180, h: 26, fontSize: 18, bold: true, color: C.navy, align: "center" });
  ctx.addText(slide, { text: "Agentic RAG", x: 900, y: 280, w: 160, h: 26, fontSize: 18, bold: true, color: C.blue2, align: "center" });
  ctx.addText(slide, { text: "Grounded Answer", x: 890, y: 384, w: 180, h: 26, fontSize: 18, bold: true, color: C.navy, align: "center" });
  ctx.addText(slide, { text: "ENTERPRISE AI", x: 72, y: 72, w: 320, h: 26, fontSize: 16, bold: true, color: "#93C5FD" });
  ctx.addText(slide, {
    text: "Enterprise Knowledge\nIntelligence Platform",
    x: 72,
    y: 142,
    w: 620,
    h: 150,
    fontSize: 46,
    bold: true,
    color: C.white,
    face: ctx.fonts.title,
  });
  ctx.addText(slide, {
    text: "Fine-tuned LLMs, multi-agent RAG, evaluation pipelines, Docker deployment, and enterprise document intelligence.",
    x: 76,
    y: 318,
    w: 610,
    h: 86,
    fontSize: 22,
    color: "#D8E9FF",
  });
  pill(slide, ctx, 76, 452, 136, "FastAPI", "#1E40AF", "#FFFFFF");
  pill(slide, ctx, 228, 452, 142, "LangGraph", "#1E40AF", "#FFFFFF");
  pill(slide, ctx, 386, 452, 126, "React", "#1E40AF", "#FFFFFF");
  pill(slide, ctx, 528, 452, 136, "Pinecone", "#1E40AF", "#FFFFFF");
  ctx.addText(slide, { text: "Presented by Atul", x: 76, y: 604, w: 280, h: 30, fontSize: 19, bold: true, color: C.white });
  ctx.addText(slide, { text: "End-to-end enterprise GenAI project", x: 76, y: 635, w: 420, h: 26, fontSize: 16, color: "#BFDBFE" });
  return slide;
}
