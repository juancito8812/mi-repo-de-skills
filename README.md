# Skills para Tasa del Día

Skills de Superpowers + Ponytail + skills personalizadas para proyectos de desarrollo.

## Skills

### Superpowers Skills (`.agents/skills/` — 17 skills)
brainstorming, dispatching-parallel-agents, executing-plans, find-skills, finishing-a-development-branch, image-to-ai, ponytail, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, verification-before-completion, writing-plans, writing-skills

### Custom Skills (`skills/` — 9 skills)

| Skill | Versión | Propósito |
|-------|---------|-----------|
| auto-sync | 1.1.0 | Auto-sync git + handoff para tasa-del-dia-app |
| changelog-generator | 1.1.0 | Generar changelogs desde commits |
| error-handling-patterns | 1.1.0 | Patrones multi-lenguaje de manejo de errores |
| frontend-design | 1.1.0 | Diseño visual distintivo para UI |
| graphql-api-design | 1.0.0 | Diseño de APIs GraphQL con schema, DataLoader y Relay |
| interface-design | 1.1.0 | Diseño craft-first de interfaces producto |
| postgresql-table-design | 1.1.0 | Diseño de schemas PostgreSQL |
| restful-api-design | 1.0.0 | Diseño de APIs REST con naming, HTTP y errores |
| vercel-react-best-practices | 1.1.0 | Optimización React/Next.js |

Todas las skills incluyen:
- Frontmatter HADS completo (name, description, version, metadata)
- Checklist de verificación pre-ejecución
- Contenido ejecutable con ejemplos concretos
- Exit Criteria para validar resultados

## Instalación

```json
{
  "plugin": [
    "superpowers@git+https://github.com/obra/superpowers.git",
    "https://raw.githubusercontent.com/juancito8812/mi-repo-de-skills/v1.0.0/.opencode/plugins/ponytail.mjs"
  ]
}
```
