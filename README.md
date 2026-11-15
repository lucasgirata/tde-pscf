# TDE 2 - Programação Concorrente

### Filósofos, Semáforos e Deadlock - Performance em Sistemas Ciberfísicos

#### Equipe TDE2 14: Andrey Brawerman, João Gabriel Esperança, Lucas Girata

#### Linguagem escolhida: Python

Link do vídeo no Youtube:

## Parte 1 - Jantar dos Filosofos
Código: `Parte1/filosofos.py`.

```
cd Parte1
python filosofos.py naive
python filosofos.py correto
```

O programa roda 8 segundos e imprime no console o estado de cada um dos 5 filósofos (*pensando*, *com fome* e *comendo*). No final, mostra se houve deadlock e quantas refeições cada filósofo fez.

### Dinâmica do problema
Cinco filósofos (threads) sentam numa mesa circular; entre cada par há um garfo (um `Lock`, total de 5).
Cada um alterna pensar → ficar com fome → comer, e para comer precisa dos dois garfos adjacentes,
compartilhados com os vizinhos (exclusão mútua). O filósofo `i` usa os garfos `i` e `(i+1) % 5`.

### Por que o impasse surge (versão ingênua)
Todos pegam primeiro o garfo da esquerda e depois o da direita. Se os cinco pegam o da esquerda
"ao mesmo tempo", cada um segura um garfo e espera o do vizinho, que também está segurado: ninguém
progride. Na execução ingênua, depois de 8 segundos todos continuam "com fome" e o programa imprime
`DEADLOCK`, com 0 refeições. Para o impasse aparecer sempre, o código tem uma pausa de 0,5 s entre
pegar o primeiro e o segundo garfo (sem ela, uma thread costuma pegar os dois garfos antes das outras
acordarem e o deadlock quase não acontece). Estão presentes as 4 condições de Coffman:

1. **Exclusão mútua** – um garfo só serve a um filósofo.
2. **Manter-e-esperar** – segura o garfo esquerdo enquanto espera o direito.
3. **Não preempção** – ninguém tira o garfo de outro.
4. **Espera circular** – F0→F1→F2→F3→F4→F0.

### Solução: hierarquia de recursos
Cada garfo tem índice único (0..4); **todo filósofo pega primeiro o garfo de menor índice e depois o
de maior**. Apenas o filósofo 4 (garfos 4 e 0) inverte a ordem em relação à versão ingênua: ele pega
o garfo 0 primeiro.

**Condição de Coffman negada: espera circular.** Como todos adquirem recursos em ordem crescente,
um ciclo de espera exigiria algum filósofo esperar por um garfo de índice menor que o que já possui,
o que o protocolo proíbe; logo não há ciclo e o impasse é impossível. As outras três condições
continuam valendo (os garfos seguem exclusivos).

### Progresso e justiça (ausência de inanição)
- **Progresso:** sem deadlock, sempre existe algum filósofo que consegue os dois garfos, e ele os
  libera ao terminar de comer, permitindo que outro avance.
- **Justiça:** o tempo de comer é finito e os garfos são liberados ao fim de cada refeição; os
  `Lock`s do Python não garantem ordem FIFO, mas como as refeições são curtas e os tempos de
  pensar são aleatórios, nenhum filósofo fica bloqueado indefinidamente. Na execução, todos comeram
  várias vezes (por exemplo `[4, 7, 7, 7, 4]` em 8 s; os valores variam a cada execução). Os filósofos
  0 e 4 tendem a comer um pouco menos porque disputam o garfo 0, mas ninguém fica com zero.
  Para uma garantia formal, bastaria usar um semáforo justo ou uma fila FIFO.

### Pseudocódigo

```
Dados: N = 5; garfos 0..N-1; o filósofo i usa os garfos i e (i+1) mod N

Para cada filósofo i:
  esq = i ;  dir = (i+1) mod N
  primeiro = min(esq, dir) ;  segundo = max(esq, dir)

  Loop:
    pensar()
    estado[i] <- "com fome"
    adquirir(primeiro)      // bloqueia até o garfo estar livre
    adquirir(segundo)
    estado[i] <- "comendo"
    comer()
    liberar(segundo)
    liberar(primeiro)
    estado[i] <- "pensando"
```
Ordem de aquisição: sempre crescente; liberação: ordem inversa.

