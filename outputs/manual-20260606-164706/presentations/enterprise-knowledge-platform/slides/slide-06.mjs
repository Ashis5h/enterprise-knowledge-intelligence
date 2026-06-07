import { C, slideShell, header, metric, card, footer } from "./common.mjs";

export async function slide06(presentation, ctx) {
  const slide = slideShell(presentation, ctx);
  header(slide, ctx, "Evaluation", "Quality dashboard and benchmark suite", "The app includes a RAGAS-style evaluation page to show faithfulness, context precision, answer relevancy, context recall, hallucination rate, and pass rate.");
  metric(slide, ctx, 72, 238, 250, "Queries", "100+", "after dataset upload", C.blue);
  metric(slide, ctx, 352, 238, 250, "Faithfulness", "0.83", "sample benchmark run", C.green);
  metric(slide, ctx, 632, 238, 250, "Context Precision", "0.61", "retrieval quality signal", C.blue);
  metric(slide, ctx, 912, 238, 250, "Hallucination Rate", "0.17", "lower is better", C.amber);
  card(slide, ctx, 98, 420, 318, 132, "Evaluation cases", "Leave policy, security incident reporting, project status reports, onboarding training, and Priority 1 incident handling.", { bodySize: 15 });
  card(slide, ctx, 482, 420, 318, 132, "Comparison story", "Base LLM vs RAG only vs fine-tuned + RAG vs multi-agent + fine-tuned + RAG.", { bodySize: 15 });
  card(slide, ctx, 866, 420, 318, 132, "Interview value", "Shows that the project measures reliability instead of only displaying chatbot answers.", { bodySize: 15 });
  footer(slide, ctx, 6);
  return slide;
}
