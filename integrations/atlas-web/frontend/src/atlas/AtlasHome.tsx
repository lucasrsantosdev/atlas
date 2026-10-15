import { useEffect, useRef, useState } from "react";
import { AtlasBrand } from "./components/layout/AtlasBrand";
import { AtlasCoreStatus } from "./components/status/AtlasCoreStatus";
import { atlasApi } from "./services/atlasApi";
import "./theme/atlas.css";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

function obj(value: unknown): Record<string, any> {
  return value && typeof value === "object"
    ? value as Record<string, any>
    : {};
}

function parseAnswer(value: unknown): string | null {
  const data = obj(value);

  for (const key of ["response", "answer", "reply", "output", "content"]) {
    if (typeof data[key] === "string") {
      return data[key];
    }
  }

  for (const key of ["message", "response", "assistant_message"]) {
    const nested = obj(data[key]);

    if (typeof nested.content === "string") {
      return nested.content;
    }
  }

  return null;
}

function parseHistory(value: unknown): Message[] {
  const data = obj(value);
  const items = Array.isArray(value)
    ? value
    : Array.isArray(data.messages)
      ? data.messages
      : [];

  return items.flatMap((item: unknown) => {
    const entry = obj(item);

    if (
      !["user", "assistant"].includes(entry.role) ||
      typeof entry.content !== "string"
    ) {
      return [];
    }

    return [{
      id: String(entry.id || crypto.randomUUID()),
      role: entry.role as "user" | "assistant",
      content: entry.content as string
    }];
  });
}

export function AtlasHome() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const running = useRef(false);
  const bottom = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function send(text?: string) {
    const content = (text ?? input).trim();

    if (!content || running.current) return;

    running.current = true;
    setBusy(true);
    setError("");

    let id = conversationId;
    let submitted = false;

    try {
      const health = obj(await atlasApi.health());

      if (
        health.name !== "Atlas" ||
        health.core !== "atlas.core.app.Atlas"
      ) {
        throw new Error("Atlas Core oficial nao identificado.");
      }

      if (!id) {
        const created = obj(await atlasApi.createConversation({
          title: content.slice(0, 60)
        }));

        id = created.id ?? created.conversation_id;

        if (typeof id !== "string" || !id) {
          throw new Error("API nao retornou identificador de conversa.");
        }

        setConversationId(id);
      }

      setInput("");
      setMessages(previous => [
        ...previous,
        {
          id: crypto.randomUUID(),
          role: "user",
          content
        }
      ]);

      submitted = true;

      const response = await atlasApi.chat(id, content);
      let answer = parseAnswer(response);

      if (!answer) {
        const history = parseHistory(await atlasApi.messages(id));
        answer = [...history].reverse()
          .find(item => item.role === "assistant")?.content ?? null;
      }

      if (!answer) {
        throw new Error(
          "Nao foi possivel interpretar a resposta da API."
        );
      }

      setMessages(previous => [
        ...previous,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: answer!
        }
      ]);

    } catch (failure) {
      const message = failure instanceof Error
        ? failure.message
        : String(failure);

      setError(
        submitted
          ? message + " Verifique o historico antes de reenviar."
          : message
      );
    } finally {
      running.current = false;
      setBusy(false);
    }
  }

  function newChat() {
    if (running.current) return;

    setConversationId(null);
    setMessages([]);
    setInput("");
    setError("");
  }

  return (
    <main className="atlas-app">
      <aside className="atlas-sidebar">
        <AtlasBrand />

        <nav className="atlas-navigation">
          <button
            className="active"
            onClick={newChat}
            disabled={busy}
          >
            + Nova conversa
          </button>

          <button disabled>Estudos (em breve)</button>
          <button disabled>Projetos (em breve)</button>
          <button disabled>Memória (em breve)</button>
          <button disabled>Conhecimento (em breve)</button>
        </nav>

        <div className="atlas-sidebar-footer">
          <AtlasCoreStatus />
        </div>
      </aside>

      <section className="atlas-main">
        <header className="atlas-header">
          <div>
            <span className="atlas-eyebrow">
              ATLAS EDUCACIONAL
            </span>
            <h1>Olá. Eu sou o Atlas.</h1>
            <p>
              Inteligência ao seu lado para aprender,
              criar, pesquisar e construir.
            </p>
          </div>
        </header>

        <section
          className="atlas-workspace"
          aria-label="Chat do Atlas"
          style={{
            display: "block",
            flex: 1,
            minHeight: 0,
            overflowY: "auto"
          }}
        >
          {messages.length === 0 ? (
            <div
              className="atlas-welcome"
              style={{ margin: "auto" }}
            >
              <div className="atlas-orb-large">A</div>

              <h2>Como posso ajudar hoje?</h2>

              <p>
                Converse com o Atlas Core e seu modelo local.
              </p>

              <div className="atlas-suggestions">
                {[
                  "Quem é você?",
                  "Explique inteligência artificial",
                  "Quero estudar matemática",
                  "Como aprender Python?"
                ].map(item => (
                  <button
                    key={item}
                    disabled={busy}
                    onClick={() => void send(item)}
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div style={{
              width: "min(850px, 100%)",
              margin: "0 auto",
              display: "flex",
              flexDirection: "column",
              gap: 16
            }}>
              {messages.map(message => (
                <article
                  key={message.id}
                  style={{
                    alignSelf: message.role === "user"
                      ? "flex-end"
                      : "flex-start",
                    maxWidth: "90%",
                    background: message.role === "user"
                      ? "rgba(37,107,217,.24)"
                      : "rgba(255,255,255,.05)",
                    border: "1px solid rgba(255,255,255,.1)",
                    borderRadius: 15,
                    padding: "15px 18px",
                    overflowWrap: "anywhere"
                  }}
                >
                  <strong>
                    {message.role === "user" ? "Você" : "Atlas"}
                  </strong>
                  <div style={{
                    marginTop: 8,
                    whiteSpace: "pre-wrap",
                    lineHeight: 1.6
                  }}>
                    {message.content}
                  </div>
                </article>
              ))}

              {busy && <p role="status">Atlas está pensando...</p>}
              <div ref={bottom} />
            </div>
          )}
        </section>

        <footer className="atlas-input-area">
          {error && (
            <p role="alert" style={{
              color: "#ff9191",
              maxWidth: 850,
              margin: "0 auto 12px",
              overflowWrap: "anywhere"
            }}>
              {error}
            </p>
          )}

          <form
            className="atlas-input"
            onSubmit={event => {
              event.preventDefault();
              void send();
            }}
          >
            <textarea
              aria-label="Mensagem para Atlas"
              placeholder="Converse com o Atlas..."
              value={input}
              disabled={busy}
              rows={2}
              onChange={event => setInput(event.target.value)}
              onKeyDown={event => {
                if (
                  event.key === "Enter" &&
                  !event.shiftKey &&
                  !event.nativeEvent.isComposing
                ) {
                  event.preventDefault();
                  void send();
                }
              }}
            />

            <button
              type="submit"
              disabled={busy || !input.trim()}
            >
              {busy ? "Aguarde..." : "Enviar"}
            </button>
          </form>

          <small>
            ATLAS.IA • Atlas Core oficial • Modelo local
          </small>
        </footer>
      </section>
    </main>
  );
}