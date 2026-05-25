# Bank Challenge AI

API RESTful de uma carteira bancaria inspirada no desafio de um banco famoso que não quer ser identificado. O projeto implementa cadastro de usuarios comuns e lojistas, abertura de conta, autenticacao por sessao e fluxo de transferencia com validacoes de regra de negocio, autorizador externo e tentativa de notificacao ao recebedor.

Esta implementacao nao replica o contrato original de forma literal em todos os pontos, porque o projeto foi pensado para evoluir alem do desafio. Ainda assim, as regras centrais do desafio foram consideradas e estao refletidas no dominio atual.

## Stack

- Python 3.13
- Django 6
- Django REST Framework
- SQLite em ambiente local
- Autenticacao por sessao do Django

## Regras de negocio atendidas

- Usuarios comuns e lojistas possuem credenciais de acesso por e-mail e senha.
- E-mails sao unicos no sistema por meio do modelo `ClientModel`.
- CPF de usuario comum e unico no sistema.
- CNPJ e razao social de lojista sao unicos no sistema.
- O tipo do cliente e separado entre `user` e `store`.
- Usuarios comuns podem enviar dinheiro para outros usuarios ou lojistas.
- Lojistas nao podem enviar transferencias.
- A transferencia valida saldo suficiente antes de movimentar dinheiro.
- A transferencia nao permite que uma conta envie dinheiro para ela mesma.
- O recebedor precisa ser uma conta valida.
- Antes de concluir a transferencia, a API consulta o autorizador externo:
  `GET https://util.devi.tools/api/v2/authorize`
- Apos a transferencia, a API tenta enviar notificacao pelo mock externo:
  `POST https://util.devi.tools/api/v1/notify`
- Falha no envio de notificacao e registrada em log e nao desfaz a transferencia ja autorizada.
- A tratativa de reversão e feita por servico que mantem o registro da transferencia recusada e cria um novo registro de estorno com uma flag true.

## Modelo de dominio

### Client

Representa a identidade autenticavel do sistema.

Campos principais:

- `email`: unico.
- `password`: armazenado com hash pelo Django.
- `client_type`: `user` ou `store`.

### User

Representa uma pessoa fisica.

Campos:

- `name`
- `cpf`: unico.
- `client`: relacionamento 1:1 com `ClientModel`.

### Store

Representa um lojista.

Campos:

- `cnpj`: unico.
- `razao_social`: unica.
- `nome_fantasia`
- `client`: relacionamento 1:1 com `ClientModel`.

### Account

Representa a carteira/conta usada nas transferencias.

Campos:

- `uuid`: identificador único da conta.
- `client`: relacionamento 1:1 com `ClientModel`.
- `agency`: agencia da conta.
- `number`: numero da conta usado como identificador de destino nas transferencias.
- `account_type`: conta corrente ou poupanca.
- `balance`: saldo da conta.
- `created_at`: data de criação da conta

### Transaction

Representa uma transferencia entre duas contas.

Campos:

- `payer`: conta pagadora.
- `payee`: conta recebedora.
- `transaction_type`: tipo de transação, atualmente suporte apenas à transferências.
- `value`: valor transferido.
- `refund`: default False, True caso seja uma operação de estorno.
- `operation_date`: data da operacao.

## Base URL

Em desenvolvimento local:

```http
http://127.0.0.1:8000/bank/
```

## Autenticacao

A API usa autenticacao por sessao. Para endpoints protegidos, primeiro faca login e envie o cookie de sessao nas requisicoes seguintes. Em clientes HTTP que respeitam CSRF do Django, envie tambem o token CSRF quando necessario.

### Login

```http
POST /bank/auth/login/
Content-Type: application/json

{
  "email": "cliente@email.com",
  "password": "senha-segura"
}
```

Resposta:

```json
{
  "login": "cliente@email.com"
}
```

### Logout

Endpoint protegido.

```http
POST /bank/auth/logout/
Content-Type: application/json
```

Resposta:

```json
{
  "logout": "cliente@email.com"
}
```

## Endpoints

### Health check

```http
GET /bank/
```

Resposta:

```json
{
  "handshake": "Hello, from my bank_challenge app!"
}
```

### Criar usuario comum

```http
POST /bank/user/
Content-Type: application/json

{
  "email": "maria@email.com",
  "password": "senha-segura",
  "cpf": "12345678901",
  "name": "Maria Silva"
}
```

Resposta:

```json
{
  "user": "maria@email.com"
}
```

Validacoes importantes:

- `email` deve ser unico.
- `cpf` deve ser unico.
- O cliente criado recebe `client_type = "user"`.

### Criar lojista

```http
POST /bank/store/
Content-Type: application/json

{
  "email": "loja@email.com",
  "password": "senha-segura",
  "cnpj": "12345678000199",
  "razao_social": "Loja Exemplo LTDA",
  "nome_fantasia": "Loja Exemplo"
}
```

Resposta:

```json
{
  "store": "loja@email.com"
}
```

Validacoes importantes:

- `email` deve ser unico.
- `cnpj` deve ser unico.
- `razao_social` deve ser unica.
- O cliente criado recebe `client_type = "store"`.

### Criar conta

Endpoint protegido. Cria uma conta para o cliente autenticado.

```http
POST /bank/account/
Content-Type: application/json
```

Resposta:

```json
{
  "account": "client: Maria Silva, ag: 1002 cc: 2134848"
}
```

Observacoes:

- A conta e vinculada ao usuario autenticado.
- O numero da conta possui 7 dígitos e e gerado automaticamente.
- O saldo inicial tambem e gerado automaticamente no ambiente atual, valor entre 2000 e 10000.
- O modelo impede saldo negativo.

### Transferir dinheiro

Endpoint protegido.

No desafio original, o contrato sugerido era:

```http
POST /transfer
Content-Type: application/json

{
  "value": 100.0,
  "payer": 4,
  "payee": 15
}
```

Neste projeto, a proposta implementada e mais alinhada com uma sessao autenticada: o `payer` e inferido a partir do usuario logado, e o `payee` e informado pelo numero da conta de destino.

```http
POST /bank/transaction/transfer/
Content-Type: application/json

{
  "value": "100.00",
  "payee": "2134848"
}
```

Resposta:

```json
{
  "transfer": {
    "value": "100.00",
    "payer": "Maria Silva",
    "payee": "Loja Exemplo LTDA"
  }
}
```

Fluxo executado:

1. A API recebe a requisição do usuário.
2. O payload da requisicao e validado.
3. A conta pagadora e obtida a partir do usuario autenticado.
4. A conta recebedora e buscada pelo numero informado em `payee`.
5. A transacao é validada no servico de transferencias pelo metodo allowed_transfer:
   - loja não pode realizar transações;
   - transferências não podem ser concluídas se o valor transferido for maior que o saldo;
   - transferências precisam de um beneficiário;
   - nao e possivel transferencia para a mesma conta;
   - a transferencia precisa ser para uma conta registrada no app;
   - modelo de usuarios garante que uma conta user so pode ser criada se o client for do tipo 'user' e store apenas para client tipo 'store';
6. O saldo e debitado do pagador.
7. O saldo e creditado no recebedor.
8. A transacao e registrada.
9. Se a transacao for cancelada ou recusada pelo servico validador é registrada uma nova transacao com uma operacao inversa para reembolso dos valores.
10. A API tenta notificar o recebedor via servico externo.

Possiveis erros de negocio:

- Lojista tentando enviar dinheiro.
- Saldo insuficiente.
- Transferencia para a propria conta.
- Conta de destino inexistente ou invalida.
- Transferencia sem conta de destino.
- Autorizador externo recusando ou indisponivel.

## Observacoes tecnicas

- O projeto usa `ViewSet` e actions do Django REST Framework.
- A transferencia e feita pelo servico `TransferService` desacoplado do modelo `TransactionModel`, que executa as validacoes e a movimentacao de saldo.
- O autorizador externo e chamado apos a criacao da transacao.
- Se a transacao nao for autorizada o reembolso e feito pelo servico `RollbackService` que faz uma operacao inversa, estornando ao pagador e debitando do beneficiario.
- A notificacao externa e chamada depois da transferencia; falhas sao registradas, mas nao impedem a resposta de sucesso.
- As operacoes de transferencia e rollback sao atomicas, com protecao contra concorrencia, garantindo que as transacoes sejam feitas no banco de forma segura.

## Como executar localmente

Ative o ambiente virtual e defina a chave de desenvolvimento:

```bash
source .venv/bin/activate
export DEV_PROJECT_KEY="dev-secret"
python manage.py migrate
python manage.py runserver
```

Depois acesse:

```http
http://127.0.0.1:8000/bank/
```

## User roadmap

### Jornada atual

- Criar cadastro como usuario comum ou lojista.
- Fazer login.
- Criar uma conta vinculada ao cliente autenticado.
- Consultar o numero da conta retornado na criacao.
- Realizar transferencia autenticada informando valor e conta recebedora.
- Recebedor e notificado por servico externo quando o mock estiver disponivel.

### Proximas melhorias de produto

- Consulta de saldo da propria conta.
- Extrato de transacoes enviadas e recebidas.
- Listagem de contas e detalhes da conta autenticada.
- Status detalhado de transferencia: autorizada, recusada, notificada, notificacao pendente.
- Cadastro com validacao mais forte de CPF/CNPJ.
- Politicas de limite por transacao, por dia e por tipo de cliente.
- Endpoint administrativo para auditoria de transacoes.
- Reprocessamento de notificacoes que falharam.
- Melhor padronizacao de respostas de erro.

### Upgrades tecnicos planejados

- ~~Criar uma service layer para centralizar o caso de uso de transferencia, autorizacao, notificacao e rollback.~~
- ~~Usar `transaction.atomic()` e bloqueio de linhas quando houver banco relacional adequado para concorrencia.~~
- Conteinerizar a aplicacao com Docker e Docker Compose.
- Separar configuracoes por ambiente: desenvolvimento, teste e producao.
- Adicionar testes automatizados de unidade e integracao para as regras de negocio.
- Criar documentacao OpenAPI/Swagger.
- Adicionar CI para lint, testes e migracoes.
- Evoluir notificacoes para processamento assicrono.
- Definir funcionalidades alimentadas por IA, como analise de risco de transacoes, categorizacao inteligente de movimentacoes, assistente de suporte e sugestoes de limite com base em comportamento.

## Status

O projeto atende ao fluxo principal do desafio: cadastro de tipos de cliente, unicidade de identificadores, restricao de lojista, validacao de saldo, autorizador externo, transferencia entre contas e tentativa de notificacao. As proximas evolucoes devem priorizar separacao de responsabilidades, transacoes atomicas no banco, testes automatizados e documentacao interativa.
