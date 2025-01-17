import requests
import time
from datetime import datetime
from threading import Thread, Event

# Configuração dos tokens de API
TODOIST_API_KEY = "e68bc41b21ea7a28b41f59b1cf7692fca2820e10"  # Substitua pelo seu token do Todoist
USEMOTION_API_KEY = "4hmJXuchtC1MhlJ6rNkY+TqD085sCt84iRefG0kaqs8="  # Substitua pelo seu token do Usemotion


# Função para buscar tarefas do Todoist
def fetch_todoist_tasks():
    url = "https://api.todoist.com/rest/v2/tasks"
    headers = {"Authorization": f"Bearer {TODOIST_API_KEY}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()  # Retorna uma lista de tarefas
    except requests.exceptions.HTTPError as err:
        print(f"Erro ao buscar tarefas do Todoist: {err}, Detalhes: {response.text}")
        return []


# Função para criar uma nova tarefa no Usemotion
def create_task_in_usemotion(task):
    url = "https://api.usemotion.com/v1/tasks"
    headers = {
        "X-API-Key": USEMOTION_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "name": task["content"],
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
    if not due_date:
        return None
    try:
        return datetime.fromisoformat(due_date).isoformat() + "Z"
    except ValueError:
        print(f"Erro ao validar e formatar a data: {due_date}")
        return None


# Função para marcar uma tarefa como concluída no Todoist
def mark_task_as_done_in_todoist(task_id):
    url = f"https://api.todoist.com/rest/v2/tasks/{task_id}/close"
    headers = {"Authorization": f"Bearer {TODOIST_API_KEY}"}
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        print(f"Tarefa {task_id} marcada como concluída no Todoist.")
    except requests.exceptions.HTTPError as err:
        print(f"Erro ao concluir a tarefa no Todoist: {err}, Detalhes: {response.text}")


# Função principal para sincronizar tarefas
def sync_tasks():
    print("Iniciando sincronização de tarefas...")
    tasks = fetch_todoist_tasks()
    for task in tasks:
        print(f"Processando tarefa: {task['content']} [ID: {task['id']}]")
        usemotion_task = create_task_in_usemotion(task)
        if usemotion_task:
            mark_task_as_done_in_todoist(task["id"])
        else:
            print(f"Falha ao processar a tarefa {task['id']}. Verifique os detalhes.")
    print("Sincronização concluída!")


# Classe para rodar tarefas agendadas usando threading
class TaskScheduler(Thread):
    def __init__(self, interval, function, *args, **kwargs):
        super().__init__()
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.stop_event = Event()

    def run(self):
        while not self.stop_event.is_set():
            self.function(*self.args, **self.kwargs)  # Executa a tarefa
            time.sleep(self.interval)  # Aguarda o intervalo especificado

    def stop(self):
        self.stop_event.set()


# Configuração do agendamento
if __name__ == "__main__":
    print("Iniciando o sincronizador de tarefas...")
    sync_tasks()  # Executa imediatamente antes do agendamento
    scheduler = TaskScheduler(60, sync_tasks)  # Agenda a cada 60 segundos (1 minuto)
    scheduler.start()

    try:
        while True:
            time.sleep(1)  # Mantém o programa rodando
    except KeyboardInterrupt:
        print("Encerrando programa...")
        scheduler.stop()
        scheduler.join()
