import { C, slideShell, header, flowBox, arrow, footer } from "./common.mjs";

export async function slide03(presentation, ctx) {
  const slide = slideShell(presentation, ctx);
  header(slide, ctx, "Architecture", "High-level system design", "React handles the user experience, FastAPI exposes APIs, LangGraph routes work across agents, and the vector layer grounds responses in enterprise documents.");
  flowBox(slide, ctx, 76, 230, 140, 74, "User", "Atul / employee", C.white);
  arrow(slide, ctx, 226, 250, 36);
  flowBox(slide, ctx, 278, 230, 150, 74, "React UI", "chat, docs, analytics", C.paleBlue);
  arrow(slide, ctx, 438, 250, 36);
  flowBox(slide, ctx, 492, 230, 170, 74, "FastAPI", "auth + REST APIs", C.white);
  arrow(slide, ctx, 674, 250, 36);
  flowBox(slide, ctx, 728, 230, 178, 74, "LangGraph", "agent router", C.lightBlue);
  arrow(slide, ctx, 918, 250, 36);
  flowBox(slide, ctx, 972, 230, 180, 74, "Final Answer", "validated + cited", C.white);
  const agents = [
    ["Retrieval Agent", "searches vector DB", 198],
    ["Reasoning Agent", "generates answer", 408],
    ["Report Agent", "summaries and reports", 618],
    ["Validation Agent", "checks grounding", 828],
  ];
  agents.forEach(([name, sub, x]) => flowBox(slide, ctx, x, 392, 170, 86, name, sub, C.white));
  ctx.addShape(slide, { x: 806, y: 304, w: 4, h: 88, fill: C.blue });
  ctx.addShape(slide, { x: 276, y: 374, w: 720, h: 4, fill: C.blue });
  ctx.addShape(slide, { x: 282, y: 374, w: 4, h: 18, fill: C.blue });
  ctx.addShape(slide, { x: 492, y: 374, w: 4, h: 18, fill: C.blue });
  ctx.addShape(slide, { x: 702, y: 374, w: 4, h: 18, fill: C.blue });
  ctx.addShape(slide, { x: 912, y: 374, w: 4, h: 18, fill: C.blue });
  flowBox(slide, ctx, 328, 550, 220, 78, "Vector DB", "local hash / Chroma / Pinecone", C.paleBlue);
  arrow(slide, ctx, 560, 572, 52);
  flowBox(slide, ctx, 628, 550, 260, 78, "Enterprise Documents", "100 generated PDFs + uploads", C.white);
  arrow(slide, ctx, 900, 572, 52);
  flowBox(slide, ctx, 968, 550, 180, 78, "Embeddings", "local-hash baseline", C.paleBlue);
  footer(slide, ctx, 3);
  return slide;
}
