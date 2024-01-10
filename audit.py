import requests
import json
import re
import spacy
from code_executor import CodeExecutor


def get_repositories(organization):
    """Obtém uma lista de repositórios do GitHub."""
    url = f"https://api.github.com/orgs/{organization}/repos"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        raise Exception(f"Erro ao obter repositórios: {response.status_code}")


def check_configuration(repository):
    """Verifica as configurações do repositório."""
    problems = []

    # Verificar branches protegidos
    if not repository.get("branches", {}).get("protected-branches", []):
        problems.append({
            "type": "configuration",
            "name": "Branch `master` não está protegido"
        })

    # Verificar revisão de pull requests
    if repository.get("pulls", {}).get("required_reviewers", []) == []:
        problems.append({
            "type": "configuration",
            "name": "Pull requests não são revisados por pelo menos um revisor"
        })

    # Verifica políticas de controle de acesso
    if repository.get("collaborators", {}).get("allow_public_contributions", False):
        problems.append({
            "type": "configuration",
            "name": "Políticas de controle de acesso permitem contribuições públicas"
        })

    return problems


def check_security(repository):
    """Verifica os problemas de segurança do repositório."""
    problems = []

    # Verifica vulnerabilidades de código aberto
    vulnerabilities = snyk.scan(repository.get("full_name"))
    for vulnerability in vulnerabilities:
        problems.append({
            "type": "security",
            "name": f"Vulnerabilidade de código aberto '{vulnerability['name']}' encontrada no arquivo '{vulnerability['file']}'"
        })

    # Verifica vulnerabilidades de infraestrutura
    vulnerabilities = detect_vulnerabilidades_infraestrutura_nlp(repository)
    for vulnerability in vulnerabilities:
        problems.append({
            "type": "security",
            "name": f"Vulnerabilidade de infraestrutura '{vulnerability['name']}' encontrada"
        })

    # Verifica vulnerabilidades dinâmicas
    vulnerabilities = detect_vulnerabilidades_dinamicas(repository)
    for vulnerability in vulnerabilities:
        problems.append({
            "type": "security",
            "name": f"Vulnerabilidade dinâmica '{vulnerability['name']}' encontrada"
        })

    return problems


def check_compliance(repository):
    """Verifica a conformidade do repositório com padrões de segurança."""
    problems = []

    # Verifica conformidade com padrão OWASP Top 10
    if not is_compliant_owasp_top_10(repository):
        problems.append({
            "type": "compliance",
            "name": "O repositório não está em conformidade com o padrão OWASP Top 10"
        })

    return problems


def generate_report(problems):
    """Gera um relatório de auditoria."""
    report = {
        "summary": {
            "total_problems_found": len(problems)
        },
        "problems": []
    }
    for problem in problems:
        report["problems"].append({
            "type": problem["type"],
            "name": problem["name"],
            "description": problem.get("description", ""),
            "severity": problem.get("severity", "")
        })
    return report

def main():
    organization = "github"
    problems = []
    for repository in get_repositories(organization):
        problems += check_configuration(repository)
        problems += check_security(repository)
        problems += check_compliance(repository)
    report = generate_report(problems)
    print(report)


if __name__ == "__main__":
    main()
