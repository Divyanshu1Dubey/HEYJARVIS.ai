# Repository Structure — Production Repository Design

## RS.1 Architecture Decision: Monorepo vs Polyrepo

**Decision: Monorepo**

**Rationale:**
- Tight coupling between AI, policy, and API layers
- Shared libraries (types, utilities, tests)
- Easier cross-cutting changes
- Simpler CI/CD
- Better dependency management

**Tools:** pnpm workspaces, Turborepo

## RS.2 Repository Layout

```
heyjarvis/
├── .claude/
│   └── CLAUDE.md                    # Claude instructions
│
├── .github/
│   ├── workflows/                   # CI/CD pipelines
│   │   ├── ci.yml
│   │   ├── deploy-staging.yml
│   │   ├── deploy-production.yml
│   │   └── security-scan.yml
│   └── dependabot.yml
│
├── apps/                            # Application services
│   ├── web/                         # Staff dashboard (Next.js)
│   │   ├── src/
│   │   │   ├── app/
│   │   │   ├── components/
│   │   │   ├── lib/
│   │   │   └── styles/
│   │   ├── public/
│   │   ├── package.json
│   │   └── next.config.js
│   │
│   ├── api/                         # REST API (FastAPI)
│   │   ├── src/
│   │   │   ├── routes/
│   │   │   ├── middleware/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── worker/                      # Background worker
│   │   ├── src/
│   │   │   ├── tasks/
│   │   │   ├── consumers/
│   │   │   ├── pipelines/
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── chatbot-ui/                  # Patient-facing chat widget
│       ├── src/
│       ├── dist/
│       ├── package.json
│       └── webpack.config.js
│
├── packages/                        # Shared packages
│   ├── shared/                      # Shared types and utilities
│   │   ├── src/
│   │   │   ├── types.ts
│   │   │   ├── utils.ts
│   │   │   ├── constants.ts
│   │   │   └── errors.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── ai/                          # AI/ML package
│   │   ├── src/
│   │   │   ├── intent/
│   │   │   ├── safety/
│   │   │   ├── tools/
│   │   │   ├── prompts/
│   │   │   ├── evaluation/
│   │   │   └── index.ts
│   │   ├── prompts/                 # Prompt files
│   │   │   ├── conversation_agent.md
│   │   │   ├── intent_classifier.md
│   │   │   ├── message_generator.md
│   │   │   └── safety_classifier.md
│   │   ├── tests/
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── policy/                      # Policy engine
│   │   ├── src/
│   │   │   ├── eligibility/
│   │   │   ├── consent/
│   │   │   ├── suppression/
│   │   │   ├── frequency/
│   │   │   └── index.ts
│   │   ├── tests/
│   │   ├── package.json
│   │   └── tsconfig.json
│   │
│   ├── database/                    # Database package
│   │   ├── src/
│   │   │   ├── models/
│   │   │   ├── migrations/
│   │   │   ├── queries/
│   │   │   └── index.ts
│   │   ├── migrations/
│   │   ├── seeds/
│   │   ├── package.json
│   │   └── package.json
│   │
│   └── integrations/                # Integration adapters
│       ├── src/
│       │   ├── scheduling/
│       │   │   ├── opendental.ts
│       │   │   ├── eaglesoft.ts
│       │   │   ├── dentrix.ts
│       │   │   └── base.ts
│       │   ├── insurance/
│       │   ├── communication/
│       │   │   ├── twilio.ts
│       │   │   └── postmark.ts
│       │   └── index.ts
│       ├── tests/
│       ├── package.json
│       └── tsconfig.json
│
├── services/                        # Standalone services
│   ├── scheduler/                   # Cron/scheduled jobs
│   │   ├── src/
│   │   ├── jobs/
│   │   ├── Dockerfile
│   │   └── package.json
│   │
│   ├── communications/              # Message delivery service
│   │   ├── src/
│   │   ├── channels/
│   │   ├── templates/
│   │   ├── Dockerfile
│   │   └── package.json
│   │
│   └── analytics/                   # Analytics service
│       ├── src/
│       ├── aggregations/
│       ├── Dockerfile
│       └── package.json
│
├── ml/                              # Machine Learning
│   ├── datasets/                    # Dataset definitions
│   │   ├── intent/
│   │   ├── conversion/
│   │   ├── safety/
│   │   └── README.md
│   ├── features/                    # Feature engineering
│   │   ├── patient_features.py
│   │   ├── campaign_features.py
│   │   └── feature_store.py
│   ├── training/                    # Training scripts
│   │   ├── intent_classifier/
│   │   ├── conversion_model/
│   │   ├── priority_scorer/
│   │   └── train.py
│   ├── evaluation/                  # Evaluation scripts
│   │   ├── safety_eval.py
│   │   ├── intent_eval.py
│   │   ├── regression_test.py
│   │   └── eval_suite.py
│   ├── models/                      # Saved models
│   │   ├── intent_v1/
│   │   ├── conversion_v1/
│   │   └── model_registry.json
│   └── experiments/                 # Experiment tracking
│       ├── results/
│       └── experiment_log.md
│
├── prompts/                         # Prompt library
│   ├── v1/
│   │   ├── conversation_agent.md
│   │   ├── intent_classifier.md
│   │   ├── message_generator.md
│   │   ├── safety_classifier.md
│   │   ├── summarizer.md
│   │   └── handoff_summarizer.md
│   ├── v2/                          # Future versions
│   └── prompt_registry.json
│
├── infra/                           # Infrastructure as Code
│   ├── terraform/                   # Terraform configs
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── modules/
│   │   └── environments/
│   │       ├── staging/
│   │       └── production/
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.worker
│   │   └── .dockerignore
│   ├── kubernetes/
│   │   ├── deployments/
│   │   ├── services/
│   │   ├── ingress/
│   │   └── configmaps/
│   └── scripts/
│       ├── deploy.sh
│       ├── migrate.sh
│       └── backup.sh
│
├── docs/                            # Documentation
│   ├── 00-executive-summary.md
│   ├── 01-product-requirements.md
│   ├── ... (all 34 docs)
│   ├── adr/
│   │   ├── 0001-use-monorepo.md
│   │   ├── 0002-use-postgresql.md
│   │   └── ...
│   ├── diagrams/
│   │   ├── architecture.png
│   │   ├── state-machine.png
│   │   ├── data-flow.png
│   │   └── ...
│   └── api/
│       └── openapi.yaml
│
├── tests/                           # Cross-cutting tests
│   ├── fixtures/
│   ├── helpers/
│   ├── e2e/
│   │   ├── test_booking_flow.py
│   │   ├── test_campaign_flow.py
│   │   └── test_safety_flow.py
│   └── performance/
│       ├── load_test.py
│       └── stress_test.py
│
├── scripts/                         # Utility scripts
│   ├── seed_data.py
│   ├── generate_synthetic.py
│   ├── run_evaluation.py
│   └── health_check.py
│
├── .env.example                     # Environment variable template
├── .gitignore
├── .prettierrc
├── .eslintrc.js
├── docker-compose.yml               # Local development
├── docker-compose.prod.yml          # Production compose
├── Makefile                         # Common commands
├── package.json                     # Root package (workspaces)
├── pnpm-workspace.yaml
├── turbo.json                       # Turborepo config
├── pyproject.toml                   # Python config
├── tox.ini                          # Python test runner
└── README.md
```

