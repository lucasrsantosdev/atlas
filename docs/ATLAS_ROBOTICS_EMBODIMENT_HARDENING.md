# Atlas — Robotics / Embodiment: hardening incremental

## Escopo
Evolução **isolada de software**, sem conexão com ESP32, Godot, microfone ou serviços reais. Mantém APIs existentes e acrescenta APIs opt-in.

## Robotics
- `protocol.py`: `encode_command`, `decode_command`, CRC32, versão, sequência e limite de frame. CRC32 não é autenticação criptográfica. A idempotência por `request_id` continua responsabilidade do simulador/transporte.
- `motion.py`: `TimedMotionStep` e `interpolate_motion` com perfil de aceleração/desaceleração, limite de velocidade, aceleração, curso e incremento. Não executa movimentos físicos.
- `controller.py`: recuperação explícita após parada, condicionada à confirmação do operador no simulador.
- `sensors.py`: snapshot filtrado por idade máxima.
- `safety.py`: consulta do watchdog e falha lógica travada.
- `simulator.py`: mudança de conectividade e injeção de falha de sensor simulada.
- `tools.py`: **sem alteração**; autorização já existente, auditoria completa permanece pendente.

## Embodiment
- `audio_capture.py`: `AudioBuffer` PCM16 mono limitado por duração, flush e detecção RMS simples; não captura microfone.
- `stt.py`: `Transcript`, validação e erro padronizado; sem executar modelo real.
- `tts.py`: fragmentação por palavras e fila síncrona cancelável entre segmentos; não faz playback nem cancelamento de síntese em curso.
- `dialogue.py`: histórico isolado por ID de sessão e tamanho limitado; adaptador de memória permanece opcional.
- `perception.py`: filtragem temporal de eventos; sem acesso à câmera.
- `gestures.py`: prioridade e cancelamento de gestos; não movimenta atuadores.
- `session.py`: `SessionLifecycle` com transições explícitas; a classe `VoiceSession` antiga foi preservada.

## Testes e critérios
- `tests/test_robotics_hardening.py`: serialização, corrupção, limites, recuperação, sensores e falhas.
- `tests/test_embodiment_hardening.py`: buffers, STT/TTS, isolamento, expiração, prioridades e estados.
- Ambiente de preparação: `PYTHONPATH=src python -m pytest -q` => **114 passed** (90 testes da base disponível + 24 testes novos).
- Usuário relatou **106 testes aprovados** em seu repositório Windows antes desta entrega; a base ZIP disponível neste ambiente tem 90. A contagem após aplicação pode diferir. **Não se deve prometer 130 testes** sem execução local.

## Critérios ainda pendentes
- Protocolo real com ESP32 (firmware deve implementar framing/CRC e ACK); teste de reconexão e perda de ACK ponta a ponta.
- Interrupção de movimento em execução e integração de estados do controller com SafetyController e Agent Loop.
- Injeção determinística de latência e perda de mensagens, auditoria de ferramentas robóticas.
- Microfone, Whisper.cpp, Piper, Ollama, Godot e medições de latência real.
- Segurança elétrica/mecânica, E-stop físico e testes em bancada.

## Aplicação
Extraia o ZIP incremental **na raiz do repositório**, mantendo a estrutura `src/`, `tests/`, `docs/`. Os 13 módulos Python existentes indicados no manifesto serão sobrescritos; confira `git diff` antes de commitar. Nenhum arquivo é apagado. `robotics/atlas-mini` permanece intocado.
