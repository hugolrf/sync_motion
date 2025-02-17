const axios = require("axios");
const express = require('express');
const app = express();

// Configuração dos tokens de API
const TODOIST_API_KEY = "e68bc41b21ea7a28b41f59b1cf7692fca2820e10"; // Substitua pelo seu token do Todoist
const USEMOTION_API_KEY = "4hmJXuchtC1MhlJ6rNkY+TqD085sCt84iRefG0kaqs8="; // Substitua pelo seu token do Usemotion
const WORKSPACE_ID = "zbBICisk6HNg4EdnysTNg";

// Função para buscar tarefas do Todoist
const fetchTodoistTasks = async () => {
  const url = "https://api.todoist.com/rest/v2/tasks";
  const headers = {
    Authorization: `Bearer ${TODOIST_API_KEY}`,
  };

  try {
    const response = await axios.get(url, { headers });
    return response.data; // Retorna uma lista de tarefas
  } catch (err) {
    console.error(`Erro ao buscar tarefas do Todoist: ${err.response.statusText}`);
    return [];
  }
};

const createTaskWithAIInUsemotion = async (task) => {
  const url = "https://api.usemotion.com/v1/tasks/ai";
  const headers = {
    "X-API-Key": USEMOTION_API_KEY,
    Accept: "application/json",
    "Content-Type": "application/json",
  };

  // Combinamos título e descrição em um único texto para a IA processar
  const taskText = `
    Título: ${task.content}
    Descrição: ${task.description || ""}
  `;

  const payload = {
    text: taskText,
    workspaceId: WORKSPACE_ID,
  };

  try {
    const response = await axios.post(url, payload, { headers });
    console.log("Tarefa criada pela IA do Usemotion:", response.data);
    return response.data;
  } catch (err) {
    console.error(`Erro ao criar tarefa com IA no Usemotion: ${err.response?.data || err.message}`);
    return null;
  }
};

// Função para criar uma nova tarefa no Usemotion
const createTaskInUsemotion = async (task) => {
  const url = "https://api.usemotion.com/v1/tasks";
  const headers = {
    "X-API-Key": USEMOTION_API_KEY,
    Accept: "application/json",
    "Content-Type": "application/json",
  };

  const payload = {
    name: task.content, // O nome da tarefa do Todoist
    description: task.description || "",
    workspaceId: WORKSPACE_ID, // Substitua pelo ID válido do workspace
  };

  try {
    const response = await axios.post(url, payload, { headers });
    return response.data; // Retorna os dados da tarefa criada no Usemotion
  } catch (err) {
    console.error(`Erro ao criar tarefa no Usemotion: ${err.response.statusText}`);
    return null;
  }
};

// Função para marcar uma tarefa como concluída no Todoist
const markTaskAsDoneInTodoist = async (taskId) => {
  const url = `https://api.todoist.com/rest/v2/tasks/${taskId}/close`;
  const headers = {
    Authorization: `Bearer ${TODOIST_API_KEY}`,
  };

  try {
    await axios.post(url, {}, { headers });
    console.log(`Tarefa ${taskId} marcada como concluída no Todoist.`);
  } catch (err) {
    console.error(`Erro ao concluir a tarefa no Todoist: ${err.response.statusText}`);
  }
};

// Função principal para sincronizar tarefas
const syncTasks = async () => {
  console.log("Iniciando sincronização de tarefas...");
  const tasks = await fetchTodoistTasks();

  for (const task of tasks) {
    console.log(`
    Processando tarefa:
    - Título: ${task.content}
    - ID: ${task.id}
    - Descrição: ${task.description || "Sem descrição"}
    `);

    const usemotionTask = await createTaskInUsemotion(task);

    if (usemotionTask) {
      await markTaskAsDoneInTodoist(task.id);
    } else {
      console.error(`Falha ao processar a tarefa ${task.id}. Verifique os detalhes.`);
    }
  }

  console.log("Sincronização concluída!");
};

// Agendador para rodar as tarefas periodicamente
const startTaskScheduler = (intervalInSeconds, taskFunction) => {
  const interval = intervalInSeconds * 1000; // Converte segundos para milissegundos

  // Intervalo contínuo para executar a função
  const scheduler = setInterval(async () => {
    await taskFunction();
  }, interval);

  // Trata encerramento do processo para limpar o agendamento
  process.on("SIGINT", () => {
    console.log("Encerrando programa...");
    clearInterval(scheduler);
    process.exit();
  });

  return scheduler;
};

// Iniciar o programa
(async () => {
  console.log("Iniciando o sincronizador de tarefas...");
  await syncTasks(); // Executa imediatamente antes do agendamento
  startTaskScheduler(60, syncTasks); // Agenda a cada 60 segundos (1 minuto)
})();

const PORT = 3000; // ou process.env.PORT, se configurado pelo ambiente

app.get('/', (req, res) => {
  res.status(200).send('Aplicação está rodando!');
});

app.listen(PORT, () => {
  console.log(`Servidor rodando na porta ${PORT}`);
})
