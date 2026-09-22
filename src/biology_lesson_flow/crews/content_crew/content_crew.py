from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from biology_lesson_flow.models import BiologyLesson, ReviewResult
from biology_lesson_flow.custom_tools import LessonStructureTool, ReviewCheckerTool


@CrewBase
class BiologyLessonCrew():
    """Biology Lesson Crew — 3 agentes sequenciais"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        self.llm = LLM(
            model="gemini-3.1-flash-lite",
        )

    # ─── AGENTES ─────────────────────────────────────────────────────────

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            tools=[SerperDevTool()],
            llm=self.llm,
            verbose=True,
            max_iter=5,
        )

    @agent
    def lesson_builder(self) -> Agent:
        return Agent(
            config=self.agents_config['lesson_builder'],
            tools=[LessonStructureTool()],
            llm=self.llm,
            verbose=True,
            max_iter=5,
        )

    @agent
    def reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['reviewer'],
            tools=[ReviewCheckerTool()],
            llm=self.llm,
            verbose=True,
            max_iter=5,
        )

    # ─── TASKS ───────────────────────────────────────────────────────────

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
        )

    @task
    def lesson_task(self) -> Task:
        return Task(
            config=self.tasks_config['lesson_task'],
            output_pydantic=BiologyLesson,
        )

    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_task'],
            output_pydantic=ReviewResult,
        )

    # ─── CREW ────────────────────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )