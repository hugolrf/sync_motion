import requests
import time
import schedule  # Biblioteca para agendamento de tarefas periódicas
from datetime import datetime

# Configuração dos tokens de API
TODOIST_API_KEY = "e68bc41b21ea7a28b41f59b1cf7692fca2820e10"  # Substitua pelo seu token do Todoist
USEMOTION_API_KEY = "4hmJXuchtC1MhlJ6rNkY+TqD085sCt84iRefG0kaqs8="  # Substitua pelo seu token do Usemotion


# Função para buscar tarefas do Todoist
def fetch_todoist_tasks():
    """
    Busca todas as tarefas ativas no Todoist.
    """
    url = "https://api.todoist.com/rest/v2/tasks"
    headers = {
        "Authorization": f"Bearer {TODOIST_API_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tasks = response.json()  # Retorna uma lista de tarefas
        return tasks
    except requests.exceptions.HTTPError as err:
        print(f"Erro ao buscar tarefas do Todoist: {err}, Detalhes: {response.text}")
        return []


# Função para criar uma nova tarefa no Usemotion
def create_task_in_usemotion(task):
    """
    Cria uma nova tarefa no Usemotion com base nos dados do Todoist.
    """
    url = "https://api.usemotion.com/v1/tasks"
    headers = {
        "X-API-Key": USEMOTION_API_KEY,  # Chave exigida pela API
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Verifica se 'due' e 'date' estão presentes na tarefa
    due_date = None
    if task.get("due") and task["due"].get("date"):
        due_date = validate_and_format_due_date(task["due"]["date"])

    # Define o payload conforme especificações da API do Usemotion
    # payload = {
    #     "dueDate": due_date,  # Data de vencimento, se disponível
    #     "duration": "NONE",  # Duração - campo fixo para este exemplo
    #     "status": "ACTIVE",  # Status - ajuste "ACTIVE" como padrão
    #     "autoScheduled": {
    #         "startDate": validate_and_format_start_date(due_date),  # Data de início
    #         "deadlineType": "SOFT",  # Tipo de deadline "SOFT"
    #         "schedule": "Work Hours"  # Horas de trabalho
    #     },
    #     "name": task["content"],  # Nome/título da tarefa
    #     "projectId": "default-project-id",  # Substitua pelo ID válido do projeto
    #     "workspaceId": "rOU1dgxfycJMM5VciMsSk",  # Substitua pelo ID válido do workspace
    #     "description": task.get("description", "Tarefa sincronizada do Todoist."),  # Descrição da tarefa
    #     "priority": "MEDIUM",  # Prioridade padrão
    #     "labels": ["sincronizada"],  # Etiqueta de identificação
    #     "assigneeId": "default-assignee-id"  # Substitua pelo ID do responsável, se disponível
    # }
    payload = {
        "name": task["content"],  # Nome/título da tarefa
        "workspaceId": "rOU1dgxfycJMM5VciMsSk",  # Substitua pelo ID válido do workspace
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"Erro ao criar tarefa no Usemotion: {err}, Detalhes: {response.text}")
        return None



# Função para validar e formatar a data no formato ISO 8601
def validate_and_format_due_date(due_date):
    """
    Valida e formata a data no formato ISO 8601.
    :param due_date: String com a data fornecida pela API Todoist.
    :return: Data formatada em ISO 8601, ou None caso a data seja inválida.
    """
    if not due_date:
        return None
    try:
        # Adiciona horário 00:00 caso nenhum horário seja fornecido
        return datetime.fromisoformat(due_date).isoformat() + "Z"
    except ValueError:
        print(f"Erro ao validar e formatar a data: {due_date}")
        return None


# Valida o início da data para evitar falhas
def validate_and_format_start_date(due_date):
    """
    Gera a data de início para o autoScheduler com base na dueDate.
    :param due_date: Data de vencimento da tarefa no Todoist.
    :return: Data formatada, ou None caso seja inválida.
    """
    if not due_date:
        return None
    try:
        return datetime.fromisoformat(due_date).date().isoformat()  # Apenas a data sem horário
    except ValueError:
        print(f"Erro ao validar a data de início: {due_date}")
        return None


# Função para marcar uma tarefa como concluída no Todoist
def mark_task_as_done_in_todoist(task_id):
    """
    Marca uma tarefa como concluída no Todoist.
    """
    url = f"https://api.todoist.com/rest/v2/tasks/{task_id}/close"
    headers = {
        "Authorization": f"Bearer {TODOIST_API_KEY}"
    }

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        print(f"Tarefa {task_id} marcada como concluída no Todoist.")
    except requests.exceptions.HTTPError as err:
        print(f"Erro ao concluir a tarefa no Todoist: {err}, Detalhes: {response.text}")


# Função principal para sincronizar tarefas
def sync_tasks():
    """
    Busca todas as tarefas no Todoist, cria no Usemotion e marca como concluídas.
    """
    print("Iniciando sincronização de tarefas...")

    # Buscar todas as tarefas do Todoist
    tasks = fetch_todoist_tasks()

    # Processar cada tarefa encontrada
    for task in tasks:
        print(f"Processando tarefa: {task['content']} [ID: {task['id']}]")

        # Criar a tarefa no Usemotion
        usemotion_task = create_task_in_usemotion(task)

        if usemotion_task:
            # Se a tarefa foi criada no Usemotion, marcamos como concluída no Todoist
            mark_task_as_done_in_todoist(task["id"])
        else:
            print(f"Falha ao processar a tarefa {task['id']}. Verifique os detalhes.")

    print("Sincronização concluída!")


# Agendamento para rodar a cada 5 minutos (ajuste conforme necessário)
if __name__ == "__main__":
    print("Iniciando o sincronizador de tarefas...")
    sync_tasks()  # Executa imediatamente antes de iniciar o agendamento
    schedule.every(1).minutes.do(sync_tasks)
    while True:
        schedule.run_pending()  # Verifica tarefas agendadas
        time.sleep(1)  # Impede loop infinito sem pausas
