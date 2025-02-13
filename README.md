# Sync Motion

Este é um projeto de sincronização de tarefas entre o Todoist e o Usemotion, que automaticamente transfere tarefas do Todoist para o Usemotion utilizando IA para melhor organização.

## Funcionalidades

- Busca tarefas do Todoist automaticamente
- Cria tarefas no Usemotion usando IA para processamento e organização
- Marca tarefas como concluídas no Todoist após a sincronização
- Executa a sincronização a cada 1 minuto
- Servidor Express básico para monitoramento

## Configuração

1. Clone o repositório
2. Instale as dependências:
```bash
npm install
```

3. Configure as variáveis de API no arquivo `main.js`:
- TODOIST_API_KEY: Seu token de API do Todoist
- USEMOTION_API_KEY: Seu token de API do Usemotion
- Ajuste o workspaceId do Usemotion conforme necessário

### Como encontrar o Workspace ID no Usemotion:

1. Faça login no Usemotion
2. Use a API do Usemotion para listar seus workspaces com o seguinte comando curl (substitua YOUR_API_KEY pelo seu token):
```bash
curl -X GET "https://api.usemotion.com/v1/workspaces" \
-H "X-API-Key: YOUR_API_KEY" \
-H "Accept: application/json"
```
3. Na resposta, procure pelo workspace chamado "Inbox" e copie o valor do campo "id"
4. Cole este ID no arquivo main.js no campo workspaceId

## Como Usar

Execute o projeto com:
```bash
node main.js
```

O servidor irá:
- Iniciar na porta 3000
- Realizar uma sincronização inicial
- Continuar sincronizando a cada 60 segundos
- Acessar http://localhost:3000 para verificar se está em execução

## Tecnologias Utilizadas

- Node.js
- Express
- Axios
- API Todoist
- API Usemotion

## Dependências

- axios: ^1.7.9
- express: ^4.21.2
