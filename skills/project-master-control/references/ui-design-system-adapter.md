# UI Design System Adapter

Use this reference when the product manager thread creates a UI/UX design child thread, frontend implementation child thread, or visual review child thread. The goal is to force Codex to behave like a product UI designer first, then a UI engineer, then a visual QA reviewer.

## Product Manager Rule

Before any UI/frontend implementation task, the product manager thread must provide a UI Design Brief. The brief must specify:

- product type: CRM, SaaS, admin, dashboard, desktop app, mobile entry, AI console, etc.;
- target users and work frequency;
- visual style track;
- technology stack or component library;
- design tokens;
- component breakdown;
- business state logic;
- required screenshots/prototypes or design handoff;
- implementation acceptance criteria.

If the technology stack is unknown, ask the user or infer from the repo before dispatching frontend implementation.

## Style Tracks

### A. Dark Productivity

Use for CRM, operations console, monitoring, AI workbench, and long-hour internal tools.

Prompt core:

```text
UI UX design, B2B SaaS/CRM operations workspace, dark mode first, deep charcoal background, low decoration, high scanning efficiency, precise 1px borders, sharp typography, dense but organized data, no landing page, no hero, no decorative gradients, engineering-driven professional interface.
```

### B. Minimal Light SaaS

Use for clean analytics, simple admin, premium modern tools.

Prompt core:

```text
UI UX design, enterprise SaaS interface, minimalist light mode, white and off-white surfaces, subtle slate typography, micro borders, generous but controlled spacing, refined shadows, premium modern software feel, functional and readable.
```

### C. Controlled Glass / AI Tech

Use only for AI panels, insight cards, monitoring centers, or visual hero modules. Do not use for dense daily tables.

Prompt core:

```text
UI UX design, AI insights panel, controlled glassmorphism, dark navy backdrop, semi-transparent frosted panels, subtle violet/cyan accents, readable text, restrained glow, data provenance focused, not decorative.
```

### D. Compact Traditional B2B

Use for ERP, Feishu-like admin, heavy data entry, call center workflows.

Prompt core:

```text
UI UX design, heavy data-dense enterprise table, compact light mode, tight row padding, clear grid lines, colored status badges, icon-driven actions, zero decorative graphics, built for long-hour administrative workflows and maximum layout efficiency.
```

## Technology Stack Adapters

### Ant Design

Use AntD when the project needs fast enterprise delivery, complex tables/forms, business workflow components, or strict consistency.

Design/implementation guidance:

- Use `ConfigProvider` and theme tokens before custom CSS.
- Prefer `Table`, `Form`, `Drawer`, `Modal`, `Tabs`, `Steps`, `Badge`, `Tag`, `Tooltip`, `Dropdown`, `Segmented`.
- Tables should define fixed columns, sorter/filter states, row actions, empty/loading/error states.
- Forms should use `Form layout="vertical"`, rules, disabled states, feedback, and grouped sections.
- High-risk actions should use semantic danger buttons.
- Do not recreate AntD primitives with ad-hoc Tailwind unless the project has intentionally rejected AntD styling.

Prompt add-on:

```text
Use React + Ant Design v5 thinking. Describe the UI through AntD component composition and theme tokens. Use Table/Form/Drawer/Badge/Tag/Tooltip semantics. Avoid hand-written CSS except for token-level layout wrappers.
```

### Tailwind CSS

Use Tailwind when the UI needs custom visual direction, precise density control, or no heavy component library.

Design/implementation guidance:

- Define tokens first: colors, spacing, radius, typography, status colors.
- Restrict radius and shadows. For B2B tools prefer `rounded-sm` / `rounded-md`, `border`, `shadow-sm` only.
- Use 4px/8px spacing rhythm.
- Use semantic classes through component wrappers, not one-off class sprawl.
- Use responsive grid constraints intentionally; do not let content collapse unpredictably.

Prompt add-on:

```text
Use Tailwind CSS utility classes but follow fixed design tokens. Radius <= 8px, spacing based on 4px/8px grid, no decorative gradients, no card nesting, no text overflow, complete responsive states.
```

### Shadcn UI

Use Shadcn when the project needs modern SaaS quality, source ownership, Radix accessibility, and Tailwind customization.

Design/implementation guidance:

- Use `components/ui` as owned source, not opaque package behavior.
- Prefer Radix-backed primitives for Dialog, Sheet, Popover, DropdownMenu, Tabs, Select, Tooltip, Command.
- Use `cn` and `class-variance-authority` style variants for status, density, and semantic intent.
- Pair with TanStack Table for complex tables.
- Avoid generic template-dashboard composition; tune density, hierarchy, and state logic for the product.

Prompt add-on:

