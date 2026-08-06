# Relatório — Tech Challenge Fase 1 (ToggleMaster)

## 1. Por que a aplicação é considerada um "monolito"?

Analisando o código, o ToggleMaster concentra **todas as responsabilidades em uma única unidade de código e de deploy**:

- **Um único arquivo/processo faz tudo**: o `app.py` contém as rotas HTTP, a validação das requisições, a regra de negócio, o acesso ao banco (SQL embutido nos handlers) e até a criação do schema (`init_db`). Não há separação em módulos ou serviços independentes.
- **Um único artefato de deploy**: a aplicação inteira é empacotada em uma única imagem Docker (`Dockerfile`) e sobe como um único processo Gunicorn. Qualquer alteração — por menor que seja — exige rebuild e redeploy de toda a aplicação.
- **Um único banco de dados compartilhado**: todas as funcionalidades leem e escrevem na mesma base PostgreSQL, na mesma tabela `flags`.
- **Escala em bloco**: não é possível escalar apenas o endpoint mais acessado (ex.: `GET /flags/<nome>`, que seria o mais consultado pelos clientes); replica-se a aplicação inteira.

Ou seja: **um codebase, um processo, um deploy, um banco** — a definição prática de monolito.

### Vantagens dessa abordagem para um MVP

| Vantagem | Por que importa nesta fase |
|---|---|
| **Simplicidade de desenvolvimento** | Um arquivo, um framework, zero comunicação entre serviços. Qualquer pessoa do time entende o sistema inteiro em minutos. |
| **Velocidade de entrega** | O objetivo do MVP é validar a ideia rápido. Sem contratos entre serviços, filas ou service discovery, o time foca na funcionalidade. |
| **Deploy e operação triviais** | Sobe com `docker-compose up` localmente e com uma única EC2 + RDS na nuvem. Um único ponto para logs e debug. |
| **Baixo custo de infraestrutura** | Uma instância pequena atende; não há overhead de rede entre serviços nem múltiplos ambientes de execução. |
| **Debug e testes simples** | Stack trace único, transações locais no mesmo banco, sem falhas parciais distribuídas. |

### Desvantagens

| Desvantagem | Impacto |
|---|---|
| **Escalabilidade** | Para atender mais leituras de flags, replica-se também a parte de escrita/administração. Uso ineficiente de recursos. |
| **Deploy** | Qualquer mudança redeploya o sistema inteiro; o raio de explosão de um bug é a aplicação toda (ponto único de falha). |
| **Acoplamento tecnológico** | Tudo preso a Python/Flask/psycopg2; não dá para evoluir uma parte com outra tecnologia. |
| **Manutenção degrada com o tamanho** | Com mais features (segmentação de usuários, auditoria, SDKs), o `app.py` vira um "big ball of mud" e times passam a conflitar no mesmo código. |
| **Ciclo de release único** | Times diferentes não conseguem lançar de forma independente — todos dependem do mesmo pipeline e da mesma janela de deploy. |