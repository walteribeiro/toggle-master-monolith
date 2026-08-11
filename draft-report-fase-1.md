# Relatório — Tech Challenge Fase 1 (ToggleMaster)

**Integrantes do Grupo:**
- **Mayara Finatto** — RM375879
- **Walter Ribeiro** — RM [Preencher RM do Walter]

---

## 1. Análise Arquitetural: Aplicação Monolítica

O **ToggleMaster** é uma plataforma de *Feature Flag as a Service*. Em sua primeira fase (MVP), ele foi construído como um **monolito**.

### 1.1. Características Monolíticas Identificadas no Código
- **Unidade Única de Código**: O arquivo [`app.py`](file:///c:/Users/mayar/dev/pos-grad-devops/toggle-master-monolith/app.py) concentra todas as responsabilidades — roteamento HTTP, validações, regras de negócio, queries SQL (`psycopg2`) e inicialização do banco (`init-db`).
- **Artefato Único de Deploy**: Todo o sistema é empacotado em uma única imagem Docker ([`Dockerfile`](file:///c:/Users/mayar/dev/pos-grad-devops/toggle-master-monolith/Dockerfile)) e executado como um único processo Gunicorn.
- **Base de Dados Compartilhada**: Todos os endpoints interagem com a mesma base PostgreSQL e com a tabela `flags`.
- **Escalabilidade em Bloco**: Para aumentar a capacidade de leitura de flags, é necessário replicar o processo completo da aplicação.

### 1.2. Vantagens e Desvantagens no Cenário Atual

| Dimensão | Vantagens no MVP | Desvantagens no Crescimento |
|---|---|---|
| **Desenvolvimento** | Alta velocidade inicial, curva de aprendizado baixa e facilidade para refatorar. | Risco de acoplamento excessivo e acúmulo de débito técnico conforme novas regras surgirem. |
| **Operação e Deploy** | Deploy simples (`docker compose up` ou container único na EC2). | Raio de explosão total: qualquer bug em um endpoint pode derrubar a aplicação inteira. |
| **Infraestrutura** | Menor custo operacional e sem overhead de comunicação via rede entre serviços. | Impossibilidade de escalar de forma granular os recursos apenas para os endpoints de maior tráfego (`GET /flags/<nome>`). |

---

## 2. Análise Prática dos 12 Fatores (12-Factor App)

Análise crítica baseada no código atual e nas percepções iniciais registradas em [`relatorio.md`](file:///c:/Users/mayar/dev/pos-grad-devops/toggle-master-monolith/relatorio.md).

### I. Base de Código (Codebase)
- **Status**: ✅ **Atende totalmente**
- **Percepção Inicial**: *"usamos Git"* (Correto)
- **Análise Técnica**: Existe um único repositório Git rastreado por controle de versão. A partir desta base única, são realizados múltiplos deploys em diferentes ambientes (desenvolvimento local com Docker Compose e produção na AWS EC2).

### II. Dependências (Dependencies)
- **Status**: 🟡 **Atende parcialmente**
- **Percepção Inicial**: *"versão do python definida na docker image"* (Parcialmente correto)
- **Análise Técnica**: O isolamento de runtime é garantido pela imagem Docker (`python:3.9-slim`), e as bibliotecas Python são declaradas via [`requirements.txt`](file:///c:/Users/mayar/dev/pos-grad-devops/toggle-master-monolith/requirements.txt).
- **Ponto de Melhoria**: Pinar as versões exatas das dependências no `requirements.txt` (ex.: `Flask==2.3.3`, `gunicorn==21.2.0`, `psycopg2-binary==2.9.9`) para evitar divergências em builds futuros.

### III. Configurações (Config)
- **Status**: ✅ **Atende totalmente**
- **Percepção Inicial**: *"precisamos separar as variáveis (eg.: DB_HOST; POSTGRES_USER)"* (Correto)
- **Análise Técnica**: O código em [`app.py`](file:///c:/Users/mayar/dev/pos-grad-devops/toggle-master-monolith/app.py) lê estritamente todas as configurações de acesso ao banco por variáveis de ambiente (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`). Elas são injetadas via `docker-compose.yaml` localmente e por `export` no ambiente EC2/RDS. Nenhuma credencial está hardcoded no código.

### IV. Serviços de Apoio (Backing Services)
- **Status**: ✅ **Atende totalmente**
- **Percepção Inicial**: *"a verificar no futuro; algo para logs"* (Ajuste de Conceito)
- **Clarificação**: No 12-Factor, *Serviços de Apoio* referem-se a recursos anexados à rede (como bancos de dados e caches). O PostgreSQL é tratado como um recurso anexo conectado via rede (`DB_HOST`). Trocar o banco local do Docker Compose para o Amazon RDS gerenciado não exige nenhuma alteração no código da aplicação.

### V. Build, Release, Run
- **Status**: 🟡 **Atende parcialmente**
- **Percepção Inicial**: *"a criar: pipeline"* (Correto)
- **Análise Técnica**: As três etapas são conceitualmente separadas:
  - **Build**: Construção da imagem Docker com a instalação das dependências.
  - **Release**: Combinação da imagem compilada com as variáveis de ambiente do destino.
  - **Run**: Execução do contêiner rodando [`entrypoint.sh`](file:///c:/Users/mayar/dev/pos-grad-devops/toggle-master-monolith/entrypoint.sh) e Gunicorn.
- **Ponto de Melhoria**: Atualmente a execução é manual; recomenda-se automatizar o ciclo Build/Release/Run utilizando um pipeline de CI/CD (ex.: GitHub Actions).

### VI. Processos (Processes)
- **Status**: ✅ **Atende totalmente**
- **Percepção Inicial**: *"já separados entre banco e aplicação (docker-compose declara app e db)"* (Correto)
- **Análise Técnica**: A aplicação é *stateless* (sem estado). O processo da API não armazena dados em memória nem no sistema de arquivos local entre requisições; todo o estado persistente reside no banco PostgreSQL.

### VII. Vinculação de Portas (Port Binding)
- **Status**: ✅ **Atende totalmente**
- **Percepção Inicial**: *"usando porta 5000:5000"* (Correto)
- **Análise Técnica**: O ToggleMaster é totalmente autônomo (self-contained) e exporta seus serviços via port binding na porta `5000` via Gunicorn (`EXPOSE 5000`), sem depender de um servidor de aplicação web externo injetado.

### VIII. Concorrência (Concurrency)
- **Status**: 🟡 **Atende parcialmente**
- **Percepção Inicial**: *"sem definições para escalar, necessário criar"* (Correto)
- **Análise Técnica**: O servidor Gunicorn já oferece concorrência no nível de processo (através de múltiplos *workers*). No entanto, para escalabilidade horizontal da infraestrutura, é necessário adicionar um Load Balancer (AWS ALB) e um Auto Scaling Group para distribuir tráfego entre múltiplas instâncias EC2.

### IX. Descartabilidade (Disposability)
- **Status**: ✅ **Atende totalmente**
- **Percepção Inicial**: *"possível iniciar e parar sem problemas; enquanto volume for mantido, dados são mantidos"* (Correto)
- **Análise Técnica**: Os processos sobem rapidamente e encerram graciosamente. O script [`entrypoint.sh`](file:///c:/Users/mayar/dev/pos-grad-devops/toggle-master-monolith/entrypoint.sh) utiliza `pg_isready` para aguardar a prontidão do banco antes de iniciar o servidor, garantindo resiliência na inicialização.

### X. Paridade entre Desenvolvimento e Produção (Dev/Prod Parity)
- **Status**: 🟡 **Atende parcialmente**
- **Percepção Inicial**: *"ainda não há separação de ambientes"* (Correto)
- **Análise Técnica**: Há paridade no motor de banco (PostgreSQL em dev e prod). Contudo, a execução local roda via Docker Compose, enquanto em produção na AWS o deploy inicial roda diretamente na EC2.
- **Ponto de Melhoria**: Adotar Infraestrutura como Código (Terraform) para criar ambientes de Staging e Produção idênticos e padronizar o deploy de contêineres na nuvem (ex.: AWS ECS).

### XI. Logs
- **Status**: ✅ **Atende no código / Necessita agregação em infra**
- **Percepção Inicial**: *"não atende ainda, precisamos armazenar os logs usando alguma ferramenta"* (Ajuste de Conceito)
- **Clarificação**: No 12-Factor, a aplicação **nunca** deve gerenciar ou armazenar seus próprios arquivos de log. Ela deve emitir o fluxo de eventos não-formatado diretamente na saída padrão (`stdout`/`stderr`). O `app.py` e o Gunicorn já fazem isso perfeitamente. Cabe à infraestrutura (AWS CloudWatch Logs / Docker Logging Driver) capturar e armazenar esse fluxo.

### XII. Processos Administrativos (Admin Processes)
- **Status**: ✅ **Atende totalmente**
- **Percepção Inicial**: *"parcialmente coberto; não há rollback definido"* (Correto)
- **Análise Técnica**: A inicialização do banco (`flask init-db`) é executada no mesmo ambiente e imagem do código através do [`entrypoint.sh`](file:///c:/Users/mayar/dev/pos-grad-devops/toggle-master-monolith/entrypoint.sh). Para evoluções futuras, recomenda-se adotar uma ferramenta de migração de banco (como Alembic/Flask-Migrate) para gerenciar alterações de schema e scripts de rollback.

---

## 3. Resumo da Avaliação e Próximos Passos para a Fase 1 (AWS)

1. **Validação das Anotações do Time**: As percepções em [`relatorio.md`](file:///c:/Users/mayar/dev/pos-grad-devops/toggle-master-monolith/relatorio.md) estão **muito boas e acertadas**. As únicas duas correções necessárias foram de ajuste de conceito formal do 12-Factor:
   - **Fator IV (Serviços de Apoio)** trata de recursos de rede anexados (o PostgreSQL/RDS), e não da ferramenta de logs.
   - **Fator XI (Logs)** exige apenas que o código envie os logs para `stdout`/`stderr` (o que a aplicação já faz); a ferramenta de armazenamento/agregação é responsabilidade da infraestrutura da nuvem (CloudWatch).

2. **Recomendações para a Entrega**:
   - Manter as variáveis de ambiente seguras (sem credenciais em repositório).
   - Configurar o **Security Group** da EC2 permitindo portas `5000` (API) e `22` (SSH).
   - Configurar o **Security Group** do RDS permitindo porta `5432` apenas vindo do Security Group da EC2.