# UI/UX Review Checklist — Mobile Apps

A systematic approach to evaluating mobile app UIs. Covers visual consistency, interaction quality, information hierarchy, and platform conventions.

## How to use

1. Open every screen in the app (each `build()` method).
2. For each screen, run through the checklist below.
3. Rate findings as **🔴 Alta** (blocks UX), **🟡 Media** (noticeable), or **🟢 Baja** (polish).
4. Present findings per-screen in a table.

## Checklist (per-screen)

### 🏠 Home / Dashboard
- Acciones principales visibles sin scroll
- Botones agrupados por categoría (monitoreo ≠ preparación)
- Jerarquía visual clara (títulos ≠ contenido ≠ acciones)
- Estados vacíos — qué muestra cuando no hay datos
- Pull-to-refresh presente en listas

### 📋 Listas
- Color codifica información — y tiene leyenda visible
- Cada item es tocable — tamaño mínimo 44px
- Iconos consistentes en toda la app

### 🗺️ Mapas
- Leyenda superpuesta — colores/tamaños se entienden sin salir del mapa
- Clustering — elementos cercanos se agrupan
- Centro dinámico — no siempre fijo

### ⚙️ Ajustes
- Secciones agrupadas con iconos — no un listview interminable
- Confirmación en acciones destructivas

### 🆘 SOS / Emergencia
- Detecta hardware disponible y muestra estado
- Botón grande y contrastante
- Funciona sin internet

## Cross-cutting
- Tema oscuro soportado
- Loading y error states
- Áreas táctiles ≥ 44px
- No solo color para transmitir información

## Priority guide
| Level | Definition | Should fix |
|-------|------------|------------|
| 🔴 Alta | Bloquea la tarea o causa confusión | Antes del próximo release |
| 🟡 Media | Notorio pero no bloqueante | Próximo sprint |
| 🟢 Baja | Pulido visual, nice-to-have | Cuando sobre tiempo |

## Real-world review findings (SismoVE Android app)

A 26-item review across 13+ screens identified these common UI issues in emergency/safety mobile apps:

### Top fixes applied

| Screen | Problem | Fix |
|--------|---------|-----|
| Home | 8 botones mezclados (monitoreo + preparación) | Dividir en 2 filas con separadores 📡 / 🧰 |
| Home | Filtros inline muy pequeños (12px) | 13px + `VisualDensity.comfortable` |
| Mapa | Sin leyenda de colores | Card superpuesta con 4 rangos de magnitud |
| Mapa | Marcadores superpuestos en zonas densas | Clustering simple (< 1° de distancia) |
| Mapa | Centro siempre fijo en Venezuela | Centro dinámico = promedio de coordenadas |
| Settings | ListView interminable sin secciones | Cards con icono + título + divider |
| Detalle | Inf rows solo texto, sin elevación | Cards con CircleAvatar + icono |
| Detalle | Marker genérico `Icons.circle` | Container con border + shadow |
| Detalle | Sin botón compartir | Share vía WhatsApp |
| Guía | Solo texto plano sin iconos | 4 cards con icono + color por fase |
| Kit | Lista plana sin categorías | 5 categorías + barra de progreso |
| Plan familiar | "Estoy bien" simulado | SMS/WhatsApp real a contactos listados |
| General | Sin tema oscuro | `darkTheme` + `ThemeMode.system` |
| SOS | Sonido requiere internet | Asset WAV local |
| Contactos | Solo números fijos | Picker de agenda + mensajes preconfigurados |
