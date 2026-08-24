# Roteiro de Gravação do Vídeo — Tech Challenge Fase 1 (ToggleMaster)

**Duração Estimada**: 10 a 12 minutos (Máximo permitido: 15 min)  
**Apresentadores**: Mayara Finatto e Walter Ribeiro  
**Ferramentas Sugeridas**: OBS Studio, Loom, Zoom ou Teams (com compartilhamento de tela)

---

## ⏱️ Cronograma do Vídeo (Visão Geral)

| Bloco | Tempo | Tema | Responsável | O que mostrar na tela |
|---|---|---|---|---|
| **1** | 00:00 - 01:30 | Introdução e Visão Geral do Projeto | Mayara | Diapositivo inicial / Câmeras ou tela inicial do GitHub |
| **2** | 01:30 - 03:30 | Aplicação Monolítica & Execução Local (Docker) | Walter | Terminal / VS Code rodando `docker compose up` e `curl` |
| **3** | 03:30 - 06:00 | Arquitetura na Nuvem (AWS) & Diagrama | Mayara | Diagrama da Arquitetura (`aws-architecture-diagram.drawio`) |
| **4** | 06:00 - 09:30 | Demonstração Prática na AWS (EC2 + RDS + Security Groups) | Walter | Console da AWS + Terminal SSH na EC2 + Postman/curl |
| **5** | 09:30 - 11:30 | Análise dos 12 Fatores & Aprendizados | Mayara e Walter | Documento do Relatório (`ENTREGA.md`) |
| **6** | 11:30 - 12:00 | Encerramento | Ambos | Câmeras |

---

## 🎬 Roteiro Detalhado Passo a Passo

### 📍 BLOCO 1: Introdução e Objetivo do Projeto (00:00 - 01:30)
**Tela**: Apresentação inicial / Câmeras dos participantes.

- **[Mayara]**: *"Olá! Sejam bem-vindos à apresentação do nosso Tech Challenge da Fase 1 do curso de DevOps e Arquitetura Cloud da Postech FIAP. Eu sou a Mayara Finatto (RM375879) e comigo está o Walter Ribeiro (RM375778)."*
- **[Walter]**: *"Nesta primeira fase, o desafio proposto pela DevOps Solutions Inc. foi implantar o MVP da plataforma ToggleMaster — um serviço interno de Feature Flag as a Service que permite ativar ou desativar funcionalidades em produção sem a necessidade de um novo deploy."*
- **[Mayara]**: *"Hoje vamos demonstrar a aplicação monolítica rodando em ambiente local com Docker, explicar a arquitetura desenhada na AWS com EC2 e RDS, validar as configurações de segurança dos Security Groups e demonstrar o sistema rodando na nuvem em tempo real."*

---

### 📍 BLOCO 2: Execução Local com Docker Compose (01:30 - 03:30)
**Tela**: VS Code e Terminal local.

- **[Walter]**: *"Para iniciar, vou mostrar a aplicação rodando no ambiente de desenvolvimento local usando Docker Compose."*
  - *(Mostrar o terminal executando: `docker compose up -d`)*
- **[Walter]**: *"Reparem que o Docker Compose sobe dois contêineres: a nossa aplicação Flask com Gunicorn na porta 5000 e a base de dados PostgreSQL. O script `entrypoint.sh` aguarda a prontidão do banco com `pg_isready` e executa a inicialização do schema antes de subir a API."*
- **[Walter]**: *"Vamos testar a API localmente:"*
  - *(Executar no terminal ou Postman: `curl http://localhost:5000/health`)* ➔ Recebendo `status: ok`.
  - *(Executar a criação de uma flag: `curl -X POST -H "Content-Type: application/json" -d '{"name": "new-ui", "is_enabled": true}' http://localhost:5000/flags`)*
  - *(Listar as flags: `curl http://localhost:5000/flags`)*

---

### 📍 BLOCO 3: Arquitetura na AWS e Decisões de Rede (03:30 - 06:00)
**Tela**: Diagrama de Arquitetura (`aws-architecture-diagram.drawio` / Miro).

- **[Mayara]**: *"Agora vamos apresentar a arquitetura que desenhamos para a implantação na AWS."*
  - *(Apontar para os componentes do diagrama)*
