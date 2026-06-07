from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from textwrap import wrap


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "enterprise_dataset"
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"


@dataclass(frozen=True)
class DocumentSpec:
    department: str
    document_type: str
    access_level: str
    title: str
    body: str


DEPARTMENTS = {
    "hr": {
        "department": "HR",
        "document_type": "Policy",
        "access_level": "internal",
        "titles": [
            "Leave Policy",
            "Employee Handbook",
            "Remote Work Policy",
            "Code of Conduct",
            "Performance Review Policy",
            "Onboarding Guide",
            "Training Completion Policy",
            "Travel and Attendance Policy",
            "Benefits Policy",
            "Workplace Conduct SOP",
        ],
        "facts": [
            "Employees are entitled to 12 casual leaves per calendar year.",
            "Earned leave requests longer than five working days require manager approval.",
            "New employees must complete onboarding training within 14 calendar days.",
            "Remote work requests must be submitted two working days in advance.",
            "Annual performance reviews are completed during the last quarter of the year.",
        ],
    },
    "it": {
        "department": "IT",
        "document_type": "SOP",
        "access_level": "internal",
        "titles": [
            "IT Support SOP",
            "Incident Escalation SOP",
            "Laptop Provisioning Guide",
            "Password Reset Procedure",
            "Service Desk Workflow",
            "Backup Restoration SOP",
            "VPN Access Guide",
            "Software Installation Policy",
            "Asset Management SOP",
            "Change Management SOP",
        ],
        "facts": [
            "Priority 1 incidents must be acknowledged within 15 minutes.",
            "All IT support requests must be submitted through the Service Desk portal.",
            "Password reset requests require identity verification before completion.",
            "Production changes require approval from the change advisory board.",
            "Laptops must include endpoint protection, encryption, and VPN configuration.",
        ],
    },
    "security": {
        "department": "Security",
        "document_type": "Policy",
        "access_level": "restricted",
        "titles": [
            "Security Guidelines",
            "Phishing Response Policy",
            "MFA Enforcement Policy",
            "Data Classification Standard",
            "Access Review SOP",
            "Device Security Policy",
            "Confidential Data Handling",
            "Vendor Security Checklist",
            "Incident Reporting Policy",
            "USB Access Standard",
        ],
        "facts": [
            "Security incidents must be reported within 30 minutes of discovery.",
            "Multi-factor authentication is mandatory for email, VPN, and cloud systems.",
            "Confidential documents must not be shared using personal email.",
            "USB storage access requires manager approval and business justification.",
            "Access reviews are performed every quarter for privileged accounts.",
        ],
    },
    "finance": {
        "department": "Finance",
        "document_type": "Policy",
        "access_level": "internal",
        "titles": [
            "Expense Reimbursement Policy",
            "Vendor Payment SOP",
            "Invoice Approval Policy",
            "Travel Reimbursement Guide",
            "Budget Review Standard",
            "Procurement Policy",
            "Corporate Card Policy",
            "Petty Cash SOP",
            "Financial Reporting Calendar",
            "Audit Evidence Checklist",
        ],
        "facts": [
            "Expense reimbursement claims must be submitted within 30 days of expense date.",
            "Invoices above 50000 require approval from the department head.",
            "Vendor payments are processed every Friday after invoice validation.",
            "Corporate card receipts must be uploaded within five working days.",
            "Quarterly budget reviews are completed within ten working days after quarter close.",
        ],
    },
    "operations": {
        "department": "Operations",
        "document_type": "Technical Manual",
        "access_level": "internal",
        "titles": [
            "Project Documentation Standard",
            "Project Status Reporting SOP",
            "Release Readiness Checklist",
            "Meeting Notes Standard",
            "Risk Register Guide",
            "Business Continuity Plan",
            "Knowledge Base Article Standard",
            "Stakeholder Communication Plan",
            "Deployment Runbook",
            "Post Implementation Review",
        ],
        "facts": [
            "Project status reports must be submitted every Friday before 5:00 PM.",
            "Every project must maintain a charter, scope statement, risk register, and delivery plan.",
            "Release readiness must be approved before production deployment.",
            "Meeting notes must include decisions, owners, dates, and action items.",
            "Post implementation reviews are completed within seven working days after release.",
        ],
    },
}


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, str | int]] = []

    specs = build_specs()
    for index, spec in enumerate(specs, start=1):
        folder = OUTPUT_DIR / spec.department.lower().replace(" ", "_")
        folder.mkdir(parents=True, exist_ok=True)
        slug = slugify(spec.title)
        filename = f"{index:03d}_{slug}.pdf"
        path = folder / filename
        write_pdf(path, spec.title, spec.body)
        manifest.append(
            {
                "id": index,
                "filename": filename,
                "path": str(path.relative_to(ROOT)),
                "department": spec.department,
                "document_type": spec.document_type,
                "access_level": spec.access_level,
                "title": spec.title,
            }
        )

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated {len(manifest)} PDFs in {OUTPUT_DIR}")
    print(f"Manifest: {MANIFEST_PATH}")


