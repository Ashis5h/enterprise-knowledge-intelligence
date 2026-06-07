import { C, slideShell, header, flowBox, arrow, card, footer } from "./common.mjs";

export async function slide07(presentation, ctx) {
  const slide = slideShell(presentation, ctx);
  header(slide, ctx, "Fine-Tuning", "QLoRA path for domain adaptation", "The project already generates instruction-response examples from enterprise content and includes a training scaffold for Qwen/Llama-style fine-tuning.");
  flowBox(slide, ctx, 96, 246, 166, 82, "Enterprise Docs", "100 PDFs + uploads", C.white);
  arrow(slide, ctx, 278, 268, 38);
  flowBox(slide, ctx, 332, 246, 178, 82, "JSONL Dataset", "instruction + output", C.paleBlue);
  arrow(slide, ctx, 526, 268, 38);
  flowBox(slide, ctx, 580, 246, 166, 82, "Base LLM", "Qwen / Llama", C.white);
  arrow(slide, ctx, 762, 268, 38);
  flowBox(slide, ctx, 816, 246, 166, 82, "QLoRA", "Unsloth + PEFT", C.lightBlue);
  arrow(slide, ctx, 998, 268, 38);
  flowBox(slide, ctx, 1052, 246, 150, 82, "Adapter", "domain style", C.white);
  card(slide, ctx, 120, 430, 300, 116, "Dataset examples", "Summaries, key requirements, business purpose explanations, and policy Q&A pairs.", { bodySize: 15 });
  card(slide, ctx, 490, 430, 300, 116, "Why QLoRA", "Trains small adapter weights instead of full model weights, reducing GPU memory cost.", { bodySize: 15 });
  card(slide, ctx, 860, 430, 300, 116, "Demo boundary", "The code path is ready; actual training needs a GPU environment such as T4, A100, or Colab.", { bodySize: 15 });
  footer(slide, ctx, 7);
  return slide;
}
