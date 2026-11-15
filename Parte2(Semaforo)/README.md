# Parte 2 - Threads e Semaforos

Nessa parte a ideia foi mostrar uma condicao de corrida com um contador compartilhado entre varias threads e depois resolver usando um semaforo binario.

Linguagem: Python (testado no 3.10+)

## Como rodar

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

## O que o codigo faz

Tem uma variavel global `contador` e 8 threads, cada uma soma 1 nela 200.000 vezes. Entao o valor final certo seria 8 x 200.000 = 1.600.000.

- `tarefa_sem_semaforo`: le o contador, soma 1 e escreve de volta, sem proteger nada
- `tarefa_com_semaforo`: faz a mesma coisa mas entre `semaforo.acquire()` e `semaforo.release()`. O release ficou no `finally` pra garantir que sempre libera

Uma coisa que tivemos que fazer: no primeiro teste, a versao sem semaforo dava o valor certo quase sempre. Isso acontece por causa do GIL do Python, as threads terminavam tao rapido que quase nao tinha troca de thread no meio da conta. Por isso colocamos a funcao `incrementa()`, que faz um loop que nao muda o valor, so pra deixar a operacao um pouco mais demorada (o proprio enunciado fala pra fazer isso). Usamos ela nas duas versoes pra comparacao de tempo ser justa.

## Resultados

T = 8, M = 200.000, esperado = 1.600.000

| Versao | Execucao | Esperado | Obtido | Tempo |
|---|---|---|---|---|
| Sem semaforo | 1 | 1600000 | 263920 | 1.39s |
| Sem semaforo | 2 | 1600000 | 352651 | 1.08s |
| Sem semaforo | 3 | 1600000 | 347496 | 1.12s |
| Com semaforo | 1 | 1600000 | 1600000 | 3.05s |
| Com semaforo | 2 | 1600000 | 1600000 | 2.99s |
| Com semaforo | 3 | 1600000 | 1600000 | 2.62s |

Saida completa no arquivo `resultados.txt`.

Sem semaforo o valor muda toda vez e fica bem longe do esperado (perdeu mais de 1 milhao de incrementos). Com semaforo deu certo nas 3 vezes, mas ficou mais ou menos 2,5x mais lento.

## Discussao

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
