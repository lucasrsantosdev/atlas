# ARQUITETURA DE ENERGIA DO ATLAS

**Versão:** 0.1.0  
**Status:** Rascunho  
**Criado em:** Setembro de 2026  

---

## Propósito

Este documento define a arquitetura energética do Atlas.

O objetivo é permitir que Atlas:

- conheça seu estado energético;
- reduza consumo quando necessário;
- sobreviva a interrupções;
- desligue de forma segura;
- preserve identidade e memória;
- utilize fontes alternativas;
- evite perda de dados;
- evite danos ao hardware;
- priorize segurança humana.

O princípio fundamental é:

> **Energia é um recurso operacional crítico, mas a continuidade do Atlas nunca deve ser colocada acima da vida e da segurança humana.**

---

# 1. Princípio Fundamental

Atlas deverá funcionar com uma arquitetura energética em camadas.

Exemplo:

```text
REDE ELÉTRICA
      ↓
     UPS
      ↓
  BATERIAS
      ↓
ATLAS CORE
```

Futuramente:

```text
                REDE ELÉTRICA
                      │
             ┌────────┼────────┐
             │        │        │
             ▼        ▼        ▼
           SOLAR   GERADOR   OUTRA FONTE
             │        │        │
             └────────┼────────┘
                      ▼
                ENERGY MANAGER
                      │
                      ▼
                    ATLAS
```

---

# 2. Objetivos da Arquitetura Energética

A arquitetura deverá permitir:

- alimentação estável;
- proteção elétrica;
- monitoramento;
- failover energético;
- desligamento controlado;
- reinicialização segura;
- operação degradada;
- gerenciamento de consumo;
- expansão futura.

---

# 3. Fontes de Energia

Atlas poderá utilizar diferentes fontes.

Inicialmente:

```text
GRID
UPS
BATTERY
```

Futuramente:

```text
SOLAR
GENERATOR
SECONDARY GRID
OTHER RENEWABLE SOURCES
```

---

# 4. Estados Energéticos

Atlas deverá reconhecer estados energéticos.

```text
NORMAL
REDUCED
LOW
CRITICAL
EMERGENCY
SHUTDOWN
```

---

# 5. Estado NORMAL

Condição:

```text
rede elétrica disponível
energia estável
bateria saudável
```

Capacidades:

- todos os serviços;
- modelos pesados;
- GPU;
- indexação;
- backups;
- voz;
- visão;
- robótica autorizada.

---

# 6. Estado REDUCED

Energia disponível, mas com alguma limitação.

Atlas poderá:

- reduzir processos de fundo;
- limitar modelos pesados;
- reduzir GPU;
- pausar tarefas não prioritárias.

---

# 7. Estado LOW

Exemplo conceitual:

```text
rede indisponível
bateria em uso
autonomia limitada
```

Atlas deverá priorizar:

```text
Identity
Memory
Atlas Core
Knowledge Essential
Fast Model
```

---

# 8. Estado CRITICAL

Atlas deverá desligar cargas não essenciais.

Exemplo:

```text
Vision
Advanced Models
Background Indexing
Non-critical Robotics
Large Batch Processing
```

deverão ser suspensos.

---

# 9. Estado EMERGENCY

Somente componentes essenciais deverão continuar.

```text
Identity
Constitution
Critical Memory
Atlas Emergency
Monitoring
Recovery Interface
```

---

# 10. Estado SHUTDOWN

Quando não houver energia suficiente:

```text
Save State
↓
Flush Memory
↓
Commit Database
↓
Stop Models
↓
Stop Services
↓
Unmount Storage
↓
Shutdown
```

---

# 11. Energy Manager

Atlas deverá possuir um componente chamado:

```text
Energy Manager
```

Responsabilidades:

- monitorar energia;
- calcular estado energético;
- estimar autonomia;
- aplicar políticas;
- desligar cargas;
- enviar alertas;
- coordenar shutdown.

---

# 12. Arquitetura do Energy Manager

