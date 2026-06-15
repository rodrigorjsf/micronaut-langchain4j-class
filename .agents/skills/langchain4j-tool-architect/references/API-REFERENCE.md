# API Reference — LangChain4j tools (PERISHABLE)

> ⚠️ **Grounded against LangChain4j `1.16.2` only.** Every identifier below is
> version-specific and is the *first* thing to rot when the project is on another
> version. **Before you emit any code:** detect the project's LangChain4j version
> (Step 0) and re-verify each name you intend to use against that version's
> javadoc / source / changelog. If the version differs, treat this file as a set
> of hypotheses, not facts. This is the only file in the skill you should expect
> to re-ground; the design rules in BEST-PRACTICES.md are stable.

Primary source for all of the below: the tagged source tree at
https://github.com/langchain4j/langchain4j/tree/1.16.2 (notably
`langchain4j-core/.../agent/tool/`, `.../service/tool/`, `.../guardrail/`,
`langchain4j-skills/`) and the tutorials at <https://docs.langchain4j.dev>.

---

## 1. Annotation-based tools

- **`@Tool`** (on a method). Attributes:
  - `name()` — defaults to the method name.
  - `value()` — the **description**; typed `String[]` (multi-line allowed).
  - `returnBehavior()` — *Experimental*; `TO_LLM` (default), `IMMEDIATE`,
    `IMMEDIATE_IF_LAST`.
  - `searchBehavior()` — *Experimental*; see tool search below.
- **`@P`** (on a parameter):
  - `value()` / `description()` — the parameter description (aliases).
  - `name()` — explicit parameter name.
  - `required()` — **defaults to `true`**. ⚠️ Every `@P` parameter is mandatory
    unless you set `required = false` or use `Optional<T>`.
  - `defaultValue()`.
- **`@ToolMemoryId`** (on a parameter) — injects the memory/session identity;
  **no attributes**. Pairs with `@MemoryId` on the AI Service interface. This is
  the mechanism that keeps identity off the model-facing contract (Identity
  test).

### Return types sent to the model
- `void` → the literal string `"Success"`.
- `String` → sent as-is (no JSON serialization).
- record / POJO / Collection → serialized to JSON.
- ⚠️ **Raw `Map` trap:** the special-case that skips schema is matched by
  **exact reference equality** (`type == Map.class`). A *concrete* `HashMap` /
  `LinkedHashMap` falls through to the POJO parser and *does* get a schema, with
  surprising results. **Return a concrete record/POJO, never a raw `Map`.**

---

## 2. Wiring into AiServices

```java
AiServices.builder(Assistant.class)
    .chatModel(model)
    .tools(toolObject)                              // @Tool methods via reflection
    .tools(Collection<Object> toolObjects)          // many annotated objects
    .tools(Map<ToolSpecification, ToolExecutor>)    // low-level, programmatic
    .toolProvider(toolProvider)                     // dynamic per-turn gating
    .build();
```

Low-level building blocks (package `dev.langchain4j.agent.tool` /
`dev.langchain4j.service.tool`):
- **`ToolSpecification`** — name, description, `inputParametersSchema()` (JSON
  Schema). The programmatic equivalent of a tool contract.
- **`ToolExecutor`** — the callable that runs the tool.

---

## 3. Dynamic gating — ToolProvider

- **`ToolProvider`** with `provideTools(ToolProviderRequest)` returning
  **`ToolProviderResult`** (built via its `Builder.add(spec, executor)`).
- `ToolProviderRequest` exposes the user message (e.g.
  `request.userMessage().singleText()` — the **raw user message**).
- `isDynamic()` — return `true` to re-evaluate the provider on every loop turn;
  default behavior evaluates once at the start.

This one substrate underlies all three gating strategies: static `.tools(...)`,
vector tool-search, and skills.

---

## 4. Tool search / RAG-over-tools (*Experimental*)

Two mechanisms over the `ToolProvider` substrate:

**(A) Built-in, model-driven:**
- Attach `VectorToolSearchStrategy` (implements `ToolSearchStrategy`) via
  `.toolSearchStrategy(new VectorToolSearchStrategy(embeddingModel))`.
- The model fires a meta-tool to search; **the model's query** (not the raw user
  message) is embedded; top-K tools are injected.
- `SearchBehavior` enum: `SEARCHABLE` (default; hidden until matched) and
  `ALWAYS_VISIBLE` (always exposed).
- Defaults: `maxResults = 5`, `minScore = 0.0`, tool-description embeddings
  cached.

**(B) Hand-rolled, you-driven:** implement `ToolProvider`, embed
`request.userMessage()` yourself, return top-K. Search runs on the **user
message** (anticipatory) rather than a model query (reactive). Set `isDynamic()`
= `true`.

⚠️ Both are `@Experimental` and **not verified end-to-end on every provider**
(notably not confirmed running on Bedrock). Treat as "fits by construction," not
"guaranteed."

---

## 5. Safety knobs & traps (AiServices builder)

- ⚠️ **Required-object-null trap:** a missing *object* parameter declared
  `required = true` is passed **silently as `null`**; only missing *primitives*
  throw `ToolArgumentsException`. **Validate critical objects defensively inside
  the tool** — don't rely on `required = true` alone.
- **Error leakage (default):** an exception thrown by a `@Tool` has its
  `getMessage()` captured and sent to the model — leaking internals/PII. Override
  with `toolExecutionErrorHandler((error, ctx) -> ToolErrorHandlerResult.text(
  sanitizedMessage))` and log the real cause server-side. (Failure-as-data test.)
- **Hallucinated tool names:** default `hallucinatedToolNameStrategy` is
  `HallucinatedToolNameStrategy.THROW_EXCEPTION` — ⚠️ that is the **sole** enum
  constant (there is no plain `THROW`). Override with a `Function` returning a
  `ToolExecutionResultMessage` if you want graceful recovery.
- ⚠️ **Loop runaway:** `maxToolCallingRoundTrips(int)` **defaults to `100`**.
  Cap it (e.g. 6–8) in production to bound cost and contain a misbehaving agent.

---

## 6. Guardrails (`dev.langchain4j.guardrail`)

- **`InputGuardrail`** — `validate(UserMessage)` returns `success()`,
  `failure(String)`, or `fatal(String)`. **No reprompt on input** — it can only
  pass or exit.
- **`OutputGuardrail`** — `validate(AiMessage)` returns `success()`,
  **`reprompt(message, repromptText)`**, or **`retry(message)`**.
  ⚠️ `reprompt(...)` / `retry(...)` are **default methods of the interface**,
  invoked from inside `validate()`. They are **NOT** static factories on
  `OutputGuardrailResult` — `OutputGuardrailResult.reprompt(...)` does not
  compile.
- Register with `@InputGuardrails(...)` / `@OutputGuardrails(value = ...,
  maxRetries = N)` (method > class > builder precedence).
  ⚠️ `maxRetries` is the **total** number of model invocations, not *additional*
  ones — default `2` means 1 initial + 1 retry. Exhaustion throws
  `OutputGuardrailException`.
- Guardrails are defense-in-depth, **not** authorization (see SECURITY-OWASP.md).

---

## 7. Observability (`ChatModelListener`)

- Interface `dev.langchain4j.model.chat.listener.ChatModelListener` with default
  no-op `onRequest`, `onResponse`, `onError`.
- ⚠️ Listeners run **synchronously and sequentially in the calling thread.** A
  blocking export (HTTP to a tracing backend) inside a listener penalizes *every*
  model call. **Emit spans/metrics asynchronously** (batch processor / async
  OTLP) — never block in the listener.
- `attributes()` is a mutable map shared `onRequest → onResponse/onError`; carry
  the span, start time, and a correlation/transaction id through it.
- Register on the model builder via `.listeners(...)`.
- For tool-call telemetry, capture: tool name, **sanitized** arguments, shaped
  result, latency, error, retry count, and a correlation id.

---

## 8. Skills (`dev.langchain4j:langchain4j-skills`, *Experimental*)

- Implements the open **agentskills.io `SKILL.md`** format; model-agnostic
  (works through any `ChatModel` / `ToolProvider`).
- ⚠️ **Lockstep version with core:** `X.Y.Z-betaN` depends on core `X.Y.Z`
  (e.g. core `1.16.2` → skills `1.16.2-beta26`). Don't pair mismatched versions.
- API:
  - `Skills.from(FileSystemSkillLoader.loadSkills(Path.of("skills")))` (or
    `ClassPathSkillLoader`).
  - `skills.toolProvider()` → the `ToolProvider` to pass to `.toolProvider(...)`.
  - `skills.formatAvailableSkills()` → catalog XML for the system message.
- ⚠️ `Skill` is an **interface** — there is **no `@Skill` annotation** and **no
  `AiServices.skills(...)`** method. Register via `.toolProvider(
  skills.toolProvider())`.
- Auto-generated meta-tools: `activate_skill` (loads a skill body into context)
  and `read_skill_resource` (loads a bundled resource on demand) — this is the
  progressive-disclosure mechanism (Surface-budget test, strategy 4).

---

## 9. Provider note — a flagged example, not a directive

This skill is **provider-agnostic**. The *tool* APIs above (`@Tool`, `@P`,
`@ToolMemoryId`, `ToolProvider`, guardrails, listeners) are provider-neutral.

But **provider choice changes the surrounding API surface**, which is exactly why
Step 0 re-grounds against the project's actual setup. One concrete example:
prompt caching is configured differently per provider — on AWS Bedrock through
`BedrockChatRequestParameters.promptCaching(...)` with a `CacheTTL` such as
`VALUE_5_M`, whereas `langchain4j-anthropic`'s `cacheSystemMessages(true)` is a
**no-op on Bedrock**. Do **not** read this as "use Bedrock" — read it as "confirm
the provider, then use that provider's names." Detect the project's provider and
ground accordingly.
