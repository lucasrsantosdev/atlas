# Atlas Robotics + Embodiment — incremento de software

## Base e rastreabilidade

Incremento realizado sobre o pacote `atlas-mini-v3-tests-organizados.zip` disponível na conversa. A branch remota `dev/fernando` e o commit `735bb88` **não foram acessíveis neste ambiente**; confirme o diff antes de integrar. Não é uma atualização automática do GitHub.

## Arquitetura

```text
Microfone/PCM -> AudioFramer -> WhisperCppSTT -> VoiceSession/DialogueCoordinator
                                              | -> Atlas Core / memória adaptável
                                              v
                                       PiperTTS -> saída WAV
PerceptionBuffer -> eventos opt-in -> intenção -> gesture_steps (allowlist)
                                                 |
ToolRegistry -> PolicyEngine -> RobotController -> Command/ACK -> RobotSimulator
                                                     |                |
                                               MotionPlanner       Telemetry
                                                     |                |
                                              RoboticsSafety ---- SensorHub
```

## Implementado neste incremento

- `robotics/protocol.py`: envelope versionado, IDs de solicitação, ACK e telemetria.
- `robotics/controller.py`: conexão, ACK, retries limitados reutilizando o mesmo ID, parada e cancelamento entre etapas.
- `robotics/motion.py`: limites por articulação, delta máximo e pré-validação integral da sequência.
- `robotics/sensors.py`: interface de sensores, amostras validadas e snapshots.
- `robotics/safety.py`: watchdog lógico com parada travada e reset confirmado localmente na simulação.
- `robotics/simulator.py`: simulador com comandos idempotentes por ID, telemetria e falha de conexão injetável.
- `robotics/tools.py`: ferramentas registradas com permissões HARDWARE_READ/WRITE e aprovação para LED.
- `embodiment/audio_capture.py`: PCM mono 16-bit para WAV, detecção básica por RMS e limites de duração; **não abre microfone**.
- `embodiment/stt.py`, `tts.py`: exportam adaptadores offline já existentes; exigem binários/modelos instalados.
- `embodiment/dialogue.py`: adaptador de memória `recall/remember` explicitamente injetado, não conectado automaticamente ao MemoryService existente.
- `embodiment/perception.py`: buffer limitado de eventos, sem câmera real.
- `embodiment/gestures.py`: gestos explicitamente permitidos, sem inferência livre de movimentos.
- `embodiment/session.py`: implementação existente preservada.

## Evidência

Executar `PYTHONPATH=src python -m pytest -q` no Linux/macOS ou `$env:PYTHONPATH='src'; python -m pytest -q` no PowerShell. Testes incluem regressão, watchdog, limites, ACK idempotente, autorização, áudio e eventos.

## Ainda pendente — não alegar 100% de maturidade

1. Compilar e validar firmware ESP32 e transporte serial com bancada; protocolo novo ainda **não está integrado ao firmware**.
2. Segurança elétrica e mecânica: E-stop físico independente, torque, limites elétricos, testes de falha de energia e análise de risco.
3. Transportes reais com timeout de I/O, reconexão, ACK/retries com o dispositivo físico; atualmente o controlador trabalha com o simulador.
4. Captura de microfone e reprodução real, streaming, VAD robusto, barge-in, cancelamento assíncrono e latência ponta a ponta.
5. Integração real com modelos Whisper/Piper/Ollama e MemoryService/Agent Loop; teste em computador do operador.
6. Câmera, sensores físicos, mapeamento de animação Godot e sincronização de fala/gestos.
7. Segurança do plano de controle: autorização do reset local, limites de velocidade/aceleração e teste de movimentos sob falha.

**Aviso:** o watchdog, estop e a confirmação de reset deste incremento são **simulados/lógicos**. Não substituem sistemas de segurança física. Nunca conectar atuadores reais a este controlador sem engenharia de segurança adicional.