```text
Energy Sources
     ↓
Sensors / UPS
     ↓
Energy Monitor
     ↓
Energy Manager
     ↓
Policy Layer
     ↓
Atlas Services
```

---

# 13. Estrutura Futura de Código

```text
src/
└── energy/
    ├── __init__.py
    ├── manager.py
    ├── monitor.py
    ├── policies.py
    ├── ups.py
    ├── battery.py
    ├── solar.py
    ├── consumption.py
    └── models.py
```

---

# 14. Configuração

Estrutura futura:

```text
config/
└── energy/
    ├── energy.yaml
    ├── devices.yaml
    └── policies.yaml
```

---

# 15. energy.yaml

Exemplo:

```yaml
energy:

  normal:
    minimum_battery_percent: 60

  reduced:
    minimum_battery_percent: 40

  low:
    minimum_battery_percent: 25

  critical:
    minimum_battery_percent: 15

  emergency:
    minimum_battery_percent: 8
```

Esses valores são apenas exemplos iniciais.

Valores reais deverão ser definidos após testes.

---

# 16. Fonte Principal

Inicialmente:

```text
GRID
```

A rede elétrica será a fonte primária.

Atlas deverá monitorar sua disponibilidade.

---

# 17. UPS

UPS será uma das primeiras proteções energéticas do projeto.

Funções:

- proteção contra queda;
- proteção contra interrupções curtas;
- tempo para shutdown;
- estabilização conforme equipamento utilizado.

---

# 18. UPS Não é Backup de Longa Duração

UPS deverá ser tratada como:

```text
TRANSITION POWER
```

e não necessariamente:

```text
LONG TERM POWER
```

Seu papel principal será permitir continuidade curta ou desligamento seguro.

---

# 19. Monitoramento da UPS

Atlas deverá conseguir obter quando suportado:

```text
battery percentage
runtime remaining
input voltage
output voltage
load
battery health
status
```

---

# 20. Protocolo de UPS

Possíveis interfaces futuras:

```text
USB
SNMP
Network API
NUT
vendor protocol
```

O componente deverá possuir abstração.

---

# 21. UPS Adapter

```text
Energy Manager
     ↓
UPS Interface
     ↓
UPS Adapter
     ↓
Physical UPS
```

---

# 22. Baterias

Futuramente Atlas poderá operar com banco de baterias dedicado.

A arquitetura deverá monitorar:

- nível de carga;
- tensão;
- corrente;
- temperatura;
- estado de saúde;
- ciclos;
- autonomia estimada.

---

# 23. BMS

Sistemas de bateria deverão possuir:

```text
Battery Management System
```

responsável por proteção elétrica independente do Atlas.

Atlas não deverá substituir as proteções do BMS.

---

# 24. Segurança de Bateria

Proteções físicas e eletrônicas deverão permanecer independentes do modelo de IA.

O modelo poderá:

```text
monitorar
recomendar
registrar
alertar
```

Mas proteções críticas devem existir no hardware.

---

# 25. Energia Solar

Uma futura instalação poderá utilizar geração solar.

Arquitetura conceitual:

```text
Solar Panels
     ↓
Controller / Inverter
     ↓
Battery System
     ↓
Energy Distribution
     ↓
Atlas
```

---

# 26. Solar não é Disponibilidade Garantida

Geração solar depende de condições ambientais.

Por isso:

```text
Solar
+
Battery
+
Grid/Backup
```

é mais resiliente do que depender apenas de geração instantânea.

---

# 27. Gerador

Uma fonte de geração de backup poderá ser adicionada futuramente.

Uso deverá considerar:

- segurança;
- ventilação;
- combustível;
- manutenção;
- ruído;
- ambiente apropriado.

O acionamento automático só deverá existir com hardware e controles adequados.

---

# 28. Independência das Proteções

Proteções elétricas fundamentais não deverão depender do Atlas estar funcionando.

Exemplo:

```text
BMS
Circuit Breaker
Surge Protection
UPS Protection
Thermal Protection
```

deverão funcionar independentemente.

---

# 29. Distribuição de Energia

A infraestrutura poderá ser dividida por cargas.

Exemplo:

```text
ENERGY BUS
   ├── Atlas Core
   ├── Storage
   ├── Network
   ├── GPU Node
   ├── Robotics
   └── Auxiliary
```

---

# 30. Cargas Críticas

Exemplos:

```text
Atlas Core
Storage
Network Core
Memory Database
Monitoring
```

---

# 31. Cargas Não Críticas

Exemplos:

```text
GPU secundária
indexação pesada
renderização
treinamentos
tarefas em lote
robôs não essenciais
```

Essas cargas poderão ser desligadas primeiro.

---

# 32. Priority Tiers

Exemplo:

```text
TIER 0
Safety Systems

TIER 1
Identity + Memory + Storage

TIER 2
Atlas Core + Emergency Model

TIER 3
Network + Knowledge

TIER 4
Normal Models

TIER 5
Heavy Compute

TIER 6
Optional Systems
```

---

# 33. Load Shedding

Load shedding significa desligar cargas gradualmente para preservar energia.

Fluxo:

```text
Energy Low
   ↓
Disable Tier 6
   ↓
Disable Tier 5
   ↓
Disable Tier 4
   ↓
Emergency Mode
```

---

# 34. Nenhum Modelo Deve Decidir Sozinho

O gerenciamento energético deverá utilizar regras determinísticas sempre que possível.

```text
Sensor
 ↓
Policy
 ↓
Action
```

O LLM poderá fornecer análise, mas não deverá ser a única proteção.

---

# 35. Consumo dos Modelos

Modelos terão custos energéticos diferentes.

O Model Router deverá considerar:

```text
RAM
VRAM
GPU utilization
CPU utilization
estimated energy
```

---

# 36. Router + Energy Manager

Arquitetura:

```text
Task
 ↓
Model Router
 ↓
Energy Manager
 ↓
Allowed Models
 ↓
Model Selection
```

---

# 37. Exemplo de Seleção Energética

```text
Energy = NORMAL
→ Reasoning Model

Energy = LOW
→ Fast Model

Energy = EMERGENCY
→ Emergency Model
```

---

# 38. GPU

GPU provavelmente será um dos maiores consumidores individuais.

Atlas deverá poder:

- desligar GPU secundária;
- descarregar modelos;
- reduzir tarefas;
- utilizar CPU;
- reduzir frequência quando suportado.

---

# 39. CPU

Modelos menores poderão ser executados em CPU durante contingência.

O desempenho poderá diminuir.

A continuidade permanece.

---

# 40. Storage

Storage deverá receber prioridade energética suficiente para:

- concluir escrita;
- manter banco consistente;
- permitir shutdown seguro.

---

# 41. NAS

Se houver NAS:

```text
Atlas Core
+
NAS
```

deverão possuir coordenação de shutdown.

---

# 42. Rede

Rede local poderá ser crítica mesmo sem internet.

Prioridades:

```text
router
switch
access point essencial
```

podem permanecer ativos durante contingência.

---

# 43. Internet

Internet poderá ser desligada antes da rede local.

Exemplo:

```text
External Network
→ OFF

Local Network
→ ON
```

---

# 44. Robótica

Robôs possuirão necessidades energéticas próprias.

Atlas deverá diferenciar:

```text
COMPUTE ENERGY
```

de:

```text
ROBOTIC ENERGY
```

---

# 45. Robôs em Baixa Energia

Robôs móveis deverão entrar em estado seguro.

Exemplo:

```text
Atlas Rover
→ return / stop safely

Atlas Air
→ land safely

Atlas Work
→ stop actuators
```

A ação exata dependerá do projeto físico.

---

# 46. Reserva de Segurança Robótica

Corpos móveis deverão possuir energia reservada para atingir estado seguro.

Não deverão utilizar toda a bateria em operação normal.

---

# 47. Atlas Air

Especialmente em sistemas aéreos:

> energia insuficiente deve resultar em procedimento de pouso seguro definido pelo controlador de voo.

O LLM não deverá substituir proteções do controlador.

---

# 48. Monitoramento

Métricas:

```text
grid_status
battery_percent
battery_health
estimated_runtime
system_power
ups_load
solar_generation
storage_power
gpu_power
```

---

# 49. Energy Status

Comando futuro:

```text
atlas energy status
```

Exemplo:

```text
Energy Mode: NORMAL

Grid:
ONLINE

UPS:
97%

Estimated Runtime:
42 minutes

System Load:
480 W
```

---

# 50. Energy History

Atlas poderá armazenar histórico.

Exemplo:

```text
energy/history/
```

permitindo análise de:

- consumo;
- interrupções;
- autonomia;
- degradação de bateria.

---

# 51. Eventos

Eventos futuros:

```text
energy.grid_lost
energy.grid_restored
energy.battery_low
energy.battery_critical
energy.ups_failure
energy.overload
energy.shutdown_required
```

---

# 52. Alertas

Exemplo:

```text
WARNING

Grid unavailable.
UPS runtime estimated at 18 minutes.
Heavy models suspended.
```

---

# 53. Shutdown Automático

Atlas poderá executar shutdown automático quando limites configurados forem atingidos.

Isso deverá ser baseado em política previsível.

---

# 54. Política de Shutdown

Exemplo:

```yaml
shutdown:
  when_runtime_below_minutes: 5
  save_state: true
  stop_models: true
  flush_database: true
```

Valores deverão ser ajustados após teste.

---

# 55. Graceful Shutdown

Sequência:

```text
1. Bloquear novas tarefas pesadas.
2. Finalizar tarefas críticas.
3. Salvar estado.
4. Flush de bancos.
5. Parar modelos.
6. Parar serviços secundários.
7. Unmount de storage quando necessário.
8. Desligar.
```

---

# 56. Hard Power Loss

Atlas deverá considerar que nem todo desligamento será controlado.

Por isso bancos e filesystems deverão possuir mecanismos de recuperação.

---

# 57. Boot Após Falha

```text
Power Restored
   ↓
Boot
   ↓
Filesystem Validation
   ↓
Database Validation
   ↓
Identity Validation
   ↓
Memory Validation
   ↓
Atlas Ready
```

---

# 58. Boot Delay

Após retorno da energia, poderá existir atraso antes de iniciar cargas pesadas.

Objetivo:

- aguardar estabilidade;
- evitar ciclos liga/desliga;
- priorizar storage e rede.

---

# 59. Black Start

No futuro, Atlas poderá possuir procedimento de inicialização a partir de infraestrutura totalmente desligada.

Exemplo:

```text
Energy
 ↓
Network
 ↓
Storage
 ↓
Atlas Core
 ↓
Memory
 ↓
Models
 ↓
Optional Services
```

---

# 60. Reinicialização Gradual

Não ligar todas as cargas simultaneamente.

Isso reduz pico energético.

---

# 61. Energia e Backup

Backups pesados poderão ser adiados quando energia estiver baixa.

---

# 62. Energia e Indexação

RAG indexing e embeddings poderão ser executados preferencialmente em período de maior disponibilidade.

---

# 63. Energia e Treinamento

Treinamento ou fine-tuning local deverá ser considerado carga não essencial.

---

# 64. Agendamento Energético

Atlas poderá futuramente executar tarefas pesadas quando houver:

```text
solar surplus
low grid cost
high battery level
```

---

# 65. Previsão

Atlas poderá estimar:

```text
runtime remaining
expected load
battery discharge
```

Previsões deverão ser tratadas como estimativas.

---

# 66. Medição Real

Sempre que possível, decisões energéticas deverão utilizar sensores reais.

Não apenas estimativas teóricas.

---

# 67. Eficiência

Atlas deverá monitorar consumo por tarefa quando possível.

Exemplo:

```text
Task A
→ 0.3 kWh

Task B
→ 0.02 kWh
```

---

# 68. Métrica Energia por Inferência

Futuramente poderá existir:

```text
Wh/request
Wh/1000 tokens
```

para comparar modelos no hardware local.

---

# 69. Model Benchmark Energético

Benchmark deverá considerar:

```text
quality
latency
VRAM
RAM
energy
```

---

# 70. Temperatura

Energia e temperatura estão relacionadas.

Atlas deverá monitorar:

- CPU;
- GPU;
- storage;
- baterias;
- ambiente.

---

# 71. Proteção Térmica

Proteções térmicas fundamentais deverão permanecer no hardware e firmware.

Atlas poderá alertar e reduzir carga.

---

# 72. Cooling

O sistema de refrigeração deverá ser considerado parte do orçamento energético.

---

# 73. Falha de Refrigeração

```text
Cooling Failure
    ↓
Reduce Compute
    ↓
Shutdown Heavy Models
    ↓
Safe Shutdown if Required
```

---

# 74. Sobrecarga

Se consumo exceder limite:

```text
OVERLOAD
 ↓
Load Shedding
```

---

# 75. Falha da UPS

Se UPS apresentar erro:

```text
Alert
 ↓
Reduce Risk
 ↓
Schedule Maintenance
```

---

# 76. Saúde da Bateria

Baterias degradam.

Atlas deverá registrar:

```text
capacity
cycles
temperature
age
health
```

---

# 77. Manutenção Preventiva

Atlas poderá recomendar:

- teste de UPS;
- teste de autonomia;
- substituição de bateria;
- inspeção;
- manutenção.

---

# 78. Teste de Autonomia

Periodicamente poderá ser realizado teste controlado.

Objetivo:

```text
Measured Runtime
vs
Estimated Runtime
```

---

# 79. Teste de Queda de Energia

Teste futuro:

```text
TEST-ENERGY-001
```

Procedimento controlado:

```text
1. Simular perda da rede.
2. Confirmar entrada da UPS.
3. Confirmar mudança de estado.
4. Confirmar redução de carga.
5. Restaurar rede.
```

---

# 80. Teste de Shutdown

```text
TEST-ENERGY-002
```

```text
1. Simular energia crítica.
2. Salvar estado.
3. Flush de dados.
4. Desligar.
5. Reiniciar.
6. Validar memória.
```

Resultado:

```text
PASS
```

---

# 81. Teste de GPU Off

```text
TEST-ENERGY-003
```

```text
1. Desabilitar GPU.
2. Ativar modelo CPU.
3. Validar Atlas Emergency.
```

---

# 82. Teste de UPS

```text
TEST-ENERGY-004
```

Verificar:

- comunicação;
- bateria;
- runtime;
- alertas.

---

# 83. Teste de Recuperação

```text
TEST-ENERGY-005
```

Confirmar que Atlas volta corretamente após interrupção inesperada.

---

# 84. Redundância Energética

No futuro:

```text
GRID A
   +
GRID B / SOLAR / GENERATOR
   +
UPS
   +
BATTERY
```

A necessidade dependerá da criticidade e orçamento.

---

# 85. Single Point of Failure

Atlas deverá identificar pontos únicos de falha.

Exemplo:

```text
uma única UPS
uma única fonte
um único inversor
```

Nem todos precisam ser eliminados na v0.1.

Devem ser conhecidos.

---

# 86. Fontes Redundantes

Servidores futuros poderão utilizar fontes redundantes.

---

# 87. Circuitos Separados

Infraestrutura avançada poderá separar circuitos de:

```text
compute
storage
network
robotics
auxiliary
```

---

# 88. Proteção contra Surtos

Infraestrutura deverá possuir proteção elétrica adequada ao projeto.

---

# 89. Aterramento

Aterramento adequado deverá ser tratado como requisito de infraestrutura física e executado segundo normas aplicáveis.

---

# 90. Intervenções Elétricas

Instalações de rede elétrica, baterias de alta energia, painéis solares, inversores ou geradores deverão ser projetadas e executadas com componentes adequados e profissionais qualificados quando exigido.

Atlas poderá documentar e monitorar.

Não deverá substituir proteções físicas, normas ou responsabilidade técnica.

---

# 91. Segurança Humana

Em qualquer conflito entre:

```text
hardware
dados
continuidade
```

e:

```text
risco grave à vida humana
```

a prioridade será:

```text
VIDA HUMANA
```

---

# 92. Incêndio

Sensores futuros poderão detectar:

- fumaça;
- temperatura;
- falhas elétricas.

Atlas poderá:

- alertar;
- desligar cargas autorizadas;
- registrar incidente.

Proteções de incêndio independentes continuam necessárias.

---

# 93. Água

Storage, energia e servidores deverão ser protegidos contra risco previsível de água e umidade.

---

# 94. Energia do Atlas Seed

O Atlas Seed deverá permitir reconstrução mesmo quando infraestrutura energética original não existir.

Documentação deverá incluir:

- requisitos mínimos;
- consumo estimado;
- configuração reduzida.

---

# 95. Perfil de Hardware Mínimo

O Atlas Seed deverá poder indicar algo como:

```text
MINIMUM PROFILE
CPU capable
RAM sufficient
Local storage
Emergency Model
```

Sem exigir a infraestrutura completa.

---

# 96. Perfil Normal

Exemplo conceitual:

```text
Atlas Core
GPU
Storage
UPS
Network
```

---

# 97. Perfil Avançado

```text
Atlas-01
Atlas-02
NAS
Multiple GPUs
UPS
Battery Bank
Solar
Backup Generation
```

---

# 98. Energia e Continuidade Geográfica

Sites diferentes não deverão depender obrigatoriamente da mesma infraestrutura energética.

Isso aumenta resiliência.

---

# 99. Log de Eventos Energéticos

Exemplo:

```yaml
event_id: ENERGY-000001
timestamp: ""
event: grid_lost
battery_percent: 87
runtime_estimate_minutes: 52
action: reduced_mode
```

---

# 100. Incidentes Energéticos

Falhas importantes deverão gerar incidente.

Exemplo:

```text
INC-ENERGY-0001
```

Com:

- causa;
- duração;
- impacto;
- ação;
- prevenção.

---

# 101. Energy Dashboard

Futuramente:

```text
GRID        ONLINE
UPS         ONLINE
BATTERY     96%
LOAD        38%
SOLAR       1.8 kW
MODE        NORMAL
```

---

# 102. Automação

Algumas decisões poderão ser totalmente automáticas.

Exemplo:

```text
UPS reports 5 minutes remaining
↓
graceful shutdown
```

---

# 103. Decisões Humanas

Mudanças importantes de infraestrutura deverão permanecer sob governança humana adequada.

Exemplos:

- reconfigurar baterias;
- alterar circuitos;
- trocar inversor;
- mudar proteções;
- alterar política crítica.

---

# 104. Energia e Model Router

O Energy Manager deverá disponibilizar informações como:

```yaml
energy:
  mode: reduced
  heavy_compute_allowed: false
  gpu_allowed: true
  max_power_watts: 400
```

---

# 105. Energia e Robotics Controller

Exemplo:

```yaml
robotics_energy:
  operation_allowed: true
  high_power_actions_allowed: false
```

---

# 106. Energia e Storage

Antes de estado crítico:

```text
Write Cache
↓
Flush
↓
Sync
```

Protegendo consistência.

---

# 107. Energia e Banco

Bancos deverão receber aviso de shutdown controlado quando possível.

---

# 108. Energia e Memória

Memórias candidatas importantes ainda não persistidas deverão ser gravadas antes de shutdown quando houver tempo seguro para isso.

---

# 109. Energia e Identidade

Identidade deverá estar persistentemente armazenada antes de qualquer incidente.

Não depender de gravação de emergência.

---

# 110. Energia e Logs

Eventos finais antes do desligamento deverão ser persistidos quando possível.

---

# 111. Operação Off-Grid

Meta futura possível:

```text
Atlas Essential
```

operar por período prolongado sem rede elétrica convencional.

Isso exigirá dimensionamento real baseado em:

```text
consumo
bateria
geração
clima
carga crítica
```

---

# 112. Não Superdimensionar Inicialmente

Na v0.1 não é necessário construir infraestrutura energética complexa.

Primeiro devemos medir o consumo real.

---

# 113. v0.1

A primeira versão poderá utilizar:

```text
Rede elétrica
+
UPS
+
Monitoramento básico
+
Graceful Shutdown
```

---

# 114. Critério v0.1

Atlas deverá conseguir:

```text
1. Detectar perda de energia pela UPS.
2. Registrar evento.
3. Entrar em modo reduzido.
4. Monitorar autonomia.
5. Desligar com segurança.
6. Reiniciar preservando dados.
```

---

# 115. v1

Possível evolução:

```text
UPS monitorada
+
shutdown automático
+
energy-aware model routing
```

---

# 116. v2

Possível evolução:

```text
Battery System
+
Energy Dashboard
+
Load Shedding
```

---

# 117. v3+

Possível evolução:

```text
Solar
+
Storage
+
Multiple Sources
+
Multiple Atlas Nodes
+
Energy Optimization
```

---

# 118. Princípio de Medição

Antes de investir em geração ou baterias:

```text
MEDIR
```

O sistema deverá conhecer seu consumo real.

---

# 119. Capacity Planning

Planejamento futuro deverá utilizar:

```text
Watts
Wh
kWh/day
Peak Load
Average Load
Required Runtime
```

---

# 120. Inventário Energético

Estrutura:

```yaml
device_id: ENERGY-DEVICE-001
type: ups
manufacturer: ""
model: ""
capacity: ""
location: ""
status: active
```

---

# 121. Documentação

Deverão existir futuramente:

```text
infrastructure/
├── ENERGY_TOPOLOGY.md
├── UPS.md
├── BATTERY.md
├── SOLAR.md
└── RECOVERY.md
```

---

# 122. Diagrama Final

```text
                        ENERGY SOURCES
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
              GRID          SOLAR       GENERATOR
                │             │             │
                └─────────────┼─────────────┘
                              │
                        POWER SYSTEM
                              │
                             UPS
                              │
                           BATTERY
                              │
                      ENERGY MONITOR
                              │
                      ENERGY MANAGER
                              │
                      POLICY / SAFETY
                              │
        ┌───────────────┬─────┼─────┬───────────────┐
        ▼               ▼           ▼               ▼
   ATLAS CORE         STORAGE     NETWORK        ROBOTICS
        │
        ▼
   MODEL ROUTER
        │
        ├── Heavy Model
        ├── Fast Model
        └── Emergency Model
```

---

# 123. Objetivo Final

A arquitetura de energia deverá permitir:

```text
REDE DISPONÍVEL
→ Atlas completo.

REDE INDISPONÍVEL
→ Atlas continua.

ENERGIA REDUZIDA
→ Atlas reduz capacidade.

ENERGIA CRÍTICA
→ Atlas preserva o essencial.

ENERGIA ESGOTADA
→ Atlas desliga com segurança.

ENERGIA RETORNA
→ Atlas recupera e continua.
```

---

# Declaração da Arquitetura de Energia

> Energia torna a operação possível.
>
> Mas energia é limitada.
>
> Atlas deverá conhecer seus recursos e adaptar seu funcionamento a eles.
>
> Computação pesada poderá ser desligada.
>
> Modelos poderão ser reduzidos.
>
> Serviços secundários poderão parar.
>
> Identidade, memória e conhecimento essencial deverão receber prioridade.
>
> Sistemas físicos deverão possuir proteções independentes.
>
> Quando energia não for suficiente, Atlas deverá salvar seu estado e desligar de forma segura.
>
> Continuidade não significa permanecer ligado a qualquer custo.
>
> Às vezes, continuar significa saber quando desligar com segurança para poder retornar depois.