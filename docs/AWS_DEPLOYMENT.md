# AWS deployment blueprint (not deployed)

This document describes a deployment path; it is **not evidence that AssessLens has
been deployed to AWS**. No AWS account, credentials, ECR image, ECS service, or S3
bucket is configured by this repository.

## Intended flow

1. Build the FastAPI image with the repository Dockerfile.
2. Push the image to a private Amazon ECR repository.
3. Run the image as an ECS Fargate service behind an HTTPS load balancer.
4. Keep raw recordings out of container images and logs. If object storage is
   required, use a private S3 bucket with encryption, narrow IAM permissions,
   lifecycle deletion, and access logging.
5. Store API credentials in AWS Secrets Manager, not in source code or image layers.
6. Restrict network access, configure request-size limits, and monitor request
   latency, errors, CPU, memory, and task restarts.

## Important privacy boundary

The current API processes an uploaded video in a temporary file and deletes that
file after processing. It does not upload media to S3. Adding S3 requires a separate
consent, retention, access-control, encryption, and deletion design. Do not enable
persistent recording storage by default.

## Local container smoke test

From the repository root:

```bash
docker build -t assesslens-api .
docker run --rm -p 8000:8000 assesslens-api
```

Open `http://localhost:8000/docs` and call `GET /health`. The video endpoint
requires an explicit `consent_confirmed=true` form field and a supported video file.

## Production work still required

- Authentication and authorization; the sample API is not an internet-ready service.
- HTTPS termination, rate limiting, malware scanning, and stricter upload controls.
- A documented model artifact/version strategy and a real PyTorch/ONNX detector
  implementation before claiming those backends.
- Load tests on representative hardware before reporting P95 latency or throughput.
- An approved data-processing agreement and retention policy before external storage.