## Parte 2 - Threads e Semaforos

Nessa parte a ideia foi mostrar uma condicao de corrida com um contador compartilhado entre varias threads e depois resolver usando um semaforo binario.

Linguagem: Python (testado no 3.10+)

### Como rodar

```
cd parte2-semaforo
python3 contador.py
```

Assim ele roda as duas versoes, 3 vezes cada. Se quiser rodar so uma:

```
python3 contador.py sem
python3 contador.py com
```

Os valores de T (threads), M (incrementos) e quantas execucoes estao no comeco do arquivo, da pra mudar la.

### O que o codigo faz

Tem uma variavel global `contador` e 8 threads, cada uma soma 1 nela 200.000 vezes. Entao o valor final certo seria 8 x 200.000 = 1.600.000.

- `tarefa_sem_semaforo`: le o contador, soma 1 e escreve de volta, sem proteger nada
- `tarefa_com_semaforo`: faz a mesma coisa mas entre `semaforo.acquire()` e `semaforo.release()`. O release ficou no `finally` pra garantir que sempre libera

Uma coisa que tivemos que fazer: no primeiro teste, a versao sem semaforo dava o valor certo quase sempre. Isso acontece por causa do GIL do Python, as threads terminavam tao rapido que quase nao tinha troca de thread no meio da conta. Por isso colocamos a funcao `incrementa()`, que faz um loop que nao muda o valor, so pra deixar a operacao um pouco mais demorada (o proprio enunciado fala pra fazer isso). Usamos ela nas duas versoes pra comparacao de tempo ser justa.

### Resultados

T = 8, M = 200.000, esperado = 1.600.000

| Versao       | Execucao | Esperado | Obtido  | Tempo |
| ------------ | -------- | -------- | ------- | ----- |
| Sem semaforo | 1        | 1600000  | 263920  | 1.39s |
| Sem semaforo | 2        | 1600000  | 352651  | 1.08s |
| Sem semaforo | 3        | 1600000  | 347496  | 1.12s |
| Com semaforo | 1        | 1600000  | 1600000 | 3.05s |
| Com semaforo | 2        | 1600000  | 1600000 | 2.99s |
| Com semaforo | 3        | 1600000  | 1600000 | 2.62s |

Saida completa no arquivo `resultados.txt`.

Sem semaforo o valor muda toda vez e fica bem longe do esperado (perdeu mais de 1 milhao de incrementos). Com semaforo deu certo nas 3 vezes, mas ficou mais ou menos 2,5x mais lento.

### Discussao

**Por que perde incrementos sem sincronizacao**

O `contador = contador + 1` parece uma coisa so, mas na verdade sao 3 passos: ler, somar e escrever. Se o Python trocar de thread no meio disso da problema. Por exemplo:

1. thread 1 le contador = 100 e para antes de escrever
2. as outras threads continuam e levam o contador para 5000
3. thread 1 volta e escreve 101

Ai tudo que as outras fizeram nesse tempo se perde. Por isso o resultado muda a cada execucao. A perda foi grande porque o Python troca de thread mais ou menos a cada 5ms, entao quando uma thread "volta" com o valor velho ela apaga muitos incrementos de uma vez.

**Por que com semaforo funciona**

O semaforo foi criado com 1 permissao, entao ele funciona como um lock. Quando uma thread faz `acquire()`, as outras que tentarem tambem ficam bloqueadas ate ela fazer o `release()`. Assim so uma thread por vez faz o ler-somar-escrever, e nenhum incremento e sobrescrito. Por isso sempre da 1.600.000.

**Por que ficou mais lento**

- cada incremento agora tem um acquire e um release, sao 1.600.000 de cada
- so uma thread trabalha por vez na secao critica, as outras ficam esperando
- tem mais troca de contexto quando as threads bloqueiam e acordam