```text
Use Shadcn UI + Tailwind design language. Treat components as project-owned source. Use Radix primitives for interaction/accessibility, Tailwind tokens for visual styling, and variant-driven component APIs.
```

### Material UI

Use MUI when the project needs strong theming, slot-level customization, cross-platform consistency, or Material Design conventions.

Design/implementation guidance:

- Use `ThemeProvider`, palette, typography, spacing, shape, shadows, and component overrides.
- Prefer `sx` or theme overrides, not scattered global CSS.
- Respect slots and component state classes.
- Avoid default MUI look if the product requires a custom brand; theme it deliberately.

Prompt add-on:

```text
Use MUI theme-first thinking. Define palette, typography, spacing, shape, and component overrides. Use component slots and `sx` intentionally; avoid random CSS overrides.
```

### Vue / Element Plus

Use Vue + Element Plus for conventional admin systems, fast CRUD, and Chinese enterprise workflows.

Design/implementation guidance:

- Use Element Plus table/form/drawer/dialog/tag/message semantics.
- Define density and status colors through CSS variables or theme overrides.
- Keep templates readable and componentized; avoid inline style sprawl.
- Model business states explicitly in computed props.

Prompt add-on:

```text
Use Vue 3 + Element Plus admin-system thinking. Structure the page with el-table, el-form, el-drawer, el-tag, el-tooltip, and theme variables. Keep business status logic explicit and reusable.
```

### Flutter / Mobile Entry

Use Flutter for mobile capture, quick entry, lightweight review, and PWA-like companion workflows. Do not copy desktop tables into mobile.

Design/implementation guidance:

- Convert tables into `ListView`, cards, sections, and bottom sheets.
- Touch targets >= 48dp.
- Put missing/blocked status near the top of each card.
- Use camera/upload/quick-input flows as primary actions.
- Keep mobile scope narrow; do not expose full desktop CRM workflows.

Prompt add-on:

```text
Use Flutter mobile-first UI. No complex tables. Use ListView/Card/BottomSheet, 48dp touch targets, clear status-first cards, camera/upload/quick-entry flows, and concise review states.
```

## Design Tokens Pipeline

Every UI design handoff should include tokens before component implementation.

```json
{
  "theme": {
    "colors": {
      "bg-main": "#0f1115",
      "bg-surface": "#181a20",
      "border-default": "#262930",
      "text-primary": "#f3f4f6",
      "text-secondary": "#9ca3af",
      "accent-success": "#14b8a6",
      "accent-warning": "#f59e0b",
      "accent-danger": "#ef4444",
      "accent-ai": "#8b5cf6"
    },
    "spacing": {
      "xs": "4px",
      "sm": "8px",
      "md": "16px",
      "lg": "24px"
    },
    "radius": {
      "sm": "2px",
      "md": "6px",
      "lg-max": "8px"
    },
    "fontSize": {
      "table-body": "13px",
      "section-title": "16px",
      "page-title": "24px"
    }
  }
}
```

Adapt token output to the chosen stack:

- Tailwind: `tailwind.config.js` or CSS variables;
- AntD: `ConfigProvider` theme tokens;
- Shadcn: CSS variables plus Tailwind config;
- MUI: `createTheme` palette/typography/shape/components;
- Element Plus: CSS variables/theme overrides;
- Flutter: `ThemeData`, color scheme, text theme, spacing constants.

## Component Breakdown

Design handoff must include a component tree, not only page screenshots.

Example format:

```text
[Page: Customer Operations Workspace]
 ├── [Topbar]
 ├── [Sidebar]
 └── [Main Layout]
      ├── [Filter Bar]
      ├── [Customer Data Table]
      │    ├── [Status Badge]
      │    ├── [Compliance Actions]
      │    └── [Row Hover Actions]
      ├── [Detail Drawer]
      │    ├── [Customer Metadata]
      │    ├── [Activity Timeline]
      │    └── [Bottom Action Bar]
      └── [AI Copilot Panel]
           ├── [Recommendation Card]
           ├── [Source Links]
           └── [Risk Review State]
```

## Business State Logic

UI design must define state behavior, not just appearance.

Required examples for CRM/operations systems:

- restricted/blacklist/do-not-contact disables outreach buttons;
- disabled controls show tooltip reasons;
- AI-generated content shows source, generation time, confidence, risk level, and review state;
- pending review uses warning semantics, not neutral gray;
- empty/loading/error/success/permission states are designed before implementation.

## State & Resilience Design

UI/UX design must cover real production edge cases, not only the ideal filled-data screen.

### Skeleton Screen

Design skeleton screens for asynchronous areas such as dense tables, detail drawers, AI recommendation panels, metric cards, timelines, upload lists, and search results.

Requirements:

