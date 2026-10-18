# Atlas — Cognitive Robotics: planejamento e avaliação isolados

## Escopo
Esta entrega incremental adiciona quatro módulos **opt-in** em `src/atlas/robotics/cognition/`, um arquivo de testes e este documento. Não modifica módulos existentes e não conecta Atlas Core, hardware, LLM, microfone ou serviços externos.

## Recursos
- `hierarchical_planner.py`: decomposição hierárquica de tarefas em ações autorizadas, com proteção contra ciclos, profundidade excessiva e explosão do plano.
- `decision_evaluator.py`: pontuação determinística de alternativas por recompensa esperada, risco e duração; rejeição de ações não autorizadas ou arriscadas.
- `episodic_memory.py`: registro limitado em memória, isolamento por sessão e estatísticas de sucesso e recompensa. Não há treinamento de modelo.
- `scenario_runner.py`: simulação **simbólica**, reproduzível, de sequências de ações, falhas e cancelamento. Não movimenta servos nem simula dinâmica física.

## Exemplo
```python
from atlas.robotics.cognition.hierarchical_planner import Task, HierarchicalPlanner
from atlas.robotics.cognition.scenario_runner import ScenarioRunner

planner = HierarchicalPlanner(
    {'greet': Task('greet', (Task('acknowledge'), Task('neutral')))},
    {'acknowledge', 'neutral'},
)
result = ScenarioRunner(planner).run('greet', fail_at=1)
assert result.status == 'failed'
assert result.completed == ('acknowledge',)
```

## Teste no Windows
```powershell
$env:PYTHONPATH = 'src'
py -3.13 -m pytest -q tests/test_cognitive_planning_advanced.py
py -3.13 -m pytest -q
```

## Critérios de aceite
1. Nenhuma ação fora da allowlist entra no plano.
2. Ciclos e planos que excedem limites são rejeitados.
3. Avaliação não seleciona candidatos acima do risco máximo.
4. Memória tem limite de capacidade e não mistura sessões.
5. Cenários completos, cancelados e com falha produzem resultados determinísticos.
6. Suíte existente permanece verde.

## Limitações
A memória é volátil; as estimativas de recompensa e risco são fornecidas pelo chamador; o executor é simbólico; não há validação de segurança física nem IA generativa. Percentuais de maturidade só devem ser revistos após critérios adicionais de integração e avaliação.
