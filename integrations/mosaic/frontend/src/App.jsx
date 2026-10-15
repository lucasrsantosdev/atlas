import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { api } from "./api";

function Icon({ name, size = 18 }) {
  const paths = {
    home:<><path d="m3 9 9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M9 20v-6h6v6"/></>,
    plus:<><path d="M12 5v14M5 12h14"/></>,
    search:<><circle cx="11" cy="11" r="6.5"/><path d="m16 16 5 5"/></>,
    settings:<><circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6 7 7M17 17l1.4 1.4M18.4 5.6 17 7M7 17l-1.4-1.4"/></>,
    help:<><circle cx="12" cy="12" r="9"/><path d="M9.8 9a2.4 2.4 0 1 1 4.1 1.7c-.9.9-1.9 1.3-1.9 2.8M12 17h.01"/></>,
    file:<><path d="M6 3h8l4 4v14H6z"/><path d="M14 3v5h5"/></>,
    folder:<path d="M3 6h7l2 2h9v10H3z"/>,
    check:<><circle cx="12" cy="12" r="8.5"/><path d="m8.5 12 2.3 2.3 4.7-5"/></>,
    memory:<><path d="M5 5h14v14H5z"/><path d="M8 9h8M8 13h6M8 17h4"/></>,
    tool:<><path d="m14.5 6.5 3-3 3 3-3 3"/><path d="M17.5 6.5 11 13l-3 3-4 1 1-4 3-3 6.5-6.5"/></>,
    note:<><path d="M5 3h11l3 3v15H5z"/><path d="M16 3v4h4M8 11h8M8 15h8"/></>,
    globe:<><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18"/></>,
    book:<><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21z"/><path d="M4 5.5v15M8 7h8M8 11h7"/></>,
    at:<><circle cx="12" cy="12" r="4"/><path d="M16 12v1a2 2 0 0 0 4 0v-1a8 8 0 1 0-2.3 5.7"/></>,
    send:<><path d="m4 4 16 8-16 8 3-8z"/><path d="M7 12h13"/></>,
    chevron:<path d="m8 10 4 4 4-4"/>,
    box:<><path d="m12 3 8 4.5v9L12 21l-8-4.5v-9z"/><path d="m4 7.5 8 4.5 8-4.5M12 12v9"/></>,
    layers:<><path d="m12 3 9 5-9 5-9-5zM3 12l9 5 9-5M3 16l9 5 9-5"/></>,
    history:<><path d="M4 12a8 8 0 1 0 2.3-5.7L4 8.5"/><path d="M4 4v4.5h4.5M12 7v5l3 2"/></>,
    cube:<><path d="m12 3 8 4.5v9L12 21l-8-4.5v-9z"/><path d="m4 7.5 8 4.5 8-4.5M12 12v9"/></>,
    guitar:<><path d="M14.5 5.5 18 2l1 1-3.5 3.5"/><path d="m14 7 3 3"/><path d="M15.5 9.5c1.3 1.3 1.2 3.4-.1 4.7l-2.1 2.1a3.4 3.4 0 0 1-4.8-4.8l2.1-2.1c1.3-1.3 3.4-1.4 4.7-.1z"/><path d="m9 15-4 4"/></>,
    car:<><path d="M5 16h14l-1-6H6z"/><path d="M3 16h2v3h2v-3h10v3h2v-3h2"/><circle cx="7.5" cy="16" r="1"/><circle cx="16.5" cy="16" r="1"/></>,
    menu:<><path d="M4 7h16M4 12h16M4 17h16"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] || paths.box}</svg>;
}

function AtlasMark({ compact=false }) {
  return <div className={compact ? "mosaic-mark compact" : "mosaic-mark"} aria-hidden="true"><svg viewBox="0 0 80 80" fill="none"><path d="M40 4 68 20v32L40 68 12 52V20z" stroke="currentColor" strokeWidth="2"/><path d="m40 4 14 8v16L40 36 26 28V12z" fill="currentColor" opacity=".82"/><path d="m26 28 14 8v16l-14 8-14-8V36z" fill="currentColor" opacity=".45"/><path d="m54 28 14-8v32l-14 8z" fill="currentColor" opacity=".25"/><path d="m40 36 14-8v16l-14 8z" fill="currentColor" opacity=".9"/></svg></div>;
}
const iconType = n => /guitar/i.test(n || "") ? "guitar" : /car/i.test(n || "") ? "car" : "cube";
const slugify = v => v.toLowerCase().trim().replace(/[^a-z0-9]+/gi,"-").replace(/^-|-$/g,"") || "project";
const groupFor = d => { const n=d ? Math.floor((Date.now()-new Date(d).getTime())/86400000) : 0; return n<1?"Hoje":n<2?"Ontem":"Últimos 7 dias"; };

function Sidebar({ projects, conversations, activeProjectId, activeConversationId, onProject, onConversation, onNewProject, onNewConversation, onModelSettings, onHelp, onHome, mobileOpen, onClose }) {
  const [expandedProjectIds, setExpandedProjectIds] = useState([]);
  const conversationsByProject = useMemo(() => {
    const map = new Map();
    conversations.forEach(c => {
      if (!map.has(c.project_id)) map.set(c.project_id, []);
      map.get(c.project_id).push(c);
    });
    return map;
  }, [conversations]);

  return <aside className={mobileOpen ? "sidebar open" : "sidebar"}>
    <div className="brand-row"><AtlasMark/><span className="wordmark">ATLAS.IA</span><button className="mobile-close" onClick={onClose}>×</button></div>
    <button className="new-chat" onClick={onNewConversation}><Icon name="plus" size={19}/>Nova conversa</button>
    <nav className="side-primary">
      <button onClick={onHome}><Icon name="home"/>Início</button>
      <div className="section-heading"><span>Projetos</span><button className="icon-inline" onClick={onNewProject}><Icon name="plus" size={16}/></button></div>
      <div className="project-tree">
        {projects.map(p => {
          const projectConversations = conversationsByProject.get(p.id) || [];
          const expanded = expandedProjectIds.includes(p.id);
          const active = p.id === activeProjectId;
          return <div className={expanded ? "project-node expanded" : "project-node"} key={p.id}>
            <div className="project-row">
              <button onClick={()=>onProject(p.id)} className={active ? "side-project active" : "side-project"}>
                <span className="project-icon"><Icon name={iconType(p.name)} size={18}/></span>
                <span className="project-name">{p.name}</span>
                <span className="project-count">{projectConversations.length}</span>
              </button>
              <button
                type="button"
                className={expanded ? "project-expand expanded" : "project-expand"}
                onClick={()=>setExpandedProjectIds(ids => expanded ? ids.filter(id => id !== p.id) : [...ids, p.id])}
                aria-label={expanded ? `Recolher conversas de ${p.name}` : `Expandir conversas de ${p.name}`}
                aria-expanded={expanded}
                title={expanded ? "Recolher conversas" : "Expandir conversas"}
              ><Icon name="chevron" size={15}/></button>
            </div>
            {expanded && <div className="project-conversation-list">
              {projectConversations.length
                ? projectConversations.map(c => <button key={c.id} onClick={()=>onConversation(c.id)} className={c.id===activeConversationId ? "conversation-item selected" : "conversation-item"}>
                    <span className="tiny-chevron">›</span>
                    <span className="conversation-title">{c.title || "Nova conversa"}</span>
                  </button>)
                : <span className="sidebar-empty">Nenhuma conversa neste projeto.</span>}
            </div>}
          </div>;
        })}
      </div>
      <button className="new-project" onClick={onNewProject}><Icon name="plus" size={17}/>Novo projeto</button>
    </nav>
    <div className="side-bottom"><button onClick={onModelSettings}><Icon name="settings"/>Configurações</button><button onClick={onHelp}><Icon name="help"/>Ajuda</button></div>
  </aside>;
}

