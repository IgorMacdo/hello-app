## Descrição
-------------------------------------------------------------------------------------------------------------

Atualmente, empresas de todos os portes estão adotando práticas de automação no ciclo de desenvolvimento, conhecidas como CI/CD (Integração Contínua e Entrega Contínua). O objetivo é simples: entregar código com velocidade, segurança e consistência.

Nesse cenário, ferramentas como GitHub Actions e ArgoCD ganham destaque:

· O GitHub Actions permite automatizar o build, os testes e a publicação de imagens Docker diretamente a partir dos commits.

· O ArgoCD, por sua vez, implementa o conceito de GitOps, onde o próprio Git é a “fonte de verdade” da infraestrutura e dos deploys em Kubernetes.

Dominar essas ferramentas e práticas é essencial para profissionais que desejam atuar com DevOps, SRE, Cloud ou Desenvolvimento moderno, pois é isso que sustenta as entregas contínuas de grandes empresas


Objetivo
-------------------------------------------------------------------------------------------------------------
Automatizar o ciclo completo de desenvolvimento, build, deploy e execução de uma aplicação FastAPI simples, usando GitHub Actions para CI/CD, Docker Hub como registry, e ArgoCD para entrega contínua em Kubernetes local com Rancher Desktop.


Pré-requisitos
-------------------------------------------------------------------------------------------------------------
· Conta no GitHub (repo público)

· Conta no Docker Hub com token de acesso

· Rancher Desktop com Kubernetes habilitado

· kubectl configurado corretamente (kubectl get nodes)

· ArgoCD instalado no cluster local

· Git instalado

· Python 3 e Docker instalados