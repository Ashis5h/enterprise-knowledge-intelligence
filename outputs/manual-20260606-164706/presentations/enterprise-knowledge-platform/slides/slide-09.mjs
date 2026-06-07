import { C, slideShell, header, flowBox, arrow, card, footer } from "./common.mjs";

export async function slide09(presentation, ctx) {
  const slide = slideShell(presentation, ctx);
  header(slide, ctx, "Deployment", "Docker today, AWS-ready architecture", "Docker Compose packages the frontend, backend, and database locally. The same service split maps cleanly to AWS deployment.");
  flowBox(slide, ctx, 92, 246, 170, 86, "React + Nginx", "frontend container", C.white);
  arrow(slide, ctx, 278, 270, 44);
  flowBox(slide, ctx, 338, 246, 170, 86, "FastAPI", "backend container", C.lightBlue);
  arrow(slide, ctx, 524, 270, 44);
  flowBox(slide, ctx, 584, 246, 170, 86, "PostgreSQL", "database service", C.white);
  arrow(slide, ctx, 770, 270, 44);
  flowBox(slide, ctx, 830, 246, 170, 86, "Vector DB", "local / Pinecone", C.paleBlue);
  arrow(slide, ctx, 1016, 270, 44);
  flowBox(slide, ctx, 1076, 246, 120, 86, "AWS", "cloud target", C.white);
  card(slide, ctx, 112, 424, 292, 124, "Local command", "docker compose up --build\n\nRuns the application stack for demo and testing.", { bodySize: 15 });
  card(slide, ctx, 494, 424, 292, 124, "AWS mapping", "EC2 or ECS for containers, RDS for Postgres, S3 for files, CloudWatch for logs.", { bodySize: 15 });
  card(slide, ctx, 876, 424, 292, 124, "Pinecone option", "Switch VECTOR_DB_PROVIDER=pinecone and provide API key/index settings.", { bodySize: 15 });
  footer(slide, ctx, 9);
  return slide;
}
