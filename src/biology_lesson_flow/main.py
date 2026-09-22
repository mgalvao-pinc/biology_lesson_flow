import json
import logging
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

from biology_lesson_flow.crews.content_crew.content_crew import BiologyLessonCrew


def sanitize_filename(value: str) -> str:
    """Converte o tema em um nome de arquivo seguro para Windows e Linux."""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    safe_value = re.sub(r"[^A-Za-z0-9]+", "_", ascii_value).strip("_")
    return safe_value or "biologia"


def timestamp_for_filename() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def ensure_session_log(topic: str) -> tuple[logging.Logger, Path]:
    log_dir = Path.cwd() / "logs"
    log_dir.mkdir(exist_ok=True)
    file_name = f"session_{timestamp_for_filename()}_{sanitize_filename(topic)}.log"
    logger = logging.getLogger(f"biology_lesson_flow_{sanitize_filename(topic)}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    handler = logging.FileHandler(log_dir / file_name, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    logger.info("Sessão iniciada para o tema: %s", topic)
    return logger, log_dir / file_name


def _as_dict(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if hasattr(value, "dict"):
        return value.dict()
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return {}


def _extract_task_payload(result: Any, key_name: str) -> dict[str, Any]:
    tasks = getattr(result, "tasks_output", []) or []
    for task in tasks:
        payload = _as_dict(getattr(task, "pydantic", None))
        if isinstance(payload, dict) and key_name in payload:
            return payload
        raw = getattr(task, "raw", None)
        if isinstance(raw, dict) and key_name in raw:
            return raw
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
            except Exception:
                continue
            if isinstance(parsed, dict) and key_name in parsed:
                return parsed

    if isinstance(result, dict) and key_name in result:
        return result

    raw = getattr(result, "raw", None)
    if isinstance(raw, dict) and key_name in raw:
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except Exception:
            return {}
        if isinstance(parsed, dict) and key_name in parsed:
            return parsed
    return {}


def render_markdown_aula(topic: str, lesson_data: dict[str, Any], review_data: dict[str, Any]) -> str:
    title = f"# Aula de Biologia: {topic}"
    intro = lesson_data.get("introduction", "")
    sections = lesson_data.get("sections", [])
    summary = lesson_data.get("summary", "")
    questions = lesson_data.get("questions", [])

    lines = [title, "", "## Introdução", "", intro.strip(), ""]

    lines.append("## Conteúdo")
    for index, section in enumerate(sections, start=1):
        title_section = section.get("title", f"Seção {index}")
        content = section.get("content", "")
        examples = section.get("examples", [])
        lines.extend(["", f"### {index}. {title_section}", "", content.strip(), ""])
        if examples:
            lines.append("**Exemplos:**")
            for example in examples:
                lines.append(f"- {example}")
            lines.append("")

    lines.extend(["## Resumo", "", summary.strip(), "", "## Questões e respostas", ""])
    if questions:
        for idx, question in enumerate(questions, start=1):
            q_text = question.get("question", "Pergunta")
            q_type = question.get("type", "")
            answer = question.get("expected_answer", "")
            lines.extend([
                f"### {idx}. {q_text}",
                "",
                f"- Tipo: {q_type}",
                f"- Resposta esperada: {answer}",
                "",
            ])
    else:
        lines.append("Nenhuma questão foi gerada para esta aula.")

    lines.extend(["", "## Revisão final", ""])
    if review_data:
        approved = review_data.get("overall_approved")
        feedback = review_data.get("feedback", "")
        lines.append(f"- Status geral: {'Aprovada' if approved else 'Revisar'}")
        lines.append("")
        lines.append(feedback.strip())
    else:
        lines.append("Sem dados de revisão disponíveis.")

    return "\n".join(lines).strip() + "\n"


def save_markdown_output(topic: str, result: Any) -> Path:
    lesson_data = _extract_task_payload(result, "sections")
    review_data = _extract_task_payload(result, "overall_approved")

    if not lesson_data:
        lesson_data = _extract_task_payload(result, "introduction")

    if not review_data:
        review_data = _extract_task_payload(result, "feedback")

    if not lesson_data:
        lesson_data = {}
    if not review_data:
        review_data = {}

    markdown_content = render_markdown_aula(topic, lesson_data, review_data)
    timestamp = timestamp_for_filename()
    file_name = f"aula_{sanitize_filename(topic)}_{timestamp}.md"
    path = Path.cwd() / file_name
    path.write_text(markdown_content, encoding="utf-8")
    return path


class BiologyLessonState(BaseModel):
    topic: str = ""


class BiologyLessonFlow(Flow[BiologyLessonState]):

    @start()
    def iniciar(self):
        print("\n" + "=" * 60)
        print("🔬 INICIANDO FLOW DE AULA DE BIOLOGIA")
        print(f"📚 Tema: {self.state.topic}")
        print("=" * 60 + "\n")

    @listen(iniciar)
    def executar_crew(self):
        logger, log_path = ensure_session_log(self.state.topic)
        print("🚀 Iniciando os 3 agentes...\n")
        logger.info("Iniciando execução do crew")

        try:
            resultado = BiologyLessonCrew().crew().kickoff(inputs={"topic": self.state.topic})
            markdown_path = save_markdown_output(self.state.topic, resultado)
            markdown_content = markdown_path.read_text(encoding="utf-8")
            logger.info("Arquivo Markdown gerado em: %s", markdown_path)
            logger.info("Sessão concluída com sucesso")
        except Exception:
            logger.exception("Erro durante a execução da sessão")
            raise

        print("\n" + "=" * 60)
        print("✅ FLOW CONCLUÍDO COM SUCESSO!")
        print(f"📄 Aula salva em: {markdown_path.name}")
        print(f"📝 Log da sessão: {log_path.name}")
        print("=" * 60)

        return markdown_content


def kickoff(topic: str | None = None):
    if topic is None:
        topic = input("\nDigite o tema de Biologia: ").strip()
    if not topic:
        topic = "Fotossíntese"
        print(f"Nenhum tema informado. Usando padrão: '{topic}'")

    flow = BiologyLessonFlow()
    flow.kickoff(inputs={"topic": topic})


def run_with_trigger():
    """Compatibilidade com o entrypoint registrado no pyproject."""
    kickoff()


def plot():
    flow = BiologyLessonFlow()
    flow.plot()