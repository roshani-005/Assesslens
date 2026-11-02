# AWS deployment blueprint (not deployed)

This document is an implementation plan, not evidence of an AWS deployment. This repository does not contain AWS account configuration, ECR images, ECS services, or S3 buckets.

## Proposed service flow

1. Build the FastAPI Docker image locally.
2. Push the image to a private Amazon ECR repository.
3. Run the container as an ECS Fargate service behind an HTTPS load balancer.
4. Store secrets in AWS Secrets Manager and grant the task only the IAM permissions it needs.
5. Monitor request count, errors, processing duration, CPU, memory, and task restarts.

## Recording storage and privacy

The current API writes an upload to a temporary local file and deletes it after processing. It does not upload recordings to S3. If S3 storage is added, it needs a separate user-consent and retention design, private buckets, encryption, least-privilege IAM, lifecycle deletion, and access logging. Do not make persistent recording storage the default.

## Production hardening still required

- Authentication and authorization; the sample API is not internet-ready.
- HTTPS termination, rate limiting, malware scanning, and request-size controls at the edge.
- Secure secret management and restricted network access.
- Documented model artifacts and versions.
- Load tests on representative hardware before reporting P95 latency or throughput.
- Privacy review and approved data-processing/retention terms before external storage.

## Local container smoke test

~~~bash
docker build -t assesslens-api .
docker run --rm -p 8000:8000 assesslens-api
~~~

Open http://localhost:8000/docs and call GET /health. The video endpoint requires consent_confirmed=true as a multipart form field.
