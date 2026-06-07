import { C, slideShell, header, card, checkList, footer } from "./common.mjs";

export async function slide10(presentation, ctx) {
  const slide = slideShell(presentation, ctx);
  header(slide, ctx, "Status and Roadmap", "What is complete and what comes next", "The core end-to-end platform is working. The remaining items are production upgrades and GPU/cloud execution.");
  card(slide, ctx, 72, 220, 360, 300, "Completed", "FastAPI backend\nReact dashboard\nJWT login with Atul admin user\nDocument upload and retrieval\n100 generated enterprise PDFs\nMulti-agent Q&A/report workflow\nEvaluation dashboard\nDocker packaging\nPinecone integration code\nQLoRA dataset and training scaffold", { bar: C.green, bodySize: 15 });
  card(slide, ctx, 462, 220, 360, 300, "Next build items", "Actual QLoRA training on GPU\nReal AWS deployment\nReal authentication/SSO\nProduction Pinecone index testing\nExpanded real enterprise PDF dataset\nRole-based document permissions\nMonitoring and audit logs", { bar: C.blue, bodySize: 15 });
  card(slide, ctx, 852, 220, 360, 300, "Interview summary", "This project shows the full GenAI lifecycle: data, retrieval, agents, validation, evaluation, fine-tuning preparation, full-stack UI, containerization, and cloud-readiness.", { bar: C.amber, bodySize: 16 });
  checkList(slide, ctx, 160, 568, ["Demo-ready story: ask a policy question, show sources, run evaluation, explain architecture"], { w: 940, gap: 36, size: 18 });
  footer(slide, ctx, 10);
  return slide;
}
