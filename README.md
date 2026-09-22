# Biology Lesson Flow

Projeto em CrewAI para gerar aulas de Biologia completas a partir de um tema informado pelo usuário. O fluxo usa três agentes especializados em pesquisa, construção didática e revisão pedagógica para criar uma aula estruturada, com questões e respostas, e salvar o resultado em um arquivo Markdown pronto para uso.

## O que o projeto faz

- Pesquisa o tema solicitado
- Produz uma aula de Biologia com introdução, seções, resumo e exercícios
- Cria questões com respostas esperadas
- Revê a aula pedagogicamente
- Salva o resultado em Markdown
- Guarda o log da sessão em pasta dedicada `logs/`
- Inclui data e horário no nome do arquivo gerado

## Estrutura do projeto

```text
biology_lesson_flow/
├── logs/                         # registros das sessões executadas
├── src/
│   └── biology_lesson_flow/
│       ├── crews/
│       │   └── content_crew/
│       │       ├── config/
│       │       └── content_crew.py
│       ├── custom_tools.py
│       ├── main.py
│       ├── models.py
│       └── __init__.py
├── tests/
├── README.md
├── pyproject.toml
└── aula_*.md
```

## Requisitos

- Python >= 3.10 e < 3.14
- uv instalado
- chave de API configurada no ambiente (por exemplo, Gemini/OpenAI)

## Instalação

```bash
cd biology_lesson_flow
uv sync
```

Se a chave de API ainda não estiver configurada, defina-a no ambiente ou em um arquivo `.env` do projeto:

```bash
export GOOGLE_API_KEY=sua_chave
# ou
export OPENAI_API_KEY=sua_chave
```

## Como executar

### Modo interativo

```bash
uv run kickoff
```

ou

```bash
uv run run_with_trigger
```

O programa pedirá o tema da aula e, em seguida, gerará um arquivo Markdown no diretório raiz, por exemplo:

```text
aula_Fotossintese_2026-09-22_14-30-00.md
```

### Saída final

O arquivo gerado contém:

- introdução da aula
- seções de conteúdo
- exemplos práticos
- resumo final
- questões e respostas esperadas
- avaliação final do revisor

## Preparação para CrewAI AMP

O projeto já está configurado como Flow no `pyproject.toml`, possui `uv.lock` e tem um `project_id` para o AMP. O Flow recebe `topic` como entrada e retorna o Markdown da aula; o arquivo local continua sendo salvo para execuções locais.

Antes do deploy, configure no AMP as variáveis usadas pelos agentes e ferramentas:

```text
GOOGLE_API_KEY=...
SERPER_API_KEY=...
```

Com o repositório publicado no GitHub, os comandos a executar são:

```bash
uv sync
crewai login
crewai deploy create
crewai deploy status
```

Para validar localmente o mesmo tipo de entrada sem interação:

```bash
uv run python -c "from biology_lesson_flow.main import BiologyLessonFlow; print(BiologyLessonFlow().kickoff(inputs={'topic': 'Poríferos'}))"
```

Não é necessário executar `crewai login` ou qualquer comando de deploy durante o desenvolvimento. Nunca versionar o arquivo `.env`, chaves de API, logs ou aulas geradas.

## Logs

Cada execução cria um registro em `logs/`, com nome no formato:

```text
logs/session_2026-09-22_14-30-00_Fotossintese.log
```

Isso facilita a auditoria de cada sessão e o diagnóstico de problemas.

## Execução de testes

```bash
uv run python -m unittest tests.test_main_entrypoints -q
```

## Observações

- O arquivo final é gerado em Markdown para leitura mais clara do que um TXT bruto.
- O nome do arquivo inclui data e hora para evitar sobrescritas.
- O projeto é orientado a fluxo de trabalho multiagente com CrewAI.
