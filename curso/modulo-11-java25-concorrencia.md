# Módulo 11 — Java 25 para chamadas de tool em paralelo

> **Rascunho-fonte da Lição 13** (`lessons/0013-java25-concorrencia.html`). Aterrado em
> openjdk.org (JEPs 444/505/506) + fonte LangChain4j 1.16.2 + Micronaut 5.

O banco consulta a **conta nacional** e a **conta global** em **backends distintos**. Buscar
as duas em **paralelo** corta latência — e o Java 25 + LangChain4j dão o caminho GA-seguro.

## 1 · O status REAL dos recursos do Java 25 (corrige o mito)

| Recurso | Status no Java 25 | Flag? |
| --- | --- | --- |
| **Virtual Threads** | **Final desde o JDK 21** (JEP 444); permanente no 25 LTS | não |
| **Scoped Values** | **Final no JDK 25** (JEP 506) — `orElse` não aceita mais `null` | não |
| **Structured Concurrency** | **Ainda PREVIEW** (JEP 505, *quinto preview*) | **sim** (`--enable-preview`) |

⚠️ Não diga "Virtual Threads finalizadas no 25" — final no **21**. E a `StructuredTaskScope`
no JDK 25 **mudou**: agora é aberta por **fábricas estáticas** `StructuredTaskScope.open()` /
`open(Joiner)` — código de previews 21–24 (`new StructuredTaskScope<>()`, `ShutdownOnFailure`)
**não compila** no 25.

## 2 · O default do LangChain4j é SEQUENCIAL (o fato-chave)

`AiServices` executa múltiplas tools de um turno **sequencialmente** por padrão (verificado:
`ToolService.execute` → `executeSequentially` quando `executor == null`). Para paralelizar,
**opt-in**:

```java
AiServices.builder(...).executeToolsConcurrently(executor)   // @since 1.4.0
```

- Concorre **apenas** quando o turno tem **&gt;1 tool call** **e** há executor (`if (executor != null && toolRequests.size() > 1)`).
- Para um `ChatModel` **síncrono** (como o `BedrockChatModel`), **uma única** tool roda na
  **thread chamadora** (executor é ignorado, de propósito). `StreamingChatModel` difere
  (até uma tool roda em thread separada).

## 3 · Virtual threads por baixo (o fit para I/O)

O executor **default** do `executeToolsConcurrently()` é um **singleton lazy de
virtual-thread-per-task** (`DefaultExecutorProvider`, padrão Holder; `VirtualThreadUtils` →
`Executors.newVirtualThreadPerTaskExecutor()` por reflexão em Java 21+). Fan-out de backends
bancários é **I/O-bound** → virtual threads são o encaixe perfeito (uma por tarefa; **não
faça pool**).

**Em produção, deixe o Micronaut dono do executor:** injete `@Named(TaskExecutors.VIRTUAL)
ExecutorService` (constante `"virtual"`) e passe a `executeToolsConcurrently(executor)`; rode a
chamada bloqueante fora do event loop com `@ExecuteOn(TaskExecutors.VIRTUAL)`.

## 4 · Scoped Values: contexto do cliente nas subtasks (final no 25)

`ScopedValue` (JEP 506, **GA no 25**) carrega identidade/escopo do request para as subtasks
forkadas — sem passar parâmetro por toda a cadeia, e **imutável** (mais seguro que
`ThreadLocal` em virtual threads). Ideal para levar "cliente X, escopo nacional/global" às
chamadas de tool concorrentes.

```java
public static final ScopedValue<String> CUSTOMER_ID = ScopedValue.newInstance();
// ...
ScopedValue.where(CUSTOMER_ID, customerId).call(() -> assistant.chat(prompt));
```

## 5 · Structured Concurrency: "para onde vai" (preview)

`StructuredTaskScope` (JEP 505, **preview no 25**) trataria as buscas nacional+global como
**uma unidade** (uma falha cancela as irmãs; join estruturado). Mas é **preview** →
`--enable-preview`. **Não ensine como GA.** O primitivo GA-seguro para o fan-out do banco é o
`executeToolsConcurrently()` (que já usa virtual threads por baixo).

```java
// PREVIEW (javac --release 25 --enable-preview; java --enable-preview) — JDK 25 usa open()/open(Joiner):
// try (var scope = StructuredTaskScope.open(/* Joiner */)) {
//     var nac = scope.fork(() -> nacional.saldo());
//     var glb = scope.fork(() -> global.saldo());
//     scope.join();
//     return combina(nac.get(), glb.get());
// }
```

## 6 · A fronteira: concorrência ≠ segurança transacional

`★ Insight ─────────────────────────────────────`
**Paralelizar é otimização de latência, NÃO de transação.** Habilitar
`executeToolsConcurrently()` é seguro para **fan-out de LEITURA** (saldos/extratos nacional +
global em paralelo). Operações que **movem dinheiro** continuam exigindo **idempotência +
confirmação** (Lição 12/14), rode qual executor rodar. Concorrência **não** dá atomicidade.
`─────────────────────────────────────────────────`

## Quiz

1. **Por padrão, o LangChain4j 1.16.2 executa múltiplas tools de um turno como?**
   (a) em paralelo, usando virtual threads automaticamente · (b) ✅ **sequencialmente**; o
   paralelo é opt-in (`executeToolsConcurrently`) · (c) em paralelo só se o modelo for streaming
2. **No Java 25, qual recurso ainda é preview (precisa de `--enable-preview`)?**
   (a) Virtual Threads, finalizadas só agora · (b) Scoped Values, que ainda exigem a flag ·
   (c) ✅ **Structured Concurrency** (JEP 505, quinto preview)
3. **Dá para paralelizar uma transferência de dinheiro com `executeToolsConcurrently`?**
   (a) ✅ não como segurança: paralelismo é latência, não transação · (b) sim: o executor garante
   atomicidade · (c) sim, com structured concurrency e `--enable-preview`

## Vá mais fundo

- **JEPs:** https://openjdk.org/jeps/444 (VT), https://openjdk.org/jeps/506 (Scoped Values),
  https://openjdk.org/jeps/505 (Structured Concurrency — preview).
- Fonte LangChain4j 1.16.2: `AiServices.executeToolsConcurrently`, `ToolService.execute`,
  `DefaultExecutorProvider`/`VirtualThreadUtils`. Micronaut: `TaskExecutors.VIRTUAL`, `@ExecuteOn`.
- **Aberto:** API exata de `StructuredTaskScope.open(Joiner)` no JDK 25 (nomes dos Joiners) e a
  injeção `@Named(VIRTUAL)` neste combo — confirmar antes de copiar.
- **Próximo (Lição 14):** arquitetura multi-backend do banco (agêntica, idempotência, human-in-the-loop).
