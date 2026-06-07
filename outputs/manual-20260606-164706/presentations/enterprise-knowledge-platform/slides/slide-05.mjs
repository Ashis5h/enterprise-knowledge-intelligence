import { C, slideShell, header, flowBox, arrow, card, footer } from "./common.mjs";

export async function slide05(presentation, ctx) {
  const slide = slideShell(presentation, ctx);
  header(slide, ctx, "Agentic AI", "LangGraph multi-agent workflow", "Each request is routed through specialized agents so retrieval, reasoning, reporting, and validation stay modular and testable.");
  flowBox(slide, ctx, 90, 242, 180, 82, "User Question", "mode: qa / report", C.white);
  arrow(slide, ctx, 286, 263, 52);
  flowBox(slide, ctx, 354, 242, 190, 82, "Retrieval Agent", "gets source context", C.lightBlue);
  arrow(slide, ctx, 560, 263, 52);
  flowBox(slide, ctx, 628, 242, 190, 82, "Reasoning Agent", "drafts answer", C.white);
  arrow(slide, ctx, 834, 263, 52);
  flowBox(slide, ctx, 902, 242, 190, 82, "Validation Agent", "checks grounding", C.lightBlue);
  ctx.addShape(slide, { x: 992, y: 324, w: 4, h: 80, fill: C.blue });
  flowBox(slide, ctx, 902, 404, 190, 82, "Final Response", "answer + citations", C.white);
  ctx.addShape(slide, { x: 722, y: 324, w: 4, h: 72, fill: C.blue });
  ctx.addShape(slide, { x: 724, y: 392, w: 178, h: 4, fill: C.blue });
  flowBox(slide, ctx, 610, 404, 230, 82, "Report Agent", "summary, findings, actions", C.white);
  card(slide, ctx, 102, 548, 306, 84, "Why agents matter", "Cleaner responsibilities, easier debugging, and a natural story for enterprise workflows.", { bodySize: 14 });
  card(slide, ctx, 486, 548, 306, 84, "Hallucination control", "Validation only marks the answer grounded when retrieved context supports it.", { bodySize: 14 });
  card(slide, ctx, 870, 548, 306, 84, "Extensible design", "New agents can be added for compliance, workflow actions, or approval routing.", { bodySize: 14 });
  footer(slide, ctx, 5);
  return slide;
}
