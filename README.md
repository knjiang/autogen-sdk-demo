## AutoGen Demo Bot with OpenTelemetry (Braintrust OTLP)

A minimal AutoGen AgentChat demo with OpenTelemetry tracing exported via OTLP gRPC. Point the OTLP endpoint to your Braintrust-compatible collector.

### Docs
- AutoGen Home: [link](https://microsoft.github.io/autogen/stable//index.html)
- Tracing Guide: [link](https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/tracing.html)

### Setup
```bash
cd /Users/kenjiang/Development/autogen-sdk-demo
python3 -m venv .venv
./.venv/bin/pip install -U pip
./.venv/bin/pip install -r requirements.txt
cp .env.example .env
# set OPENAI_API_KEY and adjust OTEL_* for your Braintrust collector
```

### Run
```bash
./.venv/bin/python -m src.demo_bot
```

### Configuration
- `OTEL_EXPORTER_OTLP_ENDPOINT`: Your Braintrust OTLP gRPC collector, e.g., `http://localhost:4317` or your remote URL.
- `OTEL_SERVICE_NAME`: Service name for tracing. Default is `autogen-demo-bot`.

Traces include agent runtime spans and instrumented OpenAI calls.
