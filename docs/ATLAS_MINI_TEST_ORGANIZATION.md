# Atlas Mini — organização dos testes

Os testes são agrupados por responsabilidade, não por versão do pacote.

- `tests/test_atlas_mini_robotics.py`: gateway, servo, parada de emergência e validação de ângulos.
- `tests/test_atlas_mini_embodiment_session.py`: histórico e validação do ciclo conversacional.
- `tests/test_atlas_mini_embodiment_providers.py`: Whisper.cpp, Piper e Ollama.
- `tests/test_atlas_mini_security.py`: aprovações e integridade de auditoria.

Os testes de V1, V2 e V3 foram preservados, apenas reorganizados. Execute `python -m pytest -q`.
