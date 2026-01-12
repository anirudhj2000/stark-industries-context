# Organization Ontology Draft

## News Website Company
**Total Headcount:** 27 people

---

## Departments Overview

| Department | Headcount | Lead Role |
|------------|-----------|-----------|
| Editorial | 14 | Managing Editor |
| Research & Investigation | 5 | Research Lead |
| Technology | 6 | Engineering Lead |
| Operations & Support | 2 | — |

---

## Organization Chart

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NEWS WEBSITE COMPANY                               │
│                            (27 employees)                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────┬───────────┴───────────┬───────────────┐
        ▼               ▼                       ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   EDITORIAL   │ │   RESEARCH    │ │  TECHNOLOGY   │ │  OPERATIONS   │
│   (14 ppl)    │ │   (5 ppl)     │ │   (6 ppl)     │ │   (2 ppl)     │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │                 │
        ▼                 ▼                 ▼                 ▼
 Managing Editor    Research Lead    Engineering Lead   HR & Admin (1)
        │                 │                 │           Social Media (1)
        │                 │                 │
   ┌────┼────┐       ┌────┴────┐       ┌────┴────┐
   ▼    ▼    ▼       ▼         ▼       ▼         ▼
Senior Staff  Copy  Senior   Research  Devs(3)  Product
Writers Writers Editors Researchers Analysts DevOps(1) Designer(1)
 (4)    (6)   (3)    (2)       (2)
```

---

## Roles by Department

### Editorial (14)

| Role | Count | Reports To | Key Responsibilities |
|------|-------|------------|---------------------|
| Managing Editor | 1 | Ownership | Daily editorial ops, calendar, staff management |
| Senior Writer | 4 | Managing Editor | Beat coverage (Politics, Business, Tech, Culture) |
| Staff Writer | 6 | Managing Editor | Daily content production |
| Copy Editor | 3 | Managing Editor | Quality control, fact-checking, style compliance |

### Research & Investigation (5)

| Role | Count | Reports To | Key Responsibilities |
|------|-------|------------|---------------------|
| Research Lead | 1 | Ownership | Research methodology, team coordination |
| Senior Researcher | 2 | Research Lead | Complex investigations, OSINT |
| Research Analyst | 2 | Research Lead | Data gathering, verification |

### Technology (6)

| Role | Count | Reports To | Key Responsibilities |
|------|-------|------------|---------------------|
| Engineering Lead | 1 | Ownership | Architecture, code quality, team leadership |
| Full-Stack Developer | 3 | Engineering Lead | Platform development, features |
| DevOps Engineer | 1 | Engineering Lead | CI/CD, infrastructure, monitoring |
| Product Designer | 1 | Engineering Lead | UX/UI, user research, design system |

### Operations & Support (2)

| Role | Count | Reports To | Key Responsibilities |
|------|-------|------------|---------------------|
| HR & Admin Coordinator | 1 | Ownership | Recruitment, onboarding, benefits |
| Social Media Manager | 1 | Ownership | Audience engagement, content distribution |

---

## Onboarding Processes

### Universal (All Hires)
- **Duration:** 2 weeks
- **Covers:** Company mission, tools access, compliance training, team intros

### Department-Specific (4 weeks each)

| Department | Key Focus Areas |
|------------|-----------------|
| Editorial | CMS training, style guide, fact-checking, first byline |
| Research | OSINT, verification methods, source protection, legal boundaries |
| Technology | Dev environment, codebase, CI/CD, first feature delivery |
| Operations | HRIS systems, recruitment process, social platforms |

---

## Coverage Areas
- Politics
- Business
- Technology
- Culture

---

## Entity File Locations

```
entities/
├── organization/
│   └── news_company/context.yaml
├── department/
│   ├── editorial/context.yaml
│   ├── research/context.yaml
│   ├── technology/context.yaml
│   └── operations/context.yaml
├── role/
│   ├── managing_editor/context.yaml
│   ├── senior_writer/context.yaml
│   ├── staff_writer/context.yaml
│   ├── copy_editor/context.yaml
│   ├── research_lead/context.yaml
│   ├── senior_researcher/context.yaml
│   ├── research_analyst/context.yaml
│   ├── engineering_lead/context.yaml
│   ├── fullstack_developer/context.yaml
│   ├── devops_engineer/context.yaml
│   ├── product_designer/context.yaml
│   ├── hr_admin_coordinator/context.yaml
│   └── social_media_manager/context.yaml
└── process/
    └── onboarding/
        ├── universal/context.yaml
        ├── editorial/context.yaml
        ├── research/context.yaml
        ├── technology/context.yaml
        └── operations/context.yaml
```

---

*Generated for Parallelloop AI - News Website Company*
