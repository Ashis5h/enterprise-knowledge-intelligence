from __future__ import annotations

import argparse
import json
import mimetypes
import time
from pathlib import Path
from urllib import error, request


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "enterprise_dataset" / "manifest.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Upload generated enterprise PDFs to the backend.")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend base URL.")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of PDFs to upload.")
    parser.add_argument("--start", type=int, default=1, help="1-based manifest row to start from.")
    parser.add_argument("--retries", type=int, default=3, help="Retries per PDF.")
    parser.add_argument("--timeout", type=int, default=120, help="Upload timeout in seconds.")
    parser.add_argument("--email", default="atul@enterprise.ai", help="Login email.")
    parser.add_argument("--password", default="atul123", help="Login password.")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    start_index = max(0, args.start - 1)
    selected = manifest[start_index : start_index + args.limit]
    token = login(args.base_url, args.email, args.password, args.timeout)

    for index, item in enumerate(selected, start=1):
        path = ROOT / item["path"]
        upload_with_retries(
            attempts=args.retries,
            timeout=args.timeout,
            token=token,
            base_url=args.base_url,
            path=path,
            department=item["department"],
            document_type=item["document_type"],
            access_level=item["access_level"],
        )
        manifest_number = start_index + index
        print(f"[{manifest_number}/{len(manifest)}] uploaded {path.name}")


def upload_with_retries(
    attempts: int,
    timeout: int,
    token: str,
    base_url: str,
    path: Path,
    department: str,
    document_type: str,
    access_level: str,
) -> None:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            upload_document(
                base_url=base_url,
                path=path,
                department=department,
                document_type=document_type,
                access_level=access_level,
                timeout=timeout,
                token=token,
            )
            return
        except (TimeoutError, error.URLError, error.HTTPError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(2 * attempt)

    raise RuntimeError(f"Upload failed for {path} after {attempts} attempts: {last_error}")


def upload_document(
    base_url: str,
    path: Path,
    department: str,
    document_type: str,
    access_level: str,
    timeout: int,
    token: str,
) -> None:
    boundary = "----EnterpriseKnowledgeBoundary"
    fields = {
        "department": department,
        "document_type": document_type,
        "access_level": access_level,
    }
    body = bytearray()

    for name, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.extend(f"{value}\r\n".encode("utf-8"))

    content_type = mimetypes.guess_type(path.name)[0] or "application/pdf"
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(
        (
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8")
    )
    body.extend(path.read_bytes())
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    upload_request = request.Request(
        f"{base_url.rstrip('/')}/api/documents/upload",
        data=bytes(body),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    with request.urlopen(upload_request, timeout=timeout) as response:
        if response.status >= 400:
            raise RuntimeError(f"Upload failed for {path}: HTTP {response.status}")


def login(base_url: str, email: str, password: str, timeout: int) -> str:
    payload = json.dumps({"email": email, "password": password}).encode("utf-8")
    login_request = request.Request(
        f"{base_url.rstrip('/')}/api/auth/login",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(login_request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
        return str(body["access_token"])


if __name__ == "__main__":
    main()
