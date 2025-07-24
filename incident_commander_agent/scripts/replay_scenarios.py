import argparse, yaml
from agent.memory.semantic_vector import VectorIndex
from agent.tools.mcp_server import MCPServer
from agent.pipeline.plan import generate_plan
from agent.pipeline.execute import execute
from agent.pipeline.reflect import reflect_and_improve

def load_text(path: str) -> str:
    with open(path, "r") as f:
        return f.read()

def load_yaml(path: str):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()

    scenario = load_yaml(args.scenario)
    incident = scenario["incident"]

    system_prompt = load_text("agent/prompts/system.md")
    planner_prompt = load_text("agent/prompts/planner.md")
    executor_prompt = load_text("agent/prompts/executor.md")
    critic_prompt = load_text("agent/prompts/critic.md")

    vector = VectorIndex()
    server = MCPServer(vector)

    plan = generate_plan(incident, system_prompt, planner_prompt)
    exec_res = execute(plan.raw_text, system_prompt, executor_prompt, server, retrieved_docs=None)
    critique, improved = reflect_and_improve(system_prompt, critic_prompt, exec_res.final_output)

    print("=== PLAN ===")
    print(plan.raw_text)
    print("\n=== DRAFT ===")
    print(exec_res.final_output)
    print("\n=== CRITIQUE ===")
    print(critique)
    print("\n=== FINAL ===")
    print(improved)

if __name__ == "__main__":
    main()