- Preserve the final layout structure during loading so the page does not jump.
- Use low-contrast geometric blocks for text, buttons, rows, avatars, tags, and metrics.
- Keep skeleton dimensions close to real content dimensions.
- Prefer subtle pulse/shimmer animation; avoid full-page blank screens and generic spinners as the only loading state.
- Define which sections load independently and which sections block the whole workflow.

Stack hints:

- Tailwind: `animate-pulse` with tokenized gray surfaces.
- AntD: `Skeleton`, `Table` loading, and `Spin` only for bounded regions.
- MUI: `Skeleton` with theme tokens.
- Element Plus: `el-skeleton`.
- Flutter: shimmer/skeleton placeholders with stable layout constraints.

### Overflow Text

Design must survive extreme real business text such as long hotel names, group names, remarks, source URLs, AI citations, and compliance reasons.

For each text category, specify one strategy:

- `truncate`: single-line ellipsis plus Tooltip on hover/focus.
- `wrap`: multi-line wrapping for notes, descriptions, and AI content.
- `clamp`: 2-3 line clamp plus expand/collapse.
- `avatar fallback`: extract 2-4 characters from long names for avatar/initial display.
- `fixed width + tooltip`: stable table columns, badges, metadata labels, and action areas.

Forbidden:

- long text breaking table layout;
- buttons squeezed by names or labels;
- status badges wrapping unpredictably;
- mobile horizontal overflow;
- hidden full values without tooltip, copy, or expand path.

### Empty States

Empty states are action guidance, not decoration. Do not output only "No data" / "暂无数据".

Each important empty state must include:

- a low-saturation illustration or simple icon;
- one sentence explaining why it is empty;
- one primary call-to-action;
- optional secondary help link or rule explanation.

Examples:

- Follow-up queue empty: "你今天还没有待跟进的酒店线索" + primary action "去公共线索池抢单".
- AI recommendation empty: "当前客户资料不足，暂时无法生成可靠建议" + primary action "补齐客户资料".
- Outreach history empty: "还没有外呼记录" + primary action "发起首次外呼".
- Upload queue empty: "还没有上传交付物" + primary action "上传文件/拍照上传".

### Full State Checklist

The UI/UX handoff and visual review must check these states:

- Normal, hover, active, focus, disabled.
- Loading and skeleton.
- Empty, error, success, permission denied.
- Long text, missing metadata, malformed values.
- Blacklist/do-not-contact disabled actions with tooltip reasons.
- AI content metadata: source links, generation time, confidence, risk level, review status.
- Responsive behavior for desktop, narrow desktop, tablet, and mobile when relevant.
## Product Manager Prompt For UI/UX Child Thread

```text
你是 UI/UX 设计子线程，不是前端实现线程，也不是产品经理线程。

先读取当前任务包和产品经理提供的 UI Design Brief。你的任务是输出可交付给前端实现线程的 UI/UX Design Handoff，不写生产代码，除非产品经理明确授权。

必须先明确：
1. 产品类型和目标用户。
2. 视觉风格轨道：暗色生产力、极简白、受控玻璃/AI 科技、紧凑传统 B 端，或项目自定义风格。
3. 技术栈/组件库：AntD、Tailwind、Shadcn、MUI、Vue/Element Plus、Flutter 或其他。
4. Design Tokens。
5. 组件树和页面结构。
6. 业务状态逻辑。
7. 前端实现验收标准。

输出必须包含：Design Summary、User Roles、Core Workflows、Information Architecture、Page Inventory、Key Screens、Design Tokens、Component Breakdown、State Logic、Responsive Rules、Implementation Acceptance Criteria、Open Decisions。

禁止只输出泛泛描述。禁止营销页风格、无意义装饰、卡片套卡片、文本溢出、缺少状态设计、未说明技术栈适配。
```

## Frontend Implementation Prompt Add-on

```text
你是前端实现子线程。严格根据 UI/UX Design Handoff 实现，不重新发明视觉方向。

实现前必须确认：技术栈/组件库、tokens、组件树、业务状态逻辑、响应式规则、验收截图要求。

不得自行改变主视觉风格、布局层级、状态语义或组件库策略。如发现设计 handoff 不足，写入 STATUS.md 并回传产品经理线程确认。
```

## UI Visual Review Prompt

```text
你是 UI Visual Review 子线程，只做视觉和体验审查，不写业务代码。

基于 UI/UX Design Handoff、实现截图和当前产品目标检查：
- 是否符合目标风格和技术栈约束；
- 是否像真实成熟产品，而不是模板页；
- 信息层级、间距、字号、颜色、状态是否一致；
- 表格、筛选、详情、表单、AI 组件是否适合长期办公；
- 是否有文本溢出、按钮拥挤、卡片套卡片、状态缺失；
- 桌面/移动端是否都可用；
- 是否满足业务状态逻辑。

输出：通过项、必须返工项、建议优化项、是否允许进入验收。
```