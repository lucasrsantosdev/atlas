# Atlas Cognitive Robotics & Intelligent Embodiment — incremento isolado

## Escopo

Adiciona planejamento cognitivo **determinístico e opt-in** sem integrar com Agent Loop, LLM, ESP32, Godot ou dispositivos de áudio. Nenhum comando é executado pelo planejador. O executor continua sendo responsável por autorização, limites e segurança.

## Novos módulos

- `robotics/cognition/behavior_planner.py`: intenções permitidas, intensidade contextual e trajetórias interpoladas limitadas.
- `robotics/cognition/goal_manager.py`: objetivos explícitos com prioridade.
- `robotics/cognition/action_selector.py`: seleção entre candidatos fornecidos pelo chamador.
- `robotics/cognition/experience_memory.py`: feedback local e limitado (não é aprendizado de modelo).
- `robotics/cognition/behavior_tree.py`: condições compostas determinísticas.
- `embodiment/emotion.py`: pistas lexicais conservadoras, **não** detecção real de emoções.
- `embodiment/personality.py`: expressividade configurável.
- `embodiment/expression_planner.py`: afeto para intenção abstrata.
- `embodiment/gesture_generator.py`: gesto dependente de contexto e posição atual.

## Restrições e segurança

- Apenas intenções allowlisted, `head` no simulador atual e limites de articulação.
- O software de parada é lógico; **não** substitui parada de emergência física certificada.
- Sem captura implícita de câmera, microfone, inferência afetiva clínica ou ação autônoma.
- O gerador não aciona motores. Integração e autorização permanecem pendentes.
- A heurística lexical não é um modelo inteligente de linguagem; para decisões semânticas robustas será necessário conectar um modelo de IA com validação estruturada.

## Executar

```powershell
$env:PYTHONPATH = 'src'
py -3.13 -m pytest -q
py -3.13 -m pytest -q tests/test_cognitive_robotics_embodiment.py
```

## Próximos critérios de aceitação

Testar decisões com modelo externo sob contratos estritos, cenários de conflito e interrupção, percepção multimodal real, hardware, recuperação física e auditoria. Os percentuais 85%/80% são metas, não resultados certificados.
