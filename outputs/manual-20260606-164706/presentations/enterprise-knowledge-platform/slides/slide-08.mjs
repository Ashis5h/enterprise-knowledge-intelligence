import { C, slideShell, header, card, metric, footer } from "./common.mjs";

export async function slide08(presentation, ctx) {
  const slide = slideShell(presentation, ctx);
  header(slide, ctx, "Security and Governance", "Enterprise controls built into the demo", "The implementation includes JWT authentication, role-aware frontend navigation, document metadata, and source traceability.");
  metric(slide, ctx, 82, 238, 230, "Demo User", "Atul", "admin account", C.blue);
  metric(slide, ctx, 350, 238, 230, "Auth", "JWT", "protected APIs", C.green);
  metric(slide, ctx, 618, 238, 230, "Metadata", "3 fields", "dept/type/access", C.blue);
  metric(slide, ctx, 886, 238, 230, "Sources", "chunk IDs", "traceable answers", C.green);
  card(slide, ctx, 126, 430, 286, 120, "Access model", "Chat, documents, analytics, fine-tuning, and admin routes require a bearer token.", { bodySize: 15 });
  card(slide, ctx, 496, 430, 286, 120, "Document governance", "Uploads carry department, document type, and access level metadata into retrieval results.", { bodySize: 15 });
  card(slide, ctx, 866, 430, 286, 120, "Production next", "Replace demo auth with SSO, RBAC policies, audit logs, and document-level permissions.", { bodySize: 15 });
  footer(slide, ctx, 8);
  return slide;
}