- **[Mayara]**: *"Nossa arquitetura conta com os seguintes componentes principais:"*
  1. *"**VPC com CIDR /24**: Definimos o bloco de endereçamento `/24` para a nossa rede virtual."*
  2. *"**Subrede Pública**: Onde fica a nossa instância EC2 (`t2.micro`) rodando Ubuntu Server. Ela possui um IP Público para receber requisições HTTP na porta 5000 e permitir acesso SSH na porta 22 para administração."*
  3. *"**Duas Subredes Privadas (Multi-AZ)**: Criadas em zonas de disponibilidade diferentes para atender aos requisitos do Amazon RDS, garantindo que a base de dados relacional PostgreSQL não fique exposta diretamente à internet."*
  4. *"**Security Groups**: Criamos regras estritas de firewall. O grupo do RDS permite tráfego na porta 5432 **exclusivamente vindo do Security Group da EC2**."*

---

### 📍 BLOCO 4: Demonstração na AWS e Validação de Segurança (06:00 - 09:30)
**Tela**: Console da AWS (EC2, RDS, Security Groups) + Terminal SSH + Postman.

- **[Walter]**: *"Vou mostrar agora a infraestrutura rodando no Console da AWS."*
  - *(Mostrar a tela de instâncias da EC2 no console AWS e destacar o IP Público)*
  - *(Mostrar a tela do Amazon RDS e indicar o status Available e o endpoint de conexão)*
- **[Walter]**: *"Um ponto fundamental exigido no projeto é a **segurança por Security Groups**."*
  - *(Abrir a aba de Inbound Rules do Security Group do RDS)*
  - *"Vejam que a porta 5432 do PostgreSQL aceita conexões unicamente da origem `sg-togglemaster-ec2`. Nenhuma máquina da internet consegue conectar diretamente no banco."*
- **[Walter]**: *"Agora vamos ver a aplicação em execução na EC2:"*
  - *(Mostrar o terminal SSH conectado na EC2 com o Gunicorn rodando)*
  - *(No Postman ou terminal local, fazer as requisições para o IP Público da EC2)*:
    1. `GET http://<IP-PUBLICO-EC2>:5000/health` ➔ `{"status": "ok"}`
    2. `POST http://<IP-PUBLICO-EC2>:5000/flags` ➔ Criar flag `feature-checkout-v2`
    3. `GET http://<IP-PUBLICO-EC2>:5000/flags` ➔ Confirmar que a flag foi gravada na tabela do RDS.

---

### 📍 BLOCO 5: Análise dos 12 Fatores e Aprendizados (09:30 - 11:30)
**Tela**: Documento do Relatório ([`ENTREGA.md`](./ENTREGA.md)).

- **[Mayara]**: *"Sobre a análise dos 12 Fatores (12-Factor App), nossa aplicação atende plenamente aos principais requisitos de um sistema moderno na nuvem:"*
  - *"**Base de Código Única (Factor I)** e **Processos Stateless (Factor VI)**, onde todo o estado reside no banco RDS."*
  - *"**Configurações via Variáveis de Ambiente (Factor III)**, lidas com `os.getenv()`, garantindo que nenhuma credencial fique gravada no código-fonte."*
  - *"**Serviços de Apoio (Factor IV)**, onde o PostgreSQL é tratado como recurso de rede anexado, permitindo trocar o banco local pelo Amazon RDS sem alterar uma linha de código."*
- **[Walter]**: *"Como desafios encontrados, destacamos o primeiro contato da equipe com a metodologia dos 12 Fatores e a necessidade de exportar manualmente as variáveis de ambiente na EC2 via SSH, algo que em produção será automatizado com arquivos de serviço `systemd` ou contêineres Docker."*

---

### 📍 BLOCO 6: Encerramento (11:30 - 12:00)
**Tela**: Câmeras dos participantes.

- **[Mayara]**: *"Demonstramos com sucesso o MVP do ToggleMaster rodando tanto localmente quanto na nuvem da AWS com isolamento e segurança."*
- **[Walter]**: *"Todos os arquivos de código, relatório de entrega e diagrama de arquitetura estão disponíveis no nosso repositório Git."*
- **[Ambos]**: *"Muito obrigado a todos e até a próxima fase!"*

---

## 🛠️ Checklist Pré-Gravação

- [ ] Instância EC2 iniciada com IP público ativo.
- [ ] Banco RDS em status *Available*.
- [ ] Terminal local pronto com o Docker Compose testado (`docker compose up`).
- [ ] Terminal SSH na EC2 aberto e testado.
- [ ] Postman/Insomnia pré-configurado com as requisições (`localhost:5000` e `<IP-EC2>:5000`).
- [ ] Abas do navegador abertas no Console AWS (EC2, RDS, Security Groups).
