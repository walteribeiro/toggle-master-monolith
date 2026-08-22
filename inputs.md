- desafios encontrados

entender o que era os 12 fatores para aí entender se o código atual estava atendendo - foi nosso primeiro contato com o topico

export manual de credenciais (precisamos reexportar a cada novo terminal)

- decisoes
    numeros IPs (/24)
    estamos usando apenas uma subrede pública, pois sistema não é crítico, não exigindo alta disponibilidade no momento
    criamos duas subredes privadas porque era um requerimento do RDS, o qual exige redes em pelo menos duas zonas

