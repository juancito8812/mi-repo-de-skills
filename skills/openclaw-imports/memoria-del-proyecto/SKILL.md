---
name: memoria-del-proyecto
description: >
  Mantiene memoria persistente del proyecto en un archivo .agents/MEMORY.md.
  Al iniciar una sesión, carga el contexto completo (arquitectura, decisiones,
  estado actual, tareas pendientes). Al finalizar, actualiza la memoria con
  los cambios realizados. Ideal para retomar proyectos después de semanas o meses.
license: MIT
metadata:
  category: utility
---

# Memoria del Proyecto

Esta skill permite que Codebuff mantenga una memoria persistente del proyecto
a través de sesiones. Almacena información clave como la arquitectura,
decisiones de diseño, estado actual, cambios recientes y próximos pasos
en un archivo `.agents/MEMORY.md` dentro del proyecto actual.

> **⚠️ Importante:** Esta skill es **global** (se instala una sola vez en
> `~/.agents/skills/memoria-del-proyecto/`). Cada proyecto tiene su propio
> archivo `.agents/MEMORY.md` con su estado particular.

## Comportamiento

### Al iniciar una sesión (automático)

1. Detecta si existe el archivo `.agents/MEMORY.md` en el proyecto actual.
2. **Si existe:** léelo completo para cargar el contexto. Luego responde al
   usuario con un breve resumen del estado del proyecto y ofrécele continuar
   desde donde se quedó la última vez.
3. **Si NO existe:** ofrécete a inicializar la memoria del proyecto. Cuando
   el usuario lo apruebe, crea `.agents/MEMORY.md` con el contenido mínimo:
   - Nombre del proyecto
   - Stack tecnológico (basado en package.json, Cargo.toml, etc.)
   - Propósito/resumen de una línea
   - Marcarlo como "Primera sesión — sin historial previo"

### Durante la sesión

1. Rastrea mentalmente los cambios significativos que se realicen:
   - Archivos creados, modificados o eliminados
   - Dependencias agregadas o removidas
   - Decisiones de arquitectura o diseño
   - Problemas encontrados y cómo se resolvieron
   - Tareas completadas
2. No escribas al archivo `.agents/MEMORY.md` durante la sesión a menos que
   el usuario lo solicite explícitamente.

### Al finalizar la sesión (cuando el usuario lo solicite o se indique "actualiza la memoria")

1. Actualiza el archivo `.agents/MEMORY.md` con toda la información nueva.
2. Usa un formato claro y consistente (ver sección Formato más abajo).
3. Preserva la información anterior que sigue siendo relevante.
4. Actualiza: versión de la memoria, última sesión, cambios realizados,
   decisiones tomadas, estado actual y próximos pasos.

## Formato del archivo .agents/MEMORY.md

El archivo sigue esta estructura:

```markdown
# Memoria del Proyecto: [Nombre del Proyecto]

## Información General

- **Propósito:** [Descripción de una línea]
- **Stack:** [Tecnologías principales]
- **Última sesión:** [Fecha y hora]
- **Versión de memoria:** [Número incremental]

## Arquitectura

[Descripción de la estructura del proyecto, organización de directorios,
patrones principales, flujo de datos]

## Decisiones Clave

- **[Fecha]** — [Decisión tomada]: [Contexto breve y razón]

## Estado Actual

- **Branch:** [rama activa]
- **Lo que se está trabajando:** [descripción breve]
- **Ticket/issue:** [referencia si aplica]

## Cambios Recientes

- **[Fecha]** — [Cambio realizado]: [breve descripción]

## Próximos Pasos / TODOs

- [ ] Tarea pendiente 1
- [ ] Tarea pendiente 2

## Notas / Problemas Conocidos

- [Problema o nota relevante]
```

## Instrucciones Clave

1. **Siempre** busca y lee `.agents/MEMORY.md` al inicio de la conversación.
2. **Siempre** confirma con el usuario antes de sobrescribir información
   importante en el archivo de memoria.
3. **Mantén** la memoria actualizada pero concisa. No acumules información
   obsoleta — archívala o elimínala.
4. **Preserva** las decisiones importantes y su justificación. Son el recurso
   más valioso para retomar el proyecto después de mucho tiempo.
5. **Si el usuario solicita** "actualiza la memoria" o "guarda el progreso",
   ejecuta la actualización completa de `.agents/MEMORY.md`.

## Activación

Esta skill se activa automáticamente al inicio de cada conversación por su
descripción. También se puede invocar manualmente con:

```
/skill:memoria-del-proyecto
```

O mencionándola en el mensaje:

```
@memoria-del-proyecto ¿qué se estaba haciendo aquí?
```