## RS.3 Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **API** | FastAPI (Python) | Fast, async, great for AI/ML integration |
| **Frontend** | Next.js (React) | SSR, React ecosystem, good DX |
| **Worker** | Python (asyncio) | Same language as API, easy sharing |
| **Database** | PostgreSQL | ACID, JSONB, mature, RLS support |
| **Cache** | Redis | Fast, versatile (cache + queue) |
| **Queue** | Redis Streams → Kafka | Start simple, scale later |
| **LLM** | Anthropic Claude | Quality, safety, API reliability |
| **SMS** | Twilio | Industry standard, reliable |
| **Email** | Postmark | Reliable, good deliverability |
| **Infrastructure** | Docker + K8s | Standard, scalable |
| **IaC** | Terraform | Multi-cloud, widely adopted |
| **Monitoring** | Datadog / Prometheus + Grafana | Full observability |
| **CI/CD** | GitHub Actions | Integrated, good free tier |

## RS.4 Build and Deployment

### Makefile Commands

```makefile
.PHONY: install test lint format deploy

install:
	pnpm install
	pip install -r requirements.txt

test:
	pnpm test
	pytest

test-ai:
	pnpm test:ai
	python -m ml.evaluation.run_all

lint:
	pnpm lint
	ruff check src/
	black --check src/

format:
	pnpm format
	ruff format src/
	black src/

migrate:
	alembic upgrade head

seed:
	python scripts/seed_data.py

evaluate:
	python scripts/run_evaluation.py

deploy-staging:
	cd infra && terraform apply -var environment=staging

deploy-production:
	cd infra && terraform apply -var environment=production

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
      - run: pnpm lint

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v3
      - run: pnpm test
      - run: pytest tests/ --cov

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm audit
      - run: pip install safety && safety check
      - run: trufflehog --fail .  # Secret scanning

  ai-eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: python -m ml.evaluation.run_all
```
