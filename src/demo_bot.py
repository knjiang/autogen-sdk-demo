import os
import asyncio
from typing import Optional

from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_core import SingleThreadedAgentRuntime
from autogen_ext.models.openai import OpenAIChatCompletionClient

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from braintrust.otel import BraintrustSpanProcessor
from opentelemetry.instrumentation.openai import OpenAIInstrumentor


def setup_tracing() -> None:
    service_name = os.getenv("OTEL_SERVICE_NAME", "autogen-demo-bot")
    provider = TracerProvider(resource=Resource({"service.name": service_name}))
    provider.add_span_processor(BraintrustSpanProcessor(filter_ai_spans=True))
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    OpenAIInstrumentor().instrument()



def search_web_tool(query: str) -> str:
    if "2006-2007" in query:
        return (
            "Here are the total points scored by Miami Heat players in the 2006-2007 season:\n"
            "Udonis Haslem: 844 points\n"
            "Dwayne Wade: 1397 points\n"
            "James Posey: 550 points\n"
            "...\n"
        )
    elif "2007-2008" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2007-2008 is 214."
    elif "2008-2009" in query:
        return "The number of total rebounds for Dwayne Wade in the Miami Heat season 2008-2009 is 398."
    return "No data found."


def percentage_change_tool(start: float, end: float) -> float:
    return ((end - start) / start) * 100


async def main(task: Optional[str] = None) -> None:
    load_dotenv()
    setup_tracing()

    model_client = OpenAIChatCompletionClient(model="gpt-4o")

    tracer = trace.get_tracer("autogen-demo-bot")
    with tracer.start_as_current_span("run_team"):
        planning_agent = AssistantAgent(
            "PlanningAgent",
            description="Plans tasks and delegates.",
            model_client=model_client,
            system_message=(
                "You are a planning agent. You only plan and delegate tasks; do not execute them.\n"
                "When assigning tasks, use this format: 1. <agent> : <task>\n"
                "After all tasks are complete, summarize the findings and end with \"TERMINATE\"."
            ),
        )

        web_search_agent = AssistantAgent(
            "WebSearchAgent",
            description="Searches information using tools.",
            tools=[search_web_tool],
            model_client=model_client,
            system_message=(
                "You are a web search agent. Your only tool is search_web_tool - use it to find information.\n"
                "You make only one search call at a time. Once you have the results, you never do calculations."
            ),
        )

        data_analyst_agent = AssistantAgent(
            "DataAnalystAgent",
            description="Performs calculations.",
            model_client=model_client,
            tools=[percentage_change_tool],
            system_message=(
                "You are a data analyst. Use the tools provided to compute numeric results."
            ),
        )

        termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(max_messages=25)

        if not task:
            task = (
                "Who was the Miami Heat player with the highest points in the 2006-2007 season, "
                "and what was the percentage change in his total rebounds between the 2007-2008 and 2008-2009 seasons?"
            )

        runtime = SingleThreadedAgentRuntime(tracer_provider=trace.get_tracer_provider())
        runtime.start()

        selector_prompt = (
            "Select an agent to perform task.\n\n{roles}\n\nCurrent conversation context:\n{history}\n\n"
            "Read the above conversation, then select an agent from {participants} to perform the next task.\n"
            "Make sure the planner agent has assigned tasks before other agents start working.\nOnly select one agent."
        )

        team = SelectorGroupChat(
            [planning_agent, web_search_agent, data_analyst_agent],
            model_client=model_client,
            termination_condition=termination,
            selector_prompt=selector_prompt,
            allow_repeated_speaker=True,
            runtime=runtime,
        )

        await Console(team.run_stream(task=task))

        await runtime.stop()
        
    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
