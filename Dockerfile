# Stage 1: Build stage
FROM python:3.10 AS builder

WORKDIR /sentinel

COPY . /sentinel

RUN python3 -m venv .venv
ENV PATH="/sentinel/.venv/bin:$PATH"
RUN pip install --upgrade pip && pip install -r requirements.txt

# Stage 2: Run stage
FROM python:3.10-slim

ENV PORT=8000

WORKDIR /sentinel

COPY --from=builder /sentinel /sentinel
COPY --from=builder /sentinel/.venv /sentinel/.venv

ENV PATH="/sentinel/.venv/bin:$PATH"

EXPOSE ${PORT}
CMD ["python", "server.py"]