Ou seja, ganha correcao mas perde desempenho. Mesmo assim nao adianta a versao sem semaforo ser mais rapida se o resultado esta errado. Uma forma de melhorar seria cada thread somar numa variavel local e so no final atualizar o contador global com o semaforo, ai seriam so 8 acquires em vez de 1.600.000.

**Justica**

Em Java da pra criar um semaforo justo com `new Semaphore(1, true)`, que atende as threads na ordem que chegaram. O `threading.Semaphore` do Python nao garante essa ordem, a thread que acabou de liberar pode pegar de novo antes de uma que ja estava esperando. Isso deixa mais rapido mas pode fazer uma thread andar mais que outra por um tempo. No nosso caso isso nao muda o resultado, porque todas terminam os seus 200.000 incrementos no final.

**Visibilidade / ordenacao**

Em Java existe o conceito de happens-before: o que uma thread escreve antes do `release()` e garantido ser visto pela thread que fizer o `acquire()` depois. Sem isso uma thread poderia ler um valor desatualizado.

No Python, o GIL acaba funcionando como uma barreira implicita, porque ele e liberado e pego de novo em toda troca de thread, entao as threads sempre veem o valor mais recente na memoria. O problema no Python entao nao e visibilidade e sim atomicidade (a sequencia ler-somar-escrever ser interrompida no meio). O acquire/release do semaforo tambem servem como ponto de sincronizacao. Mas o GIL sozinho nao resolve a corrida, ele so garante que um bytecode roda por vez, e o `contador = contador + 1` tem varios bytecodes.

## Parte 3 - Deadlock

### Logs do código com travamento

```
Thread 1 pegou A
Thread 2 pegou B
Thread 1 tenta B
Thread 2 tenta A
Deadlock: Threads nao finalizaram
[<_MainThread(MainThread, started 18236)>, <Thread(Thread-1 (thread1), started daemon 17568)>, <Thread(Thread-2 (thread2), started daemon 19572)>]

[Done] exited with code=0 in 4.341 seconds
```

### Logs do código corrigido

```
Thread 1 obteve A
Thread 1 obteve B
Thread 1 concluiu
Thread 2 obteve A
Thread 2 obteve B
Thread 2 concluiu
Programa finalizado

[Done] exited with code=0 in 0.42 seconds
```

### Explicação das condições de Coffman

Para que o deadlock aconteça, quatro das condições de Coffman foram manifestadas, sendo elas:

1. **Exclusão Mútua**: Uma thread por vez segura threading.Lock(). Com a thread 1 segurando A, a thread 2 não consegue entrar na seção crítica e vice-versa com B.
2. **Manter-e-esperar**: A thread 1 segura A e pede B simultaneamente. A thread 2 faz o inverso (Segura B e solicita A).
3. **Não preempção**: As threads não tomam um lock da outra. Ele só é liberado quando sai do bloco de código do with, ou seja, nunca acontecendo, já que o dono se bloqueia esperando o outro lock.
4. **Espera circular**: A thread 1 aguarda o recurso da thread 2 e vice-versa, formando o ciclo: Thread 1 -> Lock B -> Thread 2 -> Lock A -> Thread 1

Para a correção do código, se altera a execução das duas threads, com ambas executando "tarefa". Nessa execução, sempre se adquire o Lock A antes do Lock B. Se aplica a hierarquia de recursos, onde A tem prioridade sobre B em ambas as threads.

### Condição de Coffman quebrada

Com a ordem aplicada no código, se quebra a condição **espera circular** de Coffman, já que a Thread 2 tenta obter o Lock A antes de qualquer outro. Caso a Thread 1 já esteja com A, a Thread 2 aguarda sem segurar nenhum dos dois locks, sem existir dependências e ciclos. Ou seja, nunca existe uma thread que segura B enquanto espera A ser liberado. 

Porém as condições restantes ainda são válidas, já que os locks ainda continuam exclusivos, as threads seguram um lock e pedem outro simultaneamente e não existe a preempção. Porém, o deadlock não é possível sem a espera circular. 
