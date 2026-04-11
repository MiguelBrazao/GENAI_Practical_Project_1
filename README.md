# GENAI Practical Project 1 — ArtBench-10

Classificação de imagens no dataset [ArtBench-10](https://github.com/liaopeiyuan/artbench) usando PyTorch e HuggingFace `datasets`.

---

## 🚀 Quick Start (with `uv`)

Este projeto usa **[uv](https://github.com/astral-sh/uv)** para ambientes virtuais rápidos e reproduzíveis.

### 1. Instalar uv (uma vez)

```powershell
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex
```

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Criar o venv e instalar todas as dependências

Escolher **um** dos dois comandos conforme o hardware:

```bash
# Sem GPU
uv sync --extra cpu

# Com GPU NVIDIA (CUDA 12.8) / driver CUDA 12.x ou 13.x
uv sync --extra gpu
```

Isto cria `.venv/` na raiz do projecto. Os dois extras são **mutuamente exclusivos** — nunca se deve usar os dois ao mesmo tempo.

### 3. Ativar o ambiente

```powershell
# Windows
.venv\Scripts\activate
```

```bash
# macOS / Linux
source .venv/bin/activate
```

### 4. Executar o notebook

```bash
cd student_start_pack
jupyter lab ArtBench10_Student_Start_Pack.ipynb
```

---

## 🖥️ Suporte GPU / CUDA

O projeto suporta CPU e GPU sem alterar qualquer ficheiro — basta usar o extra certo:

| Situação | Comando |
|---|---|
| Sem GPU | `uv sync --extra cpu` |
| Com GPU NVIDIA (CUDA 12.8) | `uv sync --extra gpu` |

Compatível com drivers NVIDIA que reportem CUDA 12.x ou 13.x (retrocompatível).

Verificar se o PyTorch deteta a GPU:

```bash
uv run python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU mode')"
```

---

## 🛠️ Comandos Úteis do `uv`

O `uv` substitui o `pip` e o `python` clássico para garantir que tudo funciona sempre com as versões certas do projeto.

| O que se quer fazer... | Como fazer com o `uv` | Notas |
|:---|:---|:---|
| **Instalar um novo pacote** | `uv add scikit-learn` | Adiciona ao `pyproject.toml` e instala automaticamente no `.venv`. (Substitui o `pip install`) |
| **Remover um pacote** | `uv remove scikit-learn` | Remove do projeto e apaga do ambiente. |
| **Correr um script** | `uv run python script.py` | Corre o código usando o ambiente do projeto. **Não é preciso fazer `activate` antes** O `uv` encontra o `.venv` sozinho. |
| **Abrir o Jupyter** | `uv run jupyter lab` | Inicia o Jupyter a usar as bibliotecas deste projeto. |
| **Garantir que tens tudo** | `uv sync` | neste caso `uv sync --extra gpu` ou `uv sync --extra cpu`. |

---

## 🗃️ Dataset

Descarregar **ArtBench-10** do Kaggle e colocar a pasta em `ArtBench-10/`  
(i.e. `ArtBench-10/ArtBench-10.csv` e `ArtBench-10/artbench-10-python/` devem existir).

Alternativamente, definir `dataset_source="hf"` no notebook para fazer streaming diretamente do HuggingFace Hub.