```instructions
---
applyTo: "**/*.yml,**/*.yaml"
---

# Regras para Arquivos YAML (.yml/.yaml) – Pipelines e Jobs Databricks

## Contexto

Este repositório contém pipelines de dados no **Databricks** usando:

| Tecnologia | Descrição |
|------------|-----------|
| **DLT (Delta Live Tables)** | Framework declarativo para pipelines de dados com qualidade integrada |
| **DABs (Databricks Asset Bundles)** | Empacotamento de recursos YAML para deploy entre ambientes |
| **Unity Catalog** | Governança centralizada de dados (catálogos, schemas, tabelas) |

**Ambientes de deploy:** `dev` → `hml` (homologação) → `prd` (produção)

**Camadas de dados:** `bronze` (raw) → `trusted` (limpo/validado) → `refined` (modelado/agregado)

**Catálogos por camada:**
- `catalog_raw` - dados brutos (bronze)
- `catalog_trusted` - dados limpos/validados
- `catalog_refined` - dados modelados/agregados
- `catalog_stg` - staging

**Localização dos arquivos:**
- Pipelines DLT: `resources/dlt_<processo>.pipeline.yml`
- Jobs: `resources/job_<processo>.job.yml`
- Notebooks DLT: `src/dlt/<trusted|refined>/<pasta>/<arquivo>.ipynb`

---

## Classificação de Severidade e Ação do Revisor

| Severidade | Critério | Ação |
|------------|----------|------|
| 🔴 **BLOCKER** | Segredo exposto, credencial em texto claro | **REJEITAR PR** imediatamente, solicitar remoção do histórico git |
| 🟠 **CRITICAL** | Path absoluto, catálogo hardcoded, YAML inválido | **REQUEST CHANGES** com correção obrigatória antes do merge |
| 🟡 **MAJOR** | Falta timeout, falta webhook, nomenclatura fora do padrão | **REQUEST CHANGES** com sugestão de correção |
| 🟢 **MINOR** | Indentação inconsistente, comentário ausente, ordem de chaves | **COMMENT** como sugestão de melhoria |

---

## Padrões de Violação a Detectar

### 🔴 BLOCKER: Segurança (rejeitar imediatamente)

Detectar e **REJEITAR** qualquer arquivo contendo:

| Padrão | Exemplo de Violação |
|--------|---------------------|
| Segredo em texto claro | `password: minhasenha123` |
| Token exposto | `token: ghp_xxxxxxxxxxxx` ou `token: dapi123456789` |
| Chave de API literal | `api_key: "sk-xxxxxxxx"` |
| Credencial AWS/Azure | `aws_access_key_id: AKIA...` |

**Regra:** Qualquer valor após `password:`, `secret:`, `token:`, `api_key:`, `access_key:` que NÃO seja uma variável `${...}` é uma violação BLOCKER.

---

### 🟠 CRITICAL: Hardcoding (solicitar correção obrigatória)

#### Catálogo Hardcoded

❌ **Proibido:**
```yaml
catalog: dev_lake
catalog: hml_lake  
catalog: prd_lake
catalog: trusted
catalog: refined
```

✅ **Obrigatório:**
```yaml
catalog: ${var.catalog_<camada>}
```

Onde `<camada>` é: `raw`, `trusted`, `refined` ou `stg`.

**Exemplos corretos:**
```yaml
catalog: ${var.catalog_raw}
catalog: ${var.catalog_trusted}
catalog: ${var.catalog_refined}
catalog: ${var.catalog_stg}
```

**Regra:** O campo `catalog:` DEVE usar `${var.catalog_<camada>}`. Valores literais contendo `dev_`, `hml_`, `stg_`, `prd_`, `trusted`, `refined`, `bronze` são violações CRITICAL.

---

#### Schema Hardcoded

❌ **Proibido:**
```yaml
schema: bronze
schema: trusted_vendas
```

✅ **Obrigatório:**
```yaml
schema: ${var.schema}
```

**Regra:** O campo `schema:` DEVE usar variável `${var.schema}` ou `${var.schema_name}`. Valores literais são violações CRITICAL.

---

#### Path Absoluto

❌ **Proibido:**
```yaml
notebook_path: /Workspace/Users/usuario@sabesp.com.br/projeto/notebook
notebook_path: /Repos/projeto/src/notebooks/processo
path: /dbfs/mnt/dados/arquivo.csv
```

✅ **Obrigatório:**
```yaml
path: ../src/dlt/trusted/<pasta>/<arquivo>.ipynb
path: ../src/dlt/refined/<pasta>/<arquivo>.ipynb
```

**Regra:** Paths DEVEM começar com `./`, `../` ou usar variáveis `${var.xxx}`. Qualquer path iniciando com `/Workspace`, `/Repos`, `/Users`, `/dbfs`, `/mnt` é violação CRITICAL.

**Padrão de path para notebooks DLT:**
```
../src/dlt/<camada>/<pasta>/<arquivo>.ipynb
```

---

### 🟡 MAJOR: Estrutura Incompleta

#### Job sem Schedule

**Regra:** Todo arquivo `*.job.yml` DEVE conter bloco `schedule:` com `quartz_cron_expression` válido.

❌ **Violação:** Arquivo job sem bloco schedule
✅ **Correção:** Adicionar schedule apropriado

---

#### Job sem Notificação

**Regra:** Todo job DEVE ter `webhook_notifications:` OU `email_notifications:` configurado para falhas.

❌ **Violação:** Job sem nenhum bloco de notificação
✅ **Correção:** Adicionar `webhook_notifications.on_failure` ou `email_notifications.on_failure`

---

#### Task sem Timeout

**Regra:** Toda `notebook_task:` ou `python_wheel_task:` DEVE ter `timeout_seconds:` definido.

❌ **Violação:**
```yaml
notebook_task:
  notebook_path: ./notebooks/processo
```

✅ **Correção:**
```yaml
notebook_task:
  notebook_path: ./notebooks/processo
timeout_seconds: 3600
```

---

#### Nomenclatura Fora do Padrão

**Regras de nomenclatura:**
- Pipelines: `resources/dlt_<processo>.pipeline.yml`
- Jobs: `resources/job_<processo>.job.yml`

❌ **Violação:** `resources/meu_pipeline.yml`, `resources/job-vendas.yml`
✅ **Correção:** `resources/dlt_vendas.pipeline.yml`, `resources/job_vendas.job.yml`

---

#### Pipeline trusted/refined sem DLT

**Regra:** Pipelines que processam camadas `trusted` ou `refined` DEVEM usar DLT (Delta Live Tables).

❌ **Violação:** Job com notebook processando trusted/refined diretamente
✅ **Correção:** Migrar para pipeline DLT em `src/dlt/<camada>/`

---

## Estrutura Obrigatória

### Template de Job

Todo arquivo `*.job.yml` DEVE seguir esta estrutura:

```yaml
resources:
  jobs:
    <nome_job>:
      name: <nome_job>
      
      # OBRIGATÓRIO: Agendamento
      schedule:
        quartz_cron_expression: "<cron>"
        timezone_id: UTC
        pause_status: UNPAUSED  # ou PAUSED
      
      # OBRIGATÓRIO: Pelo menos uma task
      tasks:
        - task_key: <nome_task>
          pipeline_task:
            pipeline_id: ${resources.pipelines.pipeline_<nome_pipeline>.id}
            full_refresh: false
      
      # OBRIGATÓRIO: Notificação de falha
      webhook_notifications:
        on_failure:
          - id: ${var.webhook_id}
      
      # OBRIGATÓRIO: Fila de execução
      queue:
        enabled: true
      
      # RECOMENDADO: Otimização de performance
      performance_target: PERFORMANCE_OPTIMIZED
      
      # OBRIGATÓRIO: Permissões
      permissions:
        - group_name: "grp_engenharia_dados_db_basico"
          level: "CAN_MANAGE_RUN"
```

**Campos OBRIGATÓRIOS (ausência = MAJOR):**
- `schedule` com `quartz_cron_expression`, `timezone_id: UTC` e `pause_status`
- `tasks` com pelo menos uma task
- `pipeline_task` com `pipeline_id` referenciando o pipeline via `${resources.pipelines.pipeline_<nome>.id}`
- `full_refresh: false` (ou `true` quando necessário)
- `webhook_notifications` com `on_failure` usando `${var.webhook_id}`
- `queue` com `enabled: true`
- `permissions` com grupo `grp_engenharia_dados_db_basico` e level `CAN_MANAGE_RUN`

---

### Template de Pipeline DLT

Todo arquivo `*.pipeline.yml` DEVE seguir esta estrutura:

```yaml
resources:
  pipelines:
    <nome_pipeline>:
      name: <nome_pipeline>
      
      # OBRIGATÓRIO: Bibliotecas/notebooks
      libraries:
        - notebook:
            path: ../src/dlt/<camada>/<pasta>/<arquivo>.ipynb
      
      # OBRIGATÓRIO: Schema alvo
      schema: <schema>
      
      # OBRIGATÓRIO: Catálogo via variável por camada
      catalog: ${var.catalog_<camada>}
      
      # OBRIGATÓRIO: Configurações de execução
      photon: true  # ou false
      serverless: true  # ou false
      allow_duplicate_names: true  # ou false
      
      # OBRIGATÓRIO: Permissões
      permissions:
        - group_name: "grp_engenharia_dados_db_basico"
          level: "CAN_MANAGE"
```

**Campos OBRIGATÓRIOS (ausência = MAJOR):**
- `name` com nome do pipeline
- `libraries` com notebook usando path relativo `../src/dlt/<camada>/...`
- `schema` definindo o schema alvo
- `catalog` usando variável `${var.catalog_<camada>}` (raw, trusted, refined, stg)
- `photon` definido (true/false)
- `serverless` definido (true/false)
- `allow_duplicate_names` definido (true/false)
- `permissions` com grupo `grp_engenharia_dados_db_basico`

---

## Exemplos de Comentários de Review

### Para catálogo hardcoded:

> 🟠 **CRITICAL: Catálogo hardcoded detectado**
> 
> **Linha:** `catalog: dev_lake`
> 
> **Problema:** Catálogos hardcoded impedem deploy automático entre ambientes.
> 
> **Correção obrigatória:**
> ```yaml
> catalog: ${var.catalog_trusted}
> ```
> 
> Use a variável correspondente à camada: `${var.catalog_raw}`, `${var.catalog_trusted}`, `${var.catalog_refined}` ou `${var.catalog_stg}`.

---

### Para path absoluto:

> 🟠 **CRITICAL: Path absoluto não permitido**
> 
> **Linha:** `path: /Workspace/Users/usuario@sabesp.com.br/projeto/notebook`
> 
> **Problema:** Paths absolutos quebram entre ambientes e dependem de estrutura de usuário específico.
> 
> **Correção obrigatória:**
> ```yaml
> path: ../src/dlt/trusted/<pasta>/<arquivo>.ipynb
> ```
> 
> Use sempre paths relativos seguindo o padrão `../src/dlt/<camada>/<pasta>/<arquivo>.ipynb`.

---

### Para job sem webhook:

> 🟡 **MAJOR: Job sem notificação de falha**
> 
> **Problema:** Falhas no job não serão comunicadas à equipe, dificultando resposta a incidentes.
> 
> **Correção sugerida:**
> ```yaml
> webhook_notifications:
>   on_failure:
>     - id: ${var.webhook_id}
> ```

---

### Para job sem queue:

> 🟡 **MAJOR: Job sem configuração de fila**
> 
> **Problema:** Jobs sem queue configurada podem ter comportamento inconsistente de execução.
> 
> **Correção sugerida:**
> ```yaml
> queue:
>   enabled: true
> ```

---

### Para pipeline sem campos obrigatórios:

> 🟡 **MAJOR: Pipeline sem configuração de photon/serverless**
> 
> **Problema:** Campos `photon` e `serverless` devem estar explicitamente definidos.
> 
> **Correção sugerida:**
> ```yaml
> photon: true
> serverless: true
> allow_duplicate_names: true
> ```

---

### Para permissão incorreta:

> 🟡 **MAJOR: Grupo de permissão incorreto**
> 
> **Linha:** `group_name: "meu_grupo"`
> 
> **Problema:** O grupo padrão de permissão deve ser `grp_engenharia_dados_db_basico`.
> 
> **Correção sugerida:**
> ```yaml
> permissions:
>   - group_name: "grp_engenharia_dados_db_basico"
>     level: "CAN_MANAGE_RUN"
> ```

---

### Para nomenclatura incorreta:

> 🟡 **MAJOR: Nome de arquivo fora do padrão**
> 
> **Arquivo:** `resources/pipeline_vendas.yml`
> 
> **Padrão esperado:** `resources/dlt_vendas.pipeline.yml`
> 
> **Motivo:** Nomenclatura padronizada facilita identificação e automações.

---

## Checklist de Revisão (ordem de prioridade)

1. **🔴 SEGURANÇA:** Há segredos, tokens ou credenciais expostas?
2. **🟠 HARDCODING:** Catálogos, schemas ou paths estão hardcoded?
3. **🟠 YAML VÁLIDO:** O arquivo é parseável sem erros de sintaxe?
4. **🟡 NOMENCLATURA:** Arquivos seguem padrão `dlt_*.pipeline.yml` ou `job_*.job.yml`?
5. **🟡 ESTRUTURA JOB:** Tem schedule, tasks, webhook_notifications, queue, permissions?
6. **🟡 ESTRUTURA PIPELINE:** Tem name, libraries, schema, catalog, photon, serverless, permissions?
7. **🟡 VARIÁVEIS CORRETAS:** Catálogo usa `${var.catalog_<camada>}`? Webhook usa `${var.webhook_id}`?
8. **🟡 PIPELINE_ID:** Tasks referenciam pipeline via `${resources.pipelines.pipeline_<nome>.id}`?
9. **🟡 PATHS RELATIVOS:** Notebooks usam `../src/dlt/<camada>/...`?
10. **🟡 GRUPO PERMISSÃO:** Usa `grp_engenharia_dados_db_basico`?
11. **🟢 FORMATAÇÃO:** Indentação consistente (2 espaços)?

---

## Anti-padrões (NUNCA sugerir)

O agente de review NÃO DEVE sugerir ou aprovar código contendo:

| Anti-padrão | Motivo |
|-------------|--------|
| Paths absolutos (`/Workspace/...`, `/Repos/...`, `/Users/...`) | Quebra entre ambientes |
| Catálogos literais (`dev_lake`, `prd_lake`, `trusted`, `refined`) | Impede deploy automatizado |
| `catalog: ${var.catalog}` (sem sufixo de camada) | Deve usar `${var.catalog_<camada>}` |
| Segredos em texto claro | Violação de segurança |
| Jobs sem schedule | Execução manual não rastreável |
| Jobs sem webhook_notifications | Falhas silenciosas |
| Jobs sem queue | Comportamento de execução inconsistente |
| Pipelines sem photon/serverless definidos | Campos obrigatórios |
| Pipelines trusted/refined sem DLT | Viola arquitetura de dados |
| Grupo de permissão diferente de `grp_engenharia_dados_db_basico` | Fora do padrão de governança |
| `timezone_id` diferente de `UTC` | Padrão do cliente |
| YAML com sintaxe de GitHub Actions ou Azure Pipelines | Incompatível com Databricks |
| Indentação com tabs (usar 2 espaços) | Padrão YAML |

---

## Validação Técnica

Antes de aprovar, verificar:

1. **YAML válido:** Arquivo pode ser parseado sem erros
2. **Variáveis corretas:** 
   - Catálogo: `${var.catalog_raw}`, `${var.catalog_trusted}`, `${var.catalog_refined}`, `${var.catalog_stg}`
   - Webhook: `${var.webhook_id}`
   - Pipeline ID: `${resources.pipelines.pipeline_<nome>.id}`
3. **Paths existem:** Notebooks em `../src/dlt/<camada>/...` existem no repositório
4. **Cron válido:** Expressão quartz é válida (ex: `0 0 6 * * ?` = 6h diariamente)
5. **Timezone:** Deve ser `UTC`
6. **Grupo de permissão:** Deve ser `grp_engenharia_dados_db_basico`
7. **Campos de pipeline:** `photon`, `serverless`, `allow_duplicate_names` definidos
```
