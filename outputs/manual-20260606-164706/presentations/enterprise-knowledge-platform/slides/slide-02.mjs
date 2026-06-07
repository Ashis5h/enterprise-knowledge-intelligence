import { C, slideShell, header, card, footer, checkList } from "./common.mjs";

export async function slide02(presentation, ctx) {
  const slide = slideShell(presentation, ctx);
  header(slide, ctx, "Problem and Objective", "From document overload to trusted answers", "The platform is built for organizations where critical knowledge is spread across policies, SOPs, manuals, reports, and knowledge-base documents.");
  card(slide, ctx, 72, 230, 336, 270, "Enterprise pain points", "Employees waste time searching scattered documents.\n\nGeneric chatbots hallucinate because they are not grounded in approved sources.\n\nTeams need summaries, comparisons, and decision support with citations.", { bar: C.amber });
  card(slide, ctx, 472, 230, 336, 270, "Project objective", "Build a full-stack GenAI platform that retrieves trusted enterprise context, reasons over it, validates the answer, and exposes it through a practical dashboard.", { bar: C.blue });
  card(slide, ctx, 872, 230, 336, 270, "Differentiator", "This is not only RAG. It combines agentic workflow, metadata governance, evaluation metrics, Docker, Pinecone support, and a QLoRA fine-tuning path.", { bar: C.green });
  checkList(slide, ctx, 164, 545, ["Grounded Q&A with sources", "Report mode for executive summaries", "Evaluation dashboard for quality tracking"], { w: 950, gap: 38, size: 16 });
  footer(slide, ctx, 2);
  return slide;
}