def build_specs() -> list[DocumentSpec]:
    specs: list[DocumentSpec] = []
    for category in DEPARTMENTS.values():
        for cycle in range(2):
            for title_index, title in enumerate(category["titles"], start=1):
                version = cycle + 1
                facts = rotate(category["facts"], title_index + cycle)
                full_title = f"Enterprise {title} V{version}"
                body = render_body(
                    title=full_title,
                    department=category["department"],
                    document_type=category["document_type"],
                    access_level=category["access_level"],
                    facts=facts,
                    version=version,
                )
                specs.append(
                    DocumentSpec(
                        department=category["department"],
                        document_type=category["document_type"],
                        access_level=category["access_level"],
                        title=full_title,
                        body=body,
                    )
                )

    return specs


def render_body(
    title: str,
    department: str,
    document_type: str,
    access_level: str,
    facts: list[str],
    version: int,
) -> str:
    return "\n".join(
        [
            title,
            "",
            f"Department: {department}",
            f"Document Type: {document_type}",
            f"Access Level: {access_level}",
            f"Version: {version}.0",
            "",
            "Purpose",
            (
                f"This document defines operational guidance for the {department} department. "
                "It is written for employees, managers, auditors, and support teams who need "
                "clear enterprise procedures."
            ),
            "",
            "Policy Details",
            *facts,
            "",
            "Responsibilities",
            (
                "Employees must follow the procedure, managers must review exceptions, and "
                "department owners must keep this document current. Exceptions require written "
                "approval and must be recorded for audit review."
            ),
            "",
            "Review Cycle",
            (
                "This document is reviewed annually or when a business process, compliance "
                "requirement, security requirement, or technology platform changes."
            ),
        ]
    )


def write_pdf(path: Path, title: str, text: str) -> None:
    lines = []
    for raw_line in text.splitlines():
        if not raw_line:
            lines.append("")
            continue
        lines.extend(wrap(raw_line, width=88))

    pages = [lines[index : index + 42] for index in range(0, len(lines), 42)]
    objects: list[bytes] = []

    def add_object(data: bytes) -> int:
        objects.append(data)
        return len(objects)

    pages_id = add_object(b"<< /Type /Pages /Kids [] /Count 0 >>")
    font_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    page_ids = []

    for page_lines in pages:
        content = build_page_stream(title, page_lines)
        content_id = add_object(
            b"<< /Length "
            + str(len(content)).encode("ascii")
            + b" >>\nstream\n"
            + content
            + b"\nendstream"
        )
        page_id = add_object(
            (
                f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 612 792] "
                f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
                f"/Contents {content_id} 0 R >>"
            ).encode("ascii")
        )
        page_ids.append(page_id)

    objects[pages_id - 1] = (
        f"<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_ids)}] "
        f"/Count {len(page_ids)} >>"
    ).encode("ascii")
    catalog_id = add_object(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("ascii"))

    output = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_id, data in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{object_id} 0 obj\n".encode("ascii"))
        output.extend(data)
        output.extend(b"\nendobj\n")

    xref_start = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    output.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        ).encode("ascii")
    )
    path.write_bytes(output)


def build_page_stream(title: str, lines: list[str]) -> bytes:
    commands = ["BT", "/F1 16 Tf", "50 742 Td", f"({escape_pdf_text(title)}) Tj"]
    commands.extend(["/F1 10 Tf", "0 -28 Td"])
    for line in lines:
        if line:
            commands.append(f"({escape_pdf_text(line)}) Tj")
        commands.append("0 -14 Td")
    commands.append("ET")
    return "\n".join(commands).encode("ascii")


def escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def rotate(items: list[str], offset: int) -> list[str]:
    offset = offset % len(items)
    return items[offset:] + items[:offset]


def slugify(value: str) -> str:
    return "".join(character.lower() if character.isalnum() else "_" for character in value).strip("_")


if __name__ == "__main__":
    main()
