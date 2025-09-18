## AutoGen Demo Bot with OpenTelemetry (Braintrust)

A minimal AutoGen AgentChat demo with OpenTelemetry using Braintrust's span processor. Spans are sent to Braintrust and also printed to the console for easy inspection.

### Docs
- AutoGen Home: [link](https://microsoft.github.io/autogen/stable//index.html)
- Tracing Guide: [link](https://microsoft.github.io/autogen/stable//user-guide/agentchat-user-guide/tracing.html)

### Setup
```bash
cd /Users/kenjiang/Development/autogen-sdk-demo
python3 -m venv .venv
./.venv/bin/pip install -U pip
./.venv/bin/pip install -r requirements.txt
cp .env.example .env  # optional
# Set required env vars (at minimum):
#   OPENAI_API_KEY=...
#   OTEL_SERVICE_NAME=autogen-demo-bot  # optional
# Braintrust SDK should be configured per your account (e.g., API key/project)
```

### Run
```bash
./.venv/bin/python -m src.demo_bot
```

### Notes
- Tracing is initialized in `src/demo_bot.py` with:
  - `TracerProvider(resource={"service.name": OTEL_SERVICE_NAME or autogen-demo-bot})`
  - `BraintrustSpanProcessor(filter_ai_spans=True)` for Braintrust export
  - `SimpleSpanProcessor(ConsoleSpanExporter())` to print spans locally
- No OTLP/Jaeger is used in this setup. If you prefer OTLP, switch back to an OTLP exporter and set appropriate env vars.
