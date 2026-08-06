## Relatório

### Análise inicial do 12-factor-app

1. Base de código - usamos Git
2. Dependências - versão do python definida na docker image
3. Configurações - precisamos separar as variáveis (eg.: DB_HOST; POSTGRES_USER)
4. Serviços de apoio - a verificar no futuro; algo para logs
5. Build, Release, Run - a criar: pipeline
6. Processos - já separados entre banco e aplicação (docker-compose declara app e db)
7. Port Binding - usando porta "5000:5000"
8. Concorrência - sem definições para escalar, necessário criar
9. Descartabilidade - possível iniciar e parar sem problemas; enquanto volume for mantido, dados são mantidos
10. Paridade entre desenvolvimento e produção - ainda não há separação de ambientes
11. Logs - não atende ainda, precisamos armazenar os logs usando alguma ferramenta
12. Processos Administrativos - parcialmente coberto; não há rollback definido