function TopBar({ onMenu, onFiles, project, conversation, models, onModelChange, modelStatus, onModelSettings, onContext }) {
  const selectedModel=models.find(m=>m.id===conversation?.model_id);
  const running=selectedModel?.provider === "ollama" && modelStatus.running_models.includes(selectedModel.model_name);
  const statusLabel=!selectedModel ? "Nenhum modelo" : !modelStatus.online ? "Offline" : running ? "Rodando" : "Disponível";
  const statusClass=!selectedModel ? "offline" : !modelStatus.online ? "offline" : running ? "running" : "online";
  return <header className="topbar"><button className="mobile-menu" onClick={onMenu}><Icon name="menu"/></button><button className="workspace-file" onClick={onFiles} aria-label="Abrir arquivos do projeto" title="Arquivos do projeto"><Icon name="file"/></button>
    <div className="top-project"><span className="top-project-icon"><span className="project-icon"><Icon name={iconType(project?.name)} size={18}/></span></span><div><strong>{project?.name || "Atlas"}</strong><small>Development Project</small></div><Icon name="chevron" size={15}/></div>
    <div className="top-actions"><div className="model-picker"><select className="model-select" value={conversation?.model_id ?? ""} disabled={!conversation || !models.length} onChange={e=>onModelChange(Number(e.target.value))}><option value="">{conversation ? (models.length ? "Selecionar modelo" : "Nenhum modelo") : "Nenhuma conversa"}</option>{models.filter(m=>m.enabled || m.id===conversation?.model_id).map(m=><option key={m.id} value={m.id} disabled={!m.enabled}>{m.name}</option>)}</select><span className="model-provider">{selectedModel?.provider || ""}</span><span className={"model-status "+statusClass}><i/>{statusLabel}</span><button className="model-config-button" onClick={onModelSettings} disabled={!selectedModel}>Configurar</button></div><span className="top-divider"/><button className="top-link" onClick={()=>onContext("Contexto")}><Icon name="layers" size={16}/>Contexto</button><button className="top-link" onClick={()=>onContext("Memória")}><Icon name="memory" size={16}/>Memória</button><button className="top-link" onClick={()=>onContext("Arquivos")}><Icon name="tool" size={16}/>Ferramentas</button><span className="avatar">JD</span></div>
  </header>;
}

function ProjectHeader({ project, tab, setTab }) {
  const tabs=[["note","Conversa"],["folder","Arquivos"],["check","Tarefas"],["memory","Memória"],["tool","Artefatos"],["settings","Agente"],["note","Notas"]];
  return <section className="project-header"><div className="project-identity"><AtlasMark compact/><div><h1>{project?.name || "Atlas"}</h1><p>{project?.description || "Workspace de desenvolvimento do Atlas."}</p></div></div><nav className="project-tabs">{tabs.map(([i,l])=><button key={l} className={tab===l?"active":""} onClick={()=>setTab(l)}><Icon name={i} size={16}/><span>{l}</span></button>)}</nav></section>;
}

function renderInline(text) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)/g).filter(Boolean);
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) return <strong key={index}>{part.slice(2, -2)}</strong>;
    if (part.startsWith("`") && part.endsWith("`")) return <code key={index}>{part.slice(1, -1)}</code>;
    if (part.startsWith("*") && part.endsWith("*")) return <em key={index}>{part.slice(1, -1)}</em>;
    return part;
  });
}

function FormattedResponse({ content }) {
  const lines = String(content || "").replace(/\r\n/g, "\n").split("\n");
  const blocks = [];
  let paragraph = [];
  let list = [];
  let listType = "";
  let code = [];
  let inCode = false;

  const flushParagraph = () => {
    if (paragraph.length) {
      blocks.push(<p key={blocks.length}>{renderInline(paragraph.join(" "))}</p>);
      paragraph = [];
    }
  };
  const flushList = () => {
    if (list.length) {
      const Items = listType === "ordered" ? "ol" : "ul";
      blocks.push(<Items key={blocks.length}>{list.map((item, index) => <li key={index}>{renderInline(item)}</li>)}</Items>);
      list = [];
      listType = "";
    }
  };

  lines.forEach((line) => {
    const trimmed = line.trim();
    if (trimmed.startsWith("```")) {
      flushParagraph();
      flushList();
      if (inCode) {
        blocks.push(<pre key={blocks.length}><code>{code.join("\n")}</code></pre>);
        code = [];
      }
      inCode = !inCode;
      return;
    }
    if (inCode) {
      code.push(line);
      return;
    }
    if (!trimmed) {
      flushParagraph();
      flushList();
      return;
    }
    const heading = trimmed.match(/^(#{1,3})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const level = heading[1].length;
      const text = heading[2];
      if (level === 1) blocks.push(<h2 key={blocks.length}>{renderInline(text)}</h2>);
      else if (level === 2) blocks.push(<h3 key={blocks.length}>{renderInline(text)}</h3>);
      else blocks.push(<h4 key={blocks.length}>{renderInline(text)}</h4>);
      return;
    }
    const bullet = trimmed.match(/^[-*+]\s+(.+)$/);
    const numbered = trimmed.match(/^\d+[.)]\s+(.+)$/);
    if (bullet || numbered) {
      flushParagraph();
      const nextType = numbered ? "ordered" : "unordered";
      if (list.length && listType !== nextType) flushList();
      listType = nextType;
      list.push((bullet || numbered)[1]);
      return;
    }
    flushList();
    paragraph.push(trimmed);
  });
  flushParagraph();
  flushList();
  if (inCode && code.length) blocks.push(<pre key={blocks.length}><code>{code.join("\n")}</code></pre>);
  return <div className="formatted-response">{blocks}</div>;
}

function MessageList({ messages, streaming }) {
  if (!messages.length && !streaming) {
    return <div className="conversation-empty"><AtlasMark compact/><h2>Conversa pronta</h2><p>Envie uma mensagem para começar a conversar com o modelo selecionado.</p></div>;
  }

  return <div className="chat-content">
    {messages.map(message => message.role === "user"
      ? <div className="message user-message" key={message.id || message.localId}>
          <div className="message-bubble"><p>{message.content}</p><time>{new Date(message.created_at || Date.now()).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"})}</time></div>
          <div className="message-avatar user">JD</div>
        </div>
      : <div className="message assistant-message" key={message.id || message.localId}>
          <div className="message-avatar mosaic"><AtlasMark compact/></div>
          <div className={message.content ? "assistant-copy" : "assistant-copy assistant-empty"}>
            {message.content ? <FormattedResponse content={message.content}/> : <p>{streaming ? "Gerando resposta…" : "O Atlas recebeu a mensagem, mas o modelo não retornou conteúdo."}</p>}
            {message.content && <time className="message-time">{new Date(message.created_at || Date.now()).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"})}</time>}
          </div>
        </div>
    )}
  </div>;
}

function Composer({ disabled, onSubmit, model, onFiles, onAgent }) {
  const [text,setText]=useState("");
  const submit=e=>{e.preventDefault();if(!text.trim()||disabled)return;onSubmit(text.trim());setText("");};
  return <form className="composer" onSubmit={submit}><textarea disabled={disabled} value={text} onChange={e=>setText(e.target.value)} placeholder={disabled?"Selecione uma conversa para começar...":"Digite sua mensagem..."} rows="2" onKeyDown={e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();submit(e);}}}/><div className="composer-toolbar"><div className="composer-tools"><button type="button" disabled={disabled} onClick={onFiles} aria-label="Explorar arquivos do projeto" title="Arquivos do projeto"><Icon name="plus"/></button><button type="button" disabled={disabled} onClick={onAgent} aria-label="Configurar instruções do agente" title="Instruções e skills do agente"><Icon name="book"/></button></div><div className="composer-submit"><span className="composer-model">{model?.name || "Modelo"}</span><button className="send-button" type="submit" disabled={disabled}><Icon name="send" size={19}/></button></div></div></form>;
}


const TASK_STATUS_LABELS = {
  pending: "Na fila",
  planning: "Planejando",
  executing: "Executando",
  awaiting_approval: "Aguardando aprovação",
  validating: "Validando",
  completed: "Concluída",
  failed: "Falhou",
  cancelled: "Cancelada",
};

function TaskWorkspace({ conversationId, projectId }) {
  const [tasks, setTasks] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [events, setEvents] = useState([]);
  const [toolCalls, setToolCalls] = useState([]);
  const [connectionState, setConnectionState] = useState("connecting");
  const [goal, setGoal] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function refreshTasks(preferId = null) {
    if (!conversationId) { setTasks([]); setSelectedId(null); setLoading(false); return; }
    try {
      const data = await api.tasks.list();
      const scoped = data.filter(task => task.conversation_id === conversationId);
      setTasks(scoped);
      setSelectedId(current => {
        const preferred = preferId ?? current;
        return scoped.some(task => task.id === preferred)
          ? preferred
          : (scoped[scoped.length - 1]?.id ?? null);
      });
      setError("");
    } catch (err) {
      setError("Não foi possível carregar as tarefas: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let active = true;
    setLoading(true);
    setEvents([]);
    setToolCalls([]);
    setTasks([]);
    setSelectedId(null);
    (async () => {
      if (!conversationId) { if (active) setLoading(false); return; }
      try {
        const data = await api.tasks.list();
        if (!active) return;
        const scoped = data.filter(task => task.conversation_id === conversationId);
        setTasks(scoped);
        setSelectedId(scoped[scoped.length - 1]?.id ?? null);
        setError("");
      } catch (err) {
        if (active) setError("Não foi possível carregar as tarefas: " + err.message);
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, [conversationId]);

  useEffect(() => {
    if (!selectedId) { setEvents([]); return undefined; }
    let active = true;
    const refresh = async () => {
      try {
        const [task, nextEvents, nextToolCalls] = await Promise.all([
          api.tasks.get(selectedId),
          api.tasks.events(selectedId, 0),
          api.toolCalls.list(conversationId, selectedId),
        ]);
        if (!active) return;
        setTasks(items => {
          const rest = items.filter(item => item.id !== task.id);
          return [...rest, task].sort((a, b) => a.id - b.id);
        });
        setEvents(nextEvents);
        setToolCalls(nextToolCalls);
      } catch (err) {
        if (active) setError("Não foi possível atualizar a execução: " + err.message);
      }
    };
    refresh();
    const timer = setInterval(refresh, 2500);
    return () => { active = false; clearInterval(timer); };
  }, [selectedId, conversationId]);

  useEffect(() => {
    if (!selectedId) return undefined;
    let active = true;
    const source = api.tasks.streamEvents(selectedId, 0, event => {
      if (!active) return;
      setEvents(current => current.some(item => item.id === event.id) ? current : [...current, event].sort((a, b) => a.id - b.id));
    }, state => { if (active) setConnectionState(state); });
    return () => { active = false; source.close(); };
  }, [selectedId]);

  async function decideCall(callId, decision) {
    if (!selectedId || busy) return;
    setBusy(true);
    setError("");
    try {
      await api.tasks.decideToolCall(selectedId, callId, decision);
      const [task, calls, nextEvents] = await Promise.all([
        api.tasks.get(selectedId),
        api.toolCalls.list(conversationId, selectedId),
        api.tasks.events(selectedId, 0),
      ]);
      setTasks(items => items.map(item => item.id === task.id ? task : item));
      setToolCalls(calls);
      setEvents(nextEvents);
    } catch (err) {
      setError("Não foi possível registrar sua decisão: " + err.message);
    } finally {
      setBusy(false);
    }
  }

  async function startTask(event) {
    event.preventDefault();
    const trimmed = goal.trim();
    if (!trimmed || !conversationId || busy) return;
    setBusy(true);
    setError("");
    try {
      const task = await api.tasks.start({ conversation_id: conversationId, project_id: projectId, goal: trimmed, type: "generic" });
      setGoal("");
      await refreshTasks(task.id);
      setSelectedId(task.id);
    } catch (err) {
      setError("Não foi possível iniciar a tarefa: " + err.message);
    } finally {
      setBusy(false);
    }
  }

  async function cancelTask() {
    if (!selectedId || busy) return;
    setBusy(true);
    setError("");
    try {
      const updated = await api.tasks.cancel(selectedId);
      setTasks(items => items.map(task => task.id === updated.id ? updated : task));
    } catch (err) {
      setError("Não foi possível cancelar a tarefa: " + err.message);
    } finally {
      setBusy(false);
    }
  }

  const selected = tasks.find(task => task.id === selectedId) || null;
  const active = selected && ["pending", "planning", "executing", "awaiting_approval", "validating"].includes(selected.status);

  return <section className="task-workspace">
    <div className="task-workspace-heading">
      <div><span className="eyebrow">EXECUÇÃO AGÊNTICA</span><h2>Tarefas</h2><p>Peça ao Atlas para executar um objetivo e acompanhe o estado persistido pelo Core.</p></div>
      <span className="task-count">{tasks.length} {tasks.length === 1 ? "tarefa" : "tarefas"}</span>
    </div>
    {!conversationId
      ? <div className="task-empty"><Icon name="tool" size={25}/><strong>Selecione uma conversa</strong><span>As tarefas ficam vinculadas à conversa e ao projeto ativos.</span></div>
      : <form className="task-start-form" onSubmit={startTask}>
          <label htmlFor="agent-task-goal">O que você quer que o Atlas faça?</label>
          <textarea id="agent-task-goal" value={goal} onChange={event => setGoal(event.target.value)} rows={3} maxLength={8000} placeholder="Ex.: Analise a estrutura deste projeto e identifique os próximos passos." disabled={busy}/>
          <div className="task-start-footer"><span>Execução real · o Core controla ferramentas e permissões</span><button type="submit" className="primary-action" disabled={busy || !goal.trim()}><Icon name="send" size={15}/>{busy ? "Enviando…" : "Executar tarefa"}</button></div>
        </form>}
    {error && <div className="task-inline-error" role="alert">{error}</div>}
    <div className="task-layout">
      <section className="task-list-panel"><div className="task-panel-heading"><strong>Histórico de tarefas</strong><button type="button" onClick={() => refreshTasks()} aria-label="Atualizar tarefas" title="Atualizar">↻</button></div>
        {loading ? <div className="task-muted">Carregando tarefas…</div> : !tasks.length ? <div className="task-muted">Nenhuma tarefa nesta conversa.</div> : <div className="task-list">{[...tasks].reverse().map(task => <button type="button" key={task.id} className={selectedId === task.id ? "task-list-item selected" : "task-list-item"} onClick={() => setSelectedId(task.id)}><span className={"task-status-dot status-" + task.status}/><span className="task-list-copy"><strong>{task.plan?.goal || ("Tarefa #" + task.id)}</strong><small>#{task.id} · {new Date(task.updated_at).toLocaleString("pt-BR", {dateStyle:"short",timeStyle:"short"})}</small></span><span className={"task-status status-" + task.status}>{TASK_STATUS_LABELS[task.status] || task.status}</span></button>)}</div>}
      </section>
      <section className="task-detail-panel">
        {!selected ? <div className="task-empty compact"><Icon name="layers" size={23}/><strong>Selecione uma tarefa</strong><span>O estado, a linha do tempo e o resultado aparecerão aqui.</span></div> : <>
          <div className="task-detail-heading"><div><span className="task-id">TAREFA #{selected.id}</span><h3>{selected.plan?.goal || "Execução do Atlas"}</h3></div><span className={"task-status status-" + selected.status}>{TASK_STATUS_LABELS[selected.status] || selected.status}</span></div>
          <div className="task-progress-meta"><span>Estado atual</span><strong>{TASK_STATUS_LABELS[selected.status] || selected.status}</strong></div>
          {active && selected.status !== "awaiting_approval" && <div className="task-progress-track"><span/></div>}
          {selected.status === "awaiting_approval" && <div className="approval-stack"><div className="task-notice"><Icon name="check" size={17}/>O Atlas precisa da sua autorização antes de executar esta operação.</div>{toolCalls.filter(call => call.status === "pending").map(call => <article className="approval-card" key={call.id}><span className="eyebrow">AÇÃO #{call.id} · AGUARDANDO</span><h4>Permitir {call.tool_name}?</h4><p>O agente solicitou esta ferramenta. Revise os argumentos antes de autorizar a execução.</p><details><summary>Ver operação e argumentos</summary><pre>{JSON.stringify(call.arguments, null, 2)}</pre></details><div className="approval-actions"><button type="button" className="danger-action" disabled={busy} onClick={() => decideCall(call.id, "reject")}>Recusar</button><button type="button" className="primary-action" disabled={busy} onClick={() => decideCall(call.id, "approve")}>{busy ? "Registrando…" : "Aprovar e continuar"}</button></div></article>)}</div>}
          <div className="task-timeline-heading"><strong>Linha do tempo</strong><span>{events.length} eventos · {connectionState === "connected" ? "ao vivo" : connectionState === "reconnecting" ? "reconectando" : "conectando"}</span></div>
          {!events.length ? <div className="task-muted">Aguardando eventos do Core…</div> : <ol className="task-timeline">{events.map(event => <li key={event.id}><span className={"timeline-marker level-" + event.level}/><div><div className="timeline-event-head"><strong>{event.message}</strong><time>{new Date(event.timestamp).toLocaleTimeString("pt-BR", {hour:"2-digit",minute:"2-digit",second:"2-digit"})}</time></div><small>{event.component} · {event.event_name}{event.status ? " · " + event.status : ""}</small></div></li>)}</ol>}
          {toolCalls.length > 0 && <section className="tool-inspector"><div className="task-timeline-heading"><strong>Operações da tarefa</strong><span>{toolCalls.length} chamadas</span></div>{toolCalls.map(call => <details className="tool-inspector-item" key={call.id}><summary><span>#{call.id} · {call.tool_name}</span><span className={"task-status status-" + call.status}>{call.status}</span></summary><div className="tool-inspector-body"><strong>Argumentos</strong><pre>{JSON.stringify(call.arguments, null, 2)}</pre>{(call.results || []).map(result => <div className="tool-result-inspector" key={result.id}><strong>Resultado · {result.status}</strong>{result.error && <p>{result.error}</p>}{result.data && <pre>{JSON.stringify(result.data, null, 2)}</pre>}</div>)}</div></details>)}</section>}
                    {selected.result?.output && <div className="task-result"><strong>Resultado final</strong><FormattedResponse content={selected.result.output}/></div>}
          {selected.result?.error && <div className="task-inline-error"><strong>Falha:</strong> {selected.result.error}</div>}
          {active && <div className="task-detail-actions"><span>{selected.status === "awaiting_approval" ? "Aguardando aprovação" : "A tarefa está ativa"}</span><button type="button" className="danger-action" onClick={cancelTask} disabled={busy}>Cancelar tarefa</button></div>}
        </>}
      </section>
    </div>
  </section>;
}




function ProjectMemoryWorkspace({ projectId }) {
  const empty = { type: "fact", key: "", value: "", source: "user", confidence: "" };
  const [memories, setMemories] = useState([]);
  const [form, setForm] = useState(empty);
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  async function refresh() {
    if (!projectId) { setMemories([]); return; }
    setLoading(true);
    try { setMemories(await api.memories.list(projectId)); setError(""); }
    catch (err) { setError("Não foi possível carregar memórias: " + err.message); }
    finally { setLoading(false); }
  }
  useEffect(() => { setForm(empty); setEditingId(null); refresh(); }, [projectId]);

  function edit(memory) {
    setEditingId(memory.id);
    setForm({ type: memory.type, key: memory.key, value: memory.value, source: memory.source, confidence: memory.confidence ?? "" });
    setNotice("");
  }
  async function save(event) {
    event.preventDefault();
    if (!projectId || saving) return;
    setSaving(true); setError(""); setNotice("");
    const payload = { type: form.type.trim(), key: form.key.trim(), value: form.value.trim(), source: form.source.trim(), project_id: projectId, confidence: form.confidence === "" ? null : Number(form.confidence) };
    try {
      if (editingId) await api.memories.update(editingId, payload);
      else await api.memories.create(payload);
      setForm(empty); setEditingId(null); await refresh(); setNotice("Memória salva no Core.");
    } catch (err) { setError("Não foi possível salvar a memória: " + err.message); }
    finally { setSaving(false); }
  }
  async function remove(memory) {
    if (!window.confirm("Excluir a memória “" + memory.key + "”?")) return;
    try { await api.memories.remove(memory.id); await refresh(); setNotice("Memória excluída."); }
    catch (err) { setError("Não foi possível excluir: " + err.message); }
  }
  if (!projectId) return <div className="agent-config-workspace"><div className="task-empty"><Icon name="memory" size={25}/><strong>Selecione um projeto</strong><span>As memórias ficam vinculadas ao projeto ativo.</span></div></div>;
  return <section className="agent-config-workspace">
    <div className="task-workspace-heading"><div><span className="eyebrow">CONTEXTO PERSISTENTE</span><h2>Memória do projeto</h2><p>Gerencie registros persistidos no Core. Uma memória é um registro, não uma verdade automaticamente verificada.</p></div><span className="task-count">{memories.length} registros</span></div>
    <form className="agent-config-card memory-editor-form" onSubmit={save}><div className="agent-config-card-heading"><div><strong>{editingId ? "Editar memória" : "Nova memória"}</strong><span>Campos salvos no banco do Atlas Core</span></div></div>
      <div className="memory-form-grid"><label>Tipo<input value={form.type} onChange={e => setForm(v => ({...v,type:e.target.value}))} required maxLength={80}/></label><label>Chave<input value={form.key} onChange={e => setForm(v => ({...v,key:e.target.value}))} required maxLength={200} placeholder="Ex.: stack_principal"/></label><label>Origem<input value={form.source} onChange={e => setForm(v => ({...v,source:e.target.value}))} required maxLength={120}/></label><label>Confiança (opcional)<input type="number" min="0" max="1" step="0.05" value={form.confidence} onChange={e => setForm(v => ({...v,confidence:e.target.value}))} placeholder="0–1"/></label></div>
      <label className="memory-value-label">Conteúdo<textarea value={form.value} onChange={e => setForm(v => ({...v,value:e.target.value}))} required rows={3} maxLength={5000} placeholder="O que o Atlas deve lembrar?"/></label>
      <div className="modal-actions"><button type="button" onClick={() => {setForm(empty);setEditingId(null);}}>Limpar</button><button className="primary-action" disabled={saving}>{saving ? "Salvando…" : editingId ? "Atualizar memória" : "Salvar memória"}</button></div>
    </form>
    {error && <div className="task-inline-error" role="alert">{error}</div>}{notice && <div className="agent-config-success" role="status">{notice}</div>}
    <section className="memory-manager-list"><div className="task-panel-heading"><strong>Memórias persistidas</strong><button type="button" onClick={refresh} aria-label="Atualizar memórias">↻</button></div>{loading ? <div className="task-muted">Carregando memórias…</div> : !memories.length ? <div className="task-muted">Nenhuma memória registrada para este projeto.</div> : memories.map(memory => <article className="memory-manager-item" key={memory.id}><div><strong>{memory.key}</strong><span className="memory-type">{memory.type}</span></div><p>{memory.value}</p><small>Origem: {memory.source}{memory.confidence !== null && memory.confidence !== undefined ? " · Confiança " + Math.round(memory.confidence*100) + "%" : ""}</small><div className="memory-item-actions"><button type="button" className="secondary-action" onClick={() => edit(memory)}>Editar</button><button type="button" className="text-danger" onClick={() => remove(memory)}>Excluir</button></div></article>)}</section>
  </section>;
}

function ProjectNotesWorkspace({ project, onSaved }) {
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  useEffect(() => { setNotes(String(project?.metadata?.notes || "")); setError(""); setNotice(""); }, [project?.id, project?.metadata?.notes]);
  async function save(event) {
    event.preventDefault();
    if (!project || saving) return;
    setSaving(true); setError(""); setNotice("");
    try {
      const updated = await api.projects.update(project.id, { metadata: { ...(project.metadata || {}), notes } });
      onSaved(updated);
      setNotice("Notas salvas no projeto.");
    } catch (err) { setError("Não foi possível salvar as notas: " + err.message); }
    finally { setSaving(false); }
  }
  if (!project) return <div className="agent-config-workspace"><div className="task-empty"><Icon name="note" size={25}/><strong>Selecione um projeto</strong><span>As notas ficam associadas aos metadados do projeto.</span></div></div>;
  return <section className="agent-config-workspace"><div className="task-workspace-heading"><div><span className="eyebrow">ANOTAÇÕES DO PROJETO</span><h2>Notas</h2><p>Registre decisões e lembretes do projeto sem tratá-los automaticamente como instruções do agente.</p></div></div><form className="agent-config-card" onSubmit={save}><label className="memory-value-label">Notas de {project.name}<textarea className="project-notes-editor" value={notes} onChange={e => setNotes(e.target.value)} rows={18} maxLength={20000} placeholder="Decisões, pendências, links internos e lembretes…"/></label><div className="agent-editor-footer">{notes.length.toLocaleString("pt-BR")} / 20.000 caracteres</div>{error && <div className="task-inline-error" role="alert">{error}</div>}{notice && <div className="agent-config-success" role="status">{notice}</div>}<div className="agent-config-save"><span>Salvas nos metadados persistentes do projeto.</span><button className="primary-action" disabled={saving}>{saving ? "Salvando…" : "Salvar notas"}</button></div></form></section>;
}

function ProjectFilesWorkspace({ projectId, mode = "files" }) {
  const [inventory, setInventory] = useState([]);
  const [selectedPath, setSelectedPath] = useState("");
  const [excerpt, setExcerpt] = useState(null);
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [reading, setReading] = useState(false);
  const [error, setError] = useState("");
  const [truncated, setTruncated] = useState(false);

  useEffect(() => {
    let active = true;
    setInventory([]); setSelectedPath(""); setExcerpt(null); setSearchResults(null); setError("");
    if (!projectId) return undefined;
    setLoading(true);
    api.projects.artifacts(projectId).then(data => {
      if (!active) return;
      setInventory(data.entries || []);
      setTruncated(Boolean(data.truncated));
    }).catch(err => { if (active) setError("Não foi possível listar os arquivos: " + err.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [projectId]);

  async function openFile(path) {
    if (!projectId || !path) return;
    setSelectedPath(path); setReading(true); setError("");
    try { setExcerpt(await api.projects.artifactExcerpt(projectId, path)); }
    catch (err) { setExcerpt(null); setError("Não foi possível ler este arquivo: " + err.message); }
    finally { setReading(false); }
  }

  async function search(event) {
    event.preventDefault();
    if (!projectId || !query.trim()) { setSearchResults(null); return; }
    setError("");
    try { const data = await api.projects.searchArtifacts(projectId, query.trim()); setSearchResults(data.results || []); }
    catch (err) { setError("A busca falhou: " + err.message); }
  }

  const entries = searchResults === null ? inventory : searchResults.map(result => ({
    path: result.path, name: result.path.split("/").pop(), suffix: result.path.includes(".") ? "." + result.path.split(".").pop().toLowerCase() : "", size_bytes: result.size_bytes, score: result.score, matched_terms: result.matched_terms,
  }));
  const title = mode === "artifacts" ? "Arquivos e artefatos do workspace" : "Arquivos do projeto";

  return <section className="project-files-workspace">
    <div className="task-workspace-heading"><div><span className="eyebrow">{mode === "artifacts" ? "RESULTADOS DO WORKSPACE" : "EXPLORADOR DO PROJETO"}</span><h2>{title}</h2><p>{mode === "artifacts" ? "Inspecione arquivos existentes no workspace. O Core ainda não possui um registro separado de artefatos por tarefa." : "Navegue pelos arquivos e abra trechos de texto com origem e linhas preservadas."}</p></div><span className="task-count">{inventory.length} arquivos{truncated ? "+" : ""}</span></div>
    {!projectId ? <div className="task-empty"><Icon name="folder" size={25}/><strong>Selecione um projeto</strong><span>O inventário é limitado ao workspace do projeto ativo.</span></div> : <>
      <form className="project-file-search" onSubmit={search}><Icon name="search" size={17}/><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Buscar por nome ou conteúdo…" maxLength={300}/><button type="submit" className="secondary-action" disabled={!query.trim()}>Buscar</button>{searchResults !== null && <button type="button" className="text-danger" onClick={() => {setSearchResults(null);setQuery("");}}>Limpar</button>}</form>
      {error && <div className="task-inline-error" role="alert">{error}</div>}
      <div className="project-file-layout"><section className="project-file-list"><div className="task-panel-heading"><strong>{searchResults === null ? "Inventário" : "Resultados da busca"}</strong><span>{entries.length}</span></div>
        {loading ? <div className="task-muted">Lendo inventário…</div> : !entries.length ? <div className="task-muted">Nenhum arquivo encontrado.</div> : entries.map(entry => <button type="button" key={entry.path} className={selectedPath === entry.path ? "project-file-item selected" : "project-file-item"} onClick={() => openFile(entry.path)}><Icon name="file" size={16}/><span><strong>{entry.path}</strong><small>{entry.suffix || "arquivo"} · {Number(entry.size_bytes || 0).toLocaleString("pt-BR")} bytes{entry.score ? " · relevância " + entry.score : ""}</small></span></button>)}
        {truncated && searchResults === null && <div className="task-muted">Inventário limitado por segurança. Alguns arquivos podem não aparecer.</div>}
      </section>
      <section className="project-file-preview"><div className="task-panel-heading"><strong>{selectedPath || "Pré-visualização"}</strong>{excerpt && <span>Linhas {excerpt.start_line}–{excerpt.end_line} de {excerpt.total_lines}</span>}</div>
        {!selectedPath ? <div className="task-empty compact"><Icon name="file" size={23}/><strong>Selecione um arquivo</strong><span>O conteúdo será lido sob demanda, com limites e validação de caminho.</span></div> : reading ? <div className="task-muted">Lendo trecho…</div> : excerpt ? <><pre className="project-file-code">{excerpt.content}</pre><div className="project-file-provenance"><span>Origem: {excerpt.path} · linhas {excerpt.start_line}–{excerpt.end_line}</span>{excerpt.truncated && <span>Trecho truncado</span>}</div></> : <div className="task-muted">Pré-visualização indisponível.</div>}
      </section></div>
    </>}
  </section>;
}

function AgentConfigWorkspace({ projectId }) {
  const [instructions, setInstructions] = useState("");
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    let active = true;
    if (!projectId) { setInstructions(""); setSkills([]); return undefined; }
    setLoading(true);
    setError("");
    api.projects.agentConfig(projectId).then(config => {
      if (!active) return;
      setInstructions(config.instructions || "");
      setSkills(Array.isArray(config.skills) ? config.skills : []);
    }).catch(err => { if (active) setError("Não foi possível carregar as instruções: " + err.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [projectId]);

  function updateSkill(index, patch) {
    setSkills(items => items.map((skill, i) => i === index ? { ...skill, ...patch } : skill));
  }
  function addSkill() {
    if (skills.length >= 12) return;
    setSkills(items => [...items, { name: "", content: "", enabled: true }]);
  }
  async function save(event) {
    event.preventDefault();
    if (!projectId || saving) return;
    setSaving(true); setError(""); setNotice("");
    try {
      const config = await api.projects.saveAgentConfig(projectId, { instructions, skills });
      setInstructions(config.instructions || "");
      setSkills(config.skills || []);
      setNotice("Configuração salva. As instruções e skills serão consideradas no contexto das próximas execuções.");
    } catch (err) { setError("Não foi possível salvar: " + err.message); }
    finally { setSaving(false); }
  }

  if (!projectId) return <div className="agent-config-workspace"><div className="task-empty"><Icon name="settings" size={25}/><strong>Selecione um projeto</strong><span>As instruções e skills são específicas de cada workspace.</span></div></div>;
  return <section className="agent-config-workspace">
    <div className="task-workspace-heading"><div><span className="eyebrow">CONTROLE DO AGENTE</span><h2>Instruções e skills</h2><p>Defina o papel, os limites de trabalho e as especialidades do agente neste projeto.</p></div></div>
    {loading ? <div className="task-muted">Carregando configuração…</div> : <form onSubmit={save}>
      <section className="agent-config-card"><div className="agent-config-card-heading"><div><strong>AGENTS.md</strong><span>Instruções permanentes do projeto</span></div><span className="task-count">Até 12.000 caracteres</span></div><p>Descreva o objetivo do agente, padrões do projeto, estilo de trabalho e regras que ele deve seguir. O arquivo é salvo na raiz do workspace.</p><textarea className="agent-instructions-editor" value={instructions} maxLength={12000} onChange={event => setInstructions(event.target.value)} rows={12} placeholder={"Ex.: Você é o agente responsável por este projeto.\n- Priorize mudanças pequenas e testáveis.\n- Leia os contratos antes de editar.\n- Não declare testes como aprovados sem executá-los."}/><div className="agent-editor-footer"><span>{instructions.length.toLocaleString("pt-BR")} / 12.000 caracteres</span></div></section>
      <section className="agent-config-card"><div className="agent-config-card-heading"><div><strong>Skills do projeto</strong><span>Capacidades e procedimentos reutilizáveis</span></div><button type="button" className="secondary-action" onClick={addSkill} disabled={skills.length >= 12}>+ Adicionar skill</button></div><p>Uma skill é uma instrução especializada. Ative somente as relevantes; elas entram no contexto do agente, mas não concedem permissões extras às ferramentas.</p>
        {!skills.length && <div className="task-muted">Nenhuma skill cadastrada. Adicione, por exemplo, “Revisão de código”, “Testes Python” ou “Documentação”.</div>}
        {skills.map((skill, index) => <article className="skill-editor" key={index}><div className="skill-editor-head"><label className="skill-enabled"><input type="checkbox" checked={skill.enabled !== false} onChange={event => updateSkill(index, { enabled: event.target.checked })}/> Ativa</label><button type="button" className="text-danger" onClick={() => setSkills(items => items.filter((_, i) => i !== index))}>Remover</button></div><label>Nome da skill<input value={skill.name} maxLength={80} onChange={event => updateSkill(index, { name: event.target.value })} placeholder="Ex.: Revisão de código" required/></label><label>Instruções da skill<textarea value={skill.content} maxLength={4000} rows={5} onChange={event => updateSkill(index, { content: event.target.value })} placeholder="Quando usar esta skill, passos a seguir, critérios de qualidade…"/></label><div className="agent-editor-footer"><span>{(skill.content || "").length.toLocaleString("pt-BR")} / 4.000 caracteres</span></div></article>)}
        <div className="agent-editor-footer"><span>Máximo de 12 skills; até 12.000 caracteres ativos no total.</span></div>
      </section>
      {error && <div className="task-inline-error" role="alert">{error}</div>}{notice && <div className="agent-config-success" role="status">{notice}</div>}
      <div className="agent-config-save"><span>As regras de segurança e aprovações do Core sempre prevalecem.</span><button className="primary-action" type="submit" disabled={saving || loading}>{saving ? "Salvando…" : "Salvar configuração do agente"}</button></div>
    </form>}
  </section>;
}

function ContextRow({icon,label,children}){return <div className="context-row"><span className="context-row-icon"><Icon name={icon} size={18}/></span><span className="context-row-label">{label}</span><div className="context-row-value">{children}</div></div>;}
function ContextPanel({tab,setTab,project,conversation,model,memoryCount,messageCount,memories}) {
  return <aside className="context-panel"><nav className="context-tabs">{["Contexto","Memória","Arquivos"].map(x=><button key={x} className={tab===x?"active":""} onClick={()=>setTab(x)}>{x}</button>)}</nav>
    {tab==="Contexto"&&<><section className="context-card"><div className="card-heading"><strong>Contexto atual</strong><span>O que o Atlas está usando para responder</span></div>
      <ContextRow icon="cube" label="Projeto">{project?<><strong>{project.name}</strong><small>{project.description || "Development Project"}</small></>:<span className="muted-copy">Nenhum projeto</span>}</ContextRow>
      <ContextRow icon="box" label="Modelo">{model?<><strong>{model.name}</strong><small>{model.provider} · {model.model_name}</small><span className="online"><i/>{model.enabled ? "Disponível" : "Desabilitado"}</span></>:<span className="muted-copy">Nenhum modelo selecionado</span>}</ContextRow>
      <ContextRow icon="layers" label="Memória"><strong>{memoryCount} {memoryCount === 1 ? "item" : "itens"} relevantes</strong><small>Memórias do projeto</small></ContextRow>
      <ContextRow icon="history" label="Histórico"><strong>{messageCount} {messageCount === 1 ? "mensagem" : "mensagens"}</strong><small>Histórico da conversa</small></ContextRow>
      <ContextRow icon="file" label="Arquivos"><span className="muted-copy">Inventário disponível na aba Arquivos do projeto</span></ContextRow>
      <ContextRow icon="tool" label="Ferramentas"><span className="muted-copy">Detalhes das operações aparecem na linha do tempo das tarefas</span></ContextRow>
    </section><section className="side-card"><div className="side-card-heading"><strong>Estado real</strong></div><div className="state-line">Projeto <b>{project?.id ?? "—"}</b></div><div className="state-line">Conversa <b>{conversation?.id ?? "—"}</b></div></section></>}
    {tab==="Memória"&&<section className="context-card standalone-card"><div className="card-heading"><strong>Memória</strong><span>{memoryCount} {memoryCount === 1 ? "item" : "itens"} do projeto</span></div>{memoryCount?<div className="memory-list">{memories.map(memory=><div className="memory-item" key={memory.id}><div className="memory-item-head"><strong>{memory.key}</strong><span className="memory-type">{memory.type}</span></div><span>{memory.value}</span><small>Origem: {memory.source}{memory.confidence !== null && memory.confidence !== undefined ? ` · Confiança: ${Math.round(memory.confidence * 100)}%` : ""}</small></div>)}</div>:<div className="empty-state"><Icon name="memory" size={24}/><strong>Nenhuma memória</strong><span>O projeto ainda não possui memórias persistidas.</span></div>}</section>}
    {tab==="Arquivos"&&<section className="context-card standalone-card"><div className="card-heading"><strong>Arquivos</strong><span>Arquivos do projeto.</span></div><div className="empty-state"><Icon name="folder" size={24}/><strong>Arquivos</strong><span>Abra a aba Arquivos do projeto para navegar, buscar e pré-visualizar trechos com origem e linhas.</span></div></section>}
  </aside>;
}

function Modal({title,onClose,children}){
  if(typeof document === "undefined") return null;
  return createPortal(
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <div className="modal" role="dialog" aria-modal="true" aria-label={title} onMouseDown={e=>e.stopPropagation()}>
        <div className="modal-header"><strong>{title}</strong><button type="button" onClick={onClose} aria-label="Fechar">×</button></div>
        {children}
      </div>
    </div>,
    document.body
  );
}


export default function App(){
  const [projects,setProjects]=useState([]),[conversations,setConversations]=useState([]),[models,setModels]=useState([]),[memories,setMemories]=useState([]),[projectId,setProjectId]=useState(null),[conversationId,setConversationId]=useState(null),[messages,setMessages]=useState([]);
  const [mobile,setMobile]=useState(false),[contextTab,setContextTab]=useState("Contexto"),[projectTab,setProjectTab]=useState("Conversa"),[loading,setLoading]=useState(true),[messagesLoading,setMessagesLoading]=useState(false),[sending,setSending]=useState(false),[error,setError]=useState(""),[modal,setModal]=useState(null),[saving,setSaving]=useState(false),[modelStatus,setModelStatus]=useState({provider:"ollama",online:false,running_models:[]});
  const project=projects.find(p=>p.id===projectId)||null,conversation=conversations.find(c=>c.id===conversationId)||null,model=models.find(m=>m.id===conversation?.model_id)||null,projectConversations=conversations.filter(c=>c.project_id===projectId);

  async function load(){setLoading(true);setError("");try{const [ps,cs,ms]=await Promise.all([api.projects.list(),api.conversations.list(),api.models.list()]);setProjects(ps);setConversations(cs);setModels(ms);const savedP=Number(localStorage.getItem("mosaic.activeProjectId"));const p=ps.find(x=>x.id===savedP)||ps[0];const savedC=Number(localStorage.getItem("mosaic.activeConversationId"));const c=cs.find(x=>x.id===savedC)||cs.find(x=>x.project_id===p?.id);setProjectId(p?.id??null);setConversationId(c?.id??null);}catch(e){setError("Não foi possível conectar ao Atlas Core: "+e.message);}finally{setLoading(false);}}
  useEffect(()=>{load();},[]);
  useEffect(()=>{
    let cancelled=false;
    async function refreshModelStatus(){
      try{
        const status=await api.models.status();
        if(!cancelled)setModelStatus(status);
      }catch{
        if(!cancelled)setModelStatus({provider:"ollama",online:false,running_models:[]});
      }
    }
    refreshModelStatus();
    const timer=setInterval(refreshModelStatus,5000);
    return ()=>{cancelled=true;clearInterval(timer);};
  },[]);

  useEffect(()=>{if(projectId)localStorage.setItem("mosaic.activeProjectId",String(projectId));},[projectId]);
  useEffect(()=>{if(conversationId)localStorage.setItem("mosaic.activeConversationId",String(conversationId));},[conversationId]);
  useEffect(()=>{
    let cancelled=false;
    async function loadMemories(){
      if(!projectId){setMemories([]);return;}
      try{
        const data=await api.memories.list(projectId);
        if(!cancelled)setMemories(data);
      }catch(err){
        if(!cancelled)setError("Não foi possível recuperar as memórias: "+err.message);
      }
    }
    loadMemories();
    return ()=>{cancelled=true;};
  },[projectId]);

  useEffect(()=>{
    let cancelled=false;
    async function loadMessages(){
      if(!conversationId){setMessages([]);return;}
      setMessagesLoading(true);
      try{
        const data=await api.conversations.messages(conversationId);
        if(!cancelled)setMessages(data);
      }catch(err){
        if(!cancelled)setError("Não foi possível recuperar o histórico: "+err.message);
      }finally{
        if(!cancelled)setMessagesLoading(false);
      }
    }
    loadMessages();
    return ()=>{cancelled=true;};
  },[conversationId]);


  function selectProject(id){setProjectId(id);setConversationId(conversations.find(c=>c.project_id===id)?.id??null);setProjectTab("Conversa");setMobile(false);}
  function selectConversation(id){const c=conversations.find(x=>x.id===id);setConversationId(id);if(c?.project_id)setProjectId(c.project_id);setMobile(false);}

  async function createProject(e){e.preventDefault();setSaving(true);const f=new FormData(e.currentTarget);const name=String(f.get("name")||"").trim();const description=String(f.get("description")||"").trim();try{const p=await api.projects.create({name,description:description||null,workspace:"./workspaces/"+slugify(name),metadata:{},state:{}});setProjects(x=>[...x,p]);setProjectId(p.id);setConversationId(null);setModal(null);}catch(err){setError(err.message);}finally{setSaving(false);}}
  async function createConversation(e){e.preventDefault();setSaving(true);const f=new FormData(e.currentTarget);const title=String(f.get("title")||"Nova conversa").trim()||"Nova conversa";const modelId=Number(f.get("model_id"))||models.find(m=>m.enabled)?.id;if(!modelId){setError("Nenhum modelo habilitado está registrado no Atlas.");setSaving(false);return;}try{const c=await api.conversations.create({title,model_id:modelId,project_id:projectId});setConversations(x=>[c,...x]);setConversationId(c.id);setModal(null);}catch(err){setError(err.message);}finally{setSaving(false);}}

  async function sendMessage(content){
    if(!conversation||sending)return;
    setError("");
    setSending(true);
    const localUser={localId:`user-${Date.now()}`,role:"user",content,created_at:new Date().toISOString()};
    const localAssistant={localId:`assistant-${Date.now()}`,role:"assistant",content:"",created_at:new Date().toISOString()};
    setMessages(items=>[...items,localUser,localAssistant]);
    try{
      let streamed="";
      await api.conversations.stream(conversation.id,content,chunk=>{
        streamed+=chunk;
        setMessages(items=>items.map(item=>item.localId===localAssistant.localId?{...item,content:streamed}:item));
      });
      const persisted=await api.conversations.messages(conversation.id);
      setMessages(persisted);
      setConversations(items=>items.map(item=>item.id===conversation.id?{...item,updated_at:new Date().toISOString()}:item));
    }catch(err){
      setMessages(items=>items.filter(item=>item.localId!==localAssistant.localId));
      setError("Não foi possível concluir a resposta: "+err.message);
    }finally{
      setSending(false);
    }
  }

  async function changeConversationModel(modelId){if(!conversation)return;setError("");try{const updated=await api.conversations.update(conversation.id,{model_id:modelId});setConversations(items=>items.map(item=>item.id===updated.id?updated:item));}catch(err){setError("Não foi possível trocar o modelo: "+err.message);}}
  async function saveModel(e){
    e.preventDefault();setSaving(true);setError("");
    const f=new FormData(e.currentTarget);
    const id=Number(f.get("id")); const configuration={
      temperature:Number(f.get("temperature")), top_p:Number(f.get("top_p")), top_k:Number(f.get("top_k")),
      num_ctx:Number(f.get("num_ctx")), num_predict:Number(f.get("num_predict"))
    };
    try{
      const updated=await api.models.update(id,{name:String(f.get("name")).trim(),configuration,enabled:f.get("enabled")==="on"});
      setModels(items=>items.map(item=>item.id===updated.id?updated:item));
      setModal(null);
    }catch(err){setError("Não foi possível salvar o modelo: "+err.message);}finally{setSaving(false);}
  }
  async function createModel(e){
    e.preventDefault();setSaving(true);setError("");
    const f=new FormData(e.currentTarget);
    const configuration={temperature:Number(f.get("temperature")),top_p:Number(f.get("top_p")),top_k:Number(f.get("top_k")),num_ctx:Number(f.get("num_ctx")),num_predict:Number(f.get("num_predict"))};
    try{
      const created=await api.models.create({name:String(f.get("name")).trim(),provider:String(f.get("provider")).trim(),model_name:String(f.get("model_name")).trim(),configuration,enabled:true});
      setModels(items=>[...items,created]);setModal({type:"model",modelId:created.id}); 
    }catch(err){setError("Não foi possível cadastrar o modelo: "+err.message);}finally{setSaving(false);}
  }

  return <div className="app-shell"><Sidebar projects={projects} conversations={projectConversations} activeProjectId={projectId} activeConversationId={conversationId} onProject={selectProject} onConversation={selectConversation} onNewProject={()=>setModal("project")} onNewConversation={()=>setModal("conversation")} onModelSettings={()=>setModal({type:"models"})} onHelp={()=>setModal({type:"help"})} onHome={()=>setProjectTab("Conversa")} mobileOpen={mobile} onClose={()=>setMobile(false)}/>{mobile&&<button className="mobile-overlay" onClick={()=>setMobile(false)} aria-label="Fechar menu"/>}
    <div className="app-main"><TopBar onMenu={()=>setMobile(true)} onFiles={()=>setProjectTab("Arquivos")} project={project} conversation={conversation} models={models} onModelChange={changeConversationModel} modelStatus={modelStatus} onModelSettings={()=>setModal({type:"models"})} onContext={setContextTab}/><div className="workspace-grid"><main className="workspace"><ProjectHeader project={project} tab={projectTab} setTab={setProjectTab}/>{error&&<div className="api-error">{error}<button onClick={load}>Tentar novamente</button></div>}{projectTab === "Tarefas" ? <TaskWorkspace conversationId={conversation?.id ?? null} projectId={project?.id ?? null}/> : projectTab === "Agente" ? <AgentConfigWorkspace projectId={project?.id ?? null}/> : projectTab === "Arquivos" ? <ProjectFilesWorkspace projectId={project?.id ?? null} mode="files"/> : projectTab === "Artefatos" ? <ProjectFilesWorkspace projectId={project?.id ?? null} mode="artifacts"/> : projectTab === "Memória" ? <ProjectMemoryWorkspace projectId={project?.id ?? null}/> : projectTab === "Notas" ? <ProjectNotesWorkspace project={project} onSaved={updated => setProjects(items => items.map(item => item.id === updated.id ? updated : item))}/> : <><div className="chat-scroll">{loading?<div className="loading-state">Conectando ao Atlas Core…</div>:!conversation?<div className="conversation-empty"><AtlasMark compact/><h2>Workspace pronto</h2><p>{project ? "Projeto ativo: "+project.name+"." : "Crie ou selecione um projeto para começar."}</p>{!conversation&&<button className="empty-action" onClick={()=>setModal("conversation")} disabled={!project||!models.some(m=>m.enabled)}><Icon name="plus" size={16}/>Nova conversa</button>}</div>:messagesLoading?<div className="loading-state">Recuperando histórico…</div>:<MessageList messages={messages} streaming={sending}/>} </div><Composer disabled={!conversation||sending} model={model} onSubmit={sendMessage} onFiles={()=>setProjectTab("Arquivos")} onAgent={()=>setProjectTab("Agente")}/></>}</main><ContextPanel tab={contextTab} setTab={setContextTab} project={project} conversation={conversation} model={model} memoryCount={memories.length} messageCount={messages.length} memories={memories}/></div></div>
    {modal?.type==="help"&&<Modal title="Ajuda" onClose={()=>setModal(null)}><div className="modal-form"><p className="modal-hint">O Atlas é uma interface conectada ao Atlas Core. O estado persistente vem do backend; esta interface apresenta e controla esse estado.</p><div className="help-block"><strong>Começando</strong><span>Crie um projeto, depois crie uma conversa e selecione um modelo registrado no Core.</span></div><div className="help-block"><strong>Modelos</strong><span>Use Configurações para cadastrar e ajustar modelos. O status no topo consulta o Ollama quando o provider é Ollama.</span></div><div className="help-block"><strong>Contexto</strong><span>O painel lateral mostra projeto, modelo, memória e histórico reais da conversa ativa.</span></div></div></Modal>}
    {modal?.type==="models"&&<Modal title="Modelos e configurações" onClose={()=>!saving&&setModal(null)}><div className="modal-form"><p className="modal-hint">Os valores abaixo são persistidos no Core e enviados ao provider quando a conversa usa este modelo.</p>{models.map(m=><button key={m.id} type="button" className="related-item" onClick={()=>setModal({type:"model",modelId:m.id})}><span className="status-dot"/><span>{m.name}</span><span className="model-provider">{m.provider} · {m.model_name}</span></button>)}<button type="button" className="primary-action" onClick={()=>setModal({type:"new-model"})}>+ Cadastrar modelo</button></div></Modal>}
    {modal?.type==="model"&&(()=>{const m=models.find(x=>x.id===modal.modelId);if(!m)return null;const c=m.configuration||{};return <Modal title={"Configurar "+m.name} onClose={()=>!saving&&setModal(null)}><form className="modal-form modal-wide" onSubmit={saveModel}><input type="hidden" name="id" value={m.id}/><label>Nome<input name="name" defaultValue={m.name} required/></label><div className="model-config-grid"><label>Temperature<input type="number" name="temperature" step="0.1" min="0" max="2" defaultValue={c.temperature ?? 0.7}/></label><label>Top P<input type="number" name="top_p" step="0.05" min="0" max="1" defaultValue={c.top_p ?? 0.9}/></label><label>Top K<input type="number" name="top_k" min="0" max="100" defaultValue={c.top_k ?? 40}/></label><label>Contexto<input type="number" name="num_ctx" min="256" max="131072" defaultValue={c.num_ctx ?? 4096}/></label><label>Máx. tokens<input type="number" name="num_predict" min="-1" max="131072" defaultValue={c.num_predict ?? -1}/></label><label className="model-config-toggle">Ativo<input type="checkbox" name="enabled" defaultChecked={m.enabled}/></label></div><p className="model-config-status">Provider: {m.provider} · Modelo local: {m.model_name}</p><div className="modal-actions"><button type="button" onClick={()=>setModal({type:"models"})}>Voltar</button><button className="primary-action" disabled={saving}>{saving?"Salvando…":"Salvar configurações"}</button></div></form></Modal>})()}
    {modal?.type==="new-model"&&<Modal title="Cadastrar modelo" onClose={()=>!saving&&setModal(null)}><form className="modal-form modal-wide" onSubmit={createModel}><div className="model-config-grid"><label>Nome<input name="name" required autoFocus placeholder="Ex.: Llama 3.2 3B"/></label><label>Provider<input name="provider" defaultValue="ollama" required/></label><label className="full">Identificador do modelo<input name="model_name" required placeholder="Ex.: llama3.2:3b"/></label><label>Temperature<input type="number" name="temperature" step="0.1" min="0" max="2" defaultValue="0.7"/></label><label>Top P<input type="number" name="top_p" step="0.05" min="0" max="1" defaultValue="0.9"/></label><label>Top K<input type="number" name="top_k" min="0" max="100" defaultValue="40"/></label><label>Contexto<input type="number" name="num_ctx" min="256" max="131072" defaultValue="4096"/></label><label>Máx. tokens<input type="number" name="num_predict" min="-1" max="131072" defaultValue="-1"/></label></div><div className="modal-actions"><button type="button" onClick={()=>setModal({type:"models"})}>Cancelar</button><button className="primary-action" disabled={saving}>{saving?"Cadastrando…":"Cadastrar modelo"}</button></div></form></Modal>}
    {modal==="project"&&<Modal title="Novo projeto" onClose={()=>!saving&&setModal(null)}><form className="modal-form" onSubmit={createProject}><label>Nome<input name="name" required autoFocus placeholder="Ex.: Guitar Livre"/></label><label>Descrição<textarea name="description" rows="3" placeholder="O que estamos construindo?"/></label><div className="modal-actions"><button type="button" onClick={()=>setModal(null)}>Cancelar</button><button className="primary-action" disabled={saving}>{saving?"Criando…":"Criar projeto"}</button></div></form></Modal>}
    {modal==="conversation"&&<Modal title="Nova conversa" onClose={()=>!saving&&setModal(null)}><form className="modal-form" onSubmit={createConversation}><p className="modal-hint">Projeto: <strong>{project?.name || "Nenhum projeto"}</strong></p><label>Título<input name="title" required autoFocus placeholder="Ex.: Arquitetura do projeto"/></label><label>Modelo<select name="model_id" defaultValue={models.find(m=>m.enabled)?.id ?? ""} required><option value="" disabled>Selecione um modelo</option>{models.filter(m=>m.enabled).map(m=><option key={m.id} value={m.id}>{m.name}</option>)}</select></label><div className="modal-actions"><button type="button" onClick={()=>setModal(null)}>Cancelar</button><button className="primary-action" disabled={saving||!project||!models.some(m=>m.enabled)}>{saving?"Criando…":"Criar conversa"}</button></div></form></Modal>}
  </div>;
}
