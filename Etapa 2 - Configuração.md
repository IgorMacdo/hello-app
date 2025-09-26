### **Configuração**

Antes de começar, certifique-se de que todos os pré-requisitos estão instalados e configurados corretamente.

- **GitHub**: Crie sua conta e dois repositórios públicos:
    
    1. `hello-app`: Para o código da aplicação FastAPI.
        
    2. `hello-manifests`: Para os manifestos do Kubernetes.

### **Preparando a Aplicação e os Repositórios**

Essa é a fase inicial de criação dos arquivos e repositórios.

#### **No Repositório `hello-app`**

 **Crie o arquivo `main.py`**:
```bash
from typing import Union

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
```

**Crie o arquivo `Dockerfile`**:

```bash
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

**Crie o arquivo `requirements.txt`**:
```bash
fastapi
uvicorn
```

**Faça o commit e o push** desses arquivos para o seu repositório `hello-app`.

### **Criando a Pipeline de CI/CD com GitHub Actions**

Agora é a parte central do projeto: a automação.

 **Acesse o Repositório `hello-app`**: Vá para a aba **Settings -> Secrets and variables -> Actions -> Repository Secrets**

 **Crie os segredos**:

- `DOCKER_USERNAME`: Seu nome de usuário do Docker Hub.

- `DOCKER_PASSWORD`: Seu token de acesso do Docker Hub.

Para criar o token, acesse a aba `Account Settings`

![Perfil Docker](imagens/Docker_Profile.png)

No canto esquerdo inferior procure  `Settings` e `Personal access tokens` e clique em **Generate New Token**



![Token Docker](imagens/Docker_Token.png)

Dê um nome ao token e deixe as duas opções abaixo selecionadas

![Token Criado](imagens/Token_Criado.png)

- `SSH_PRIVATE_KEY`: A chave privada SSH que dará acesso ao GitHub Actions para fazer push no repositório `hello-manifests`. Você precisará configurar a chave pública no repositório de manifests.


### **Gerar o Par de Chaves SSH**

Abra o terminal do WSL e execute o seguinte comando:

Bash

```bash
ssh-keygen -t ed25519 -C "github-actions-key"
```

O sistema fará algumas perguntas:

1. **Enter file in which to save the key:** Pressione `Enter` para salvar a chave no local padrão, que é `~/.ssh/id_ed25519`.
    
2. **Enter passphrase (empty for no passphrase):** **Deixe em branco e pressione `Enter` duas vezes.** A chave privada para o GitHub Actions não deve ter uma senha, pois não haverá como um humano digitá-la durante a execução do workflow.
    

Após a execução, o comando irá gerar dois arquivos no diretório `~/.ssh/`:

- `id_ed25519`: Sua **chave privada**.
    
- `id_ed25519.pub`: Sua **chave pública**.


No repositório `hello-app` faça a adição da Private Key.
Para localizar a Private Key, volte ao terminal do WSL e execute o seguinte comando:

```
cat ~/.ssh/id_ed25519
```

Copie **todo** o conteúdo da chave privada, incluindo as linhas `-----BEGIN OPENSSH PRIVATE KEY-----` e `-----END OPENSSH PRIVATE KEY-----`.

### **Obter a Chave Pública**

A chave pública é o conteúdo do arquivo `.pub`. Você pode exibi-la e copiá-la facilmente com o comando `cat`.


```
cat ~/.ssh/id_ed25519.pub
```

O comando irá imprimir a chave pública na tela, algo parecido com isto: `ssh-ed25519 AAAA...seu-conteudo-da-chave-publica... seu-comentario`

Copie todo o conteúdo, incluindo a parte `ssh-ed25519` e o comentário no final.

Agora você precisa dar ao GitHub acesso ao repositório `hello-manifests` usando a chave pública que você copiou.

1. Vá para a página do seu repositório `hello-manifests` no GitHub.
    
2. Clique em **Settings** no canto superior direito.
    
3. No menu lateral, clique em **Deploy keys**.
    
4. Clique em **Add deploy key**.
    
5. Dê um nome à chave (por exemplo, `github-actions-runner`).
    
6. Cole o conteúdo da sua **chave pública** na caixa de texto "Key".
    
7. **Importante**: Marque a caixa **Allow write access**. Isso é crucial, pois o GitHub Actions precisa de permissão de escrita para fazer o push das alterações.
    
8. Clique em **Add key**.


**Crie a pasta `.github/workflows`**: Dentro do seu repositório `hello-app`.

**Crie o arquivo `ci-cd.yaml`**: Adicione o seguinte conteúdo a ele. Este script fará o build, o push da imagem e a atualização do manifesto.

```bash
name: CI/CD Pipeline

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Docker image
        id: docker_build
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/hello-app:latest, ${{ secrets.DOCKER_USERNAME }}/hello-app:${{ github.sha }}


      - name: Set up SSH
        uses: webfactory/ssh-agent@v0.8.0
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: Checkout manifests repo
        uses: actions/checkout@v3
        with:
          repository: IgorMacdo/hello-manifests
          path: manifests
          ssh-key: ${{ secrets.SSH_PRIVATE_KEY }}
          persist-credentials: true

      - name: Update image tag in manifests
        run: |
          cd manifests
          sed -i "s|image: .*|image: ${{ secrets.DOCKER_USERNAME }}/hello-app:${{ github.sha }}|g" deployment.yaml
          git config --global user.email "actions@github.com"
          git config --global user.name "GitHub Actions"
          git add deployment.yaml
          git commit -m "Update image tag to ${{ github.sha }}"
          git push
```


### **Criando os Manifestos do Kubernetes**

Agora, vamos preparar o repositório que o ArgoCD irá monitorar.

#### **No Repositório `hello-manifests`**

1. **Crie o arquivo `deployment.yaml`**:

```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-app-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hello-app
  template:
    metadata:
      labels:
        app: hello-app
    spec:
      containers:
        - name: hello-app-container
          image: seu-usuario/hello-app:0cce2eef8f4fd97247e880c41aa11bbcb6b8aafb
          ports:
            - containerPort: 8000
      imagePullSecrets:
      - name: regcred
```

OBS: Insira o nome do seu usuário do Docker Hub nessa linha abaixo
 image: seu-usuario/hello-app:0cce2eef8f4fd97247e880c41aa11bbcb6b8aafb


Crie o arquivo `service.yaml`

```bash
apiVersion: v1
kind: Service
metadata:
  name: hello-app-service
spec:
  selector:
    app: hello-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
```


**Faça o commit e o push** desses arquivos para o repositório `hello-manifests`.


### **Configuração do Aplicativo no ArgoCD**

Aqui estão as configurações exatas que você deve usar na interface do ArgoCD, divididas por seções.

#### **Seção "Application Name"**

- **Application Name:** `hello-app-argocd`
    
- **Project Name:** `default`
    

#### **Seção "SYNC POLICY"**

- **Sync Policy:** Mude de "Manual" para **"Automatic"**.
    
- **Prune Resources:** Marque a caixa de seleção.
    
- **Self Heal:** Marque a caixa de seleção.
    

#### **Seção "SOURCE"**

- **Repository URL:** Cole a URL do seu repositório Git que contém os manifestos (ex: `https://github.com/seu-usuario/hello-manifests).
    
- **Revision:** Deixe como `HEAD`.
    
- **Path:** Deixe como `.` (ponto). Isso indica que o ArgoCD deve usar o diretório raiz do repositório para encontrar os manifestos.
    

#### **Seção "DESTINATION"**

- **Cluster URL:** Selecione `in-cluster`. O Rancher Desktop já deve ter configurado o contexto local corretamente, e o ArgoCD irá detectar o cluster onde ele está rodando.
    
- **Namespace:** `default` (ou o namespace que você criou para sua aplicação).
    

Após preencher todos esses campos, clique em **Create** no canto superior esquerdo da tela.

O ArgoCD irá se conectar ao seu repositório de manifests, ler os arquivos `deployment.yaml` e `service.yaml` e aplicar essas configurações automaticamente no seu cluster Kubernetes local. Se tudo estiver correto, o aplicativo aparecerá como **`Synced`** na interface do ArgoCD.


![Criando App no ArgoCD](imagens/Argo_CriandoAPP.png)

![Configurando App no ArgoCD](imagens/Argo_CriandoAPP2.png)



O ArgoCD deverá ficar desse formato

![ArgoCD em funcionamento](imagens/ArgoCD_UP.png)


Confira a aba de Action no GitHub pra ver se está tudo certo.

![Action no GitHub](imagens/ActionGH.png)
![Passos da Action](imagens/Actiion.png)

![Visão geral da Action](imagens/Action.png)
