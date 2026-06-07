import { C, slideShell, header, flowBox, arrow, card, footer } from "./common.mjs";

export async function slide04(presentation, ctx) {
  const slide = slideShell(presentation, ctx);
  header(slide, ctx, "RAG Pipeline", "Document ingestion to grounded response", "The pipeline accepts enterprise files, extracts text, chunks content, embeds chunks, stores metadata, and retrieves trusted source context at query time.");
  const y = 248;
  flowBox(slide, ctx, 72, y, 132, 82, "PDF / DOCX", "enterprise files", C.white);
  arrow(slide, ctx, 214, y + 22, 34);
  flowBox(slide, ctx, 262, y, 142, 82, "Extraction", "PyPDF + parsers", C.paleBlue);
  arrow(slide, ctx, 414, y + 22, 34);
  flowBox(slide, ctx, 462, y, 130, 82, "Chunking", "retrievable blocks", C.white);
  arrow(slide, ctx, 602, y + 22, 34);
  flowBox(slide, ctx, 650, y, 142, 82, "Embedding", "vector features", C.paleBlue);
  arrow(slide, ctx, 802, y + 22, 34);
  flowBox(slide, ctx, 850, y, 150, 82, "Vector DB", "Pinecone-ready", C.white);
  arrow(slide, ctx, 1010, y + 22, 34);
  flowBox(slide, ctx, 1058, y, 150, 82, "Answer", "cited output", C.lightBlue);
  card(slide, ctx, 96, 424, 300, 126, "Metadata captured", "department, document_type, access_level, source path, chunk ID, confidence", { bodySize: 15 });
  card(slide, ctx, 490, 424, 300, 126, "Retrieval controls", "top-k search, fallback local provider, deduped sources, grounded status", { bodySize: 15 });
  card(slide, ctx, 884, 424, 300, 126, "Demo dataset", "100 realistic enterprise PDFs across HR, IT, Security, Finance, and Operations", { bodySize: 15 });
  footer(slide, ctx, 4);
  return slide;
}
