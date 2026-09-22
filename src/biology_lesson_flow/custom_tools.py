from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type


# ─── Tool do Agente 2: Professor ────────────────────────────────────────────

class LessonStructureInput(BaseModel):
    lesson_content: str = Field(
        description="Conteúdo da aula para validar a estrutura"
    )


class LessonStructureTool(BaseTool):
    name: str = "lesson_structure_validator"
    description: str = (
        "Valida se a aula de Biologia possui todos os blocos obrigatórios: "
        "introdução, seções de conteúdo com exemplos, resumo e questões. "
        "Use esta ferramenta antes de finalizar a aula."
    )
    args_schema: Type[BaseModel] = LessonStructureInput

    def _run(self, lesson_content: str) -> str:
        content_lower = lesson_content.lower()
        checks = []

        required_blocks = {
            "introdução": ["introdução", "introducao", "introdução:"],
            "seções de conteúdo": ["##", "seção", "secao", "parte ", "capítulo"],
            "exemplos": ["exemplo", "por exemplo", "como ", "ilustra"],
            "resumo": ["resumo", "conclusão", "conclusao", "em resumo"],
            "questões": ["questão", "questao", "pergunta", "exercício", "1.", "1)"],
        }

        for block, keywords in required_blocks.items():
            found = any(kw in content_lower for kw in keywords)
            if found:
                checks.append(f"✅ '{block}' encontrado")
            else:
                checks.append(f"❌ '{block}' AUSENTE — adicione antes de finalizar")

        # Conta questões
        import re
        question_count = len(re.findall(r'\d+[\.\)]\s', lesson_content))
        if question_count >= 5:
            checks.append(f"✅ {question_count} questões encontradas (mínimo 5 ✓)")
        else:
            checks.append(f"❌ Apenas {question_count} questões — adicione mais (mínimo 5)")

        resultado = "\n".join(checks)
        aprovada = all("✅" in c for c in checks)

        return (
            f"VALIDAÇÃO DE ESTRUTURA:\n{resultado}\n\n"
            f"STATUS: {'✅ ESTRUTURA COMPLETA' if aprovada else '❌ ESTRUTURA INCOMPLETA — ajuste os itens marcados'}"
        )


# ─── Tool do Agente 3: Revisor ───────────────────────────────────────────────

class ReviewCheckerInput(BaseModel):
    lesson_content: str = Field(
        description="A aula completa para ser revisada"
    )


class ReviewCheckerTool(BaseTool):
    name: str = "review_checker"
    description: str = (
        "Executa um checklist estruturado de revisão pedagógica sobre a aula de Biologia. "
        "Avalia precisão científica, coerência, ordem lógica e validade das questões. "
        "Use esta ferramenta para guiar sua revisão."
    )
    args_schema: Type[BaseModel] = ReviewCheckerInput

    def _run(self, lesson_content: str) -> str:
        checklist = [
            ("Precisão Científica",
             "As informações e terminologias científicas estão corretas e atualizadas?"),
            ("Coerência Didática",
             "A aula faz sentido como um todo? O tema central é mantido do início ao fim?"),
            ("Progressão Lógica",
             "O conteúdo parte do básico para o complexo de forma adequada?"),
            ("Qualidade dos Exemplos",
             "Os exemplos são relevantes, claros e adequados ao nível dos alunos?"),
            ("Completude do Resumo",
             "O resumo cobre os pontos essenciais apresentados na aula?"),
            ("Validade das Questões",
             "Todas as questões podem ser respondidas com base no conteúdo da aula?"),
            ("Diversidade das Questões",
             "Há questões de diferentes níveis de dificuldade (fácil, médio, difícil)?"),
            ("Linguagem Adequada",
             "A linguagem é adequada para estudantes do ensino médio/fundamental?"),
        ]

        output = "CHECKLIST DE REVISÃO PEDAGÓGICA:\n\n"
        for i, (criterio, descricao) in enumerate(checklist, 1):
            output += f"{i}. {criterio}\n   → {descricao}\n\n"

        output += (
            "INSTRUÇÕES: Avalie cada critério acima para a aula fornecida. "
            "Para cada um, indique se está ✅ aprovado, ⚠️ parcialmente adequado ou ❌ reprovado. "
            "Forneça justificativa específica e ao final emita um VEREDITO GERAL: "
            "APROVADA / APROVADA COM RESSALVAS / REPROVADA."
        )

        return output