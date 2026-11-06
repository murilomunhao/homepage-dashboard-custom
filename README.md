# Homepage Dashboard Custom

Projeto para personalizar o [Homepage](https://gethomepage.dev/) e gerar arquivos de configuração YAML a partir de um assistente interativo em Python. Ele reúne uma configuração inicial de dashboard e um instalador de linha de comando que ajuda a montar outra configuração para os serviços, categorias e integrações do seu ambiente.

O Homepage continua sendo o aplicativo que exibe o dashboard. Este projeto não instala nem executa o Homepage, Docker, Glances ou Portainer: ele prepara os arquivos para você revisar e aplicar na instalação existente.

## Por que este projeto existe

Manter manualmente vários arquivos YAML para links, widgets e layout pode ser repetitivo e sujeito a erros. O assistente centraliza as informações principais, verifica campos e URLs, permite revisar o resultado e exporta os arquivos necessários para o Homepage. A configuração inicial em `config/` também serve como exemplo editável e como registro do layout usado neste projeto.

## Requisitos

- Python 3.10 ou superior.
- Uma instalação funcional do Homepage para aplicar os arquivos gerados.
- Glances e/ou Portainer apenas se você optar por habilitar essas integrações.

O instalador usa somente a biblioteca padrão do Python; não é necessário instalar dependências com `pip`.

## Instalação e execução

Clone o repositório e entre na pasta do projeto:

```bash
git clone <URL-DO-REPOSITORIO>
cd homepage-dashboard-custom
```

Inicie o assistente:

```bash
python3 main.py
```

Responda às perguntas sobre o nome e o título do dashboard, tema, integrações, categorias e serviços. O assistente valida os dados, avisa quando uma URL de integração não responde e apresenta uma revisão antes da exportação. Na revisão, você pode aprovar, editar ou remover serviços.

Por padrão, os arquivos são exportados para `generated/`. Para definir outro destino:

```bash
python3 main.py --output ./minha-config
```

Para exportar sem a etapa de revisão:

```bash
python3 main.py --skip-preview
```

O instalador salva o estado em `.homepage-installer-state.json`, que é ignorado pelo Git. Para continuar usando o último estado salvo:

```bash
python3 main.py --resume
```

O caminho do arquivo de estado também pode ser personalizado:

```bash
python3 main.py --resume --state-file ./meu-estado.json
```

## Aplicar a configuração

Depois de revisar a saída, copie os arquivos YAML e CSS da pasta `generated/config/` para a pasta `config/` da sua instalação do Homepage. Faça backup dos arquivos existentes antes de substituí-los e ajuste URLs, portas, nomes de containers e opções específicas da sua rede.

```bash
cp -r generated/config/. /caminho/para/homepage/config/
```

Em uma instalação Docker, o destino é a pasta configurada como volume de configuração do Homepage no seu `compose.yaml`. O caminho acima é apenas um exemplo: use o caminho real do seu ambiente.

O exportador também deixa uma cópia dos arquivos na raiz do diretório de saída e cria um `README.txt` com observações sobre o ambiente.

## Exemplo dos arquivos gerados

Um serviço adicionado pelo assistente é representado em `services.yaml` em uma estrutura semelhante a esta:

```yaml
- Infraestrutura:
		- Home Assistant:
				icon: mdi-home-assistant
				href: "http://localhost:8123"
				description: "Automação residencial"
```

O layout correspondente aparece em `settings.yaml`:

```yaml
title: "Meu Dashboard"
theme: "dark"
layout:
	Infraestrutura:
		style: row
		columns: 3
```

Os exemplos refletem os dados informados no assistente. Atualize `localhost` para o hostname ou endereço que o navegador do usuário do dashboard consegue acessar; `localhost` só funciona quando o serviço está no mesmo computador que abre o Homepage.

## Integrações e segurança

- **Glances:** habilite a integração se o serviço estiver acessível pelo Homepage. O endereço padrão é `http://localhost:61208`; confirme a versão, sensores e métricas existentes na sua instalação.
- **Portainer:** o widget exportado usa o identificador de ambiente `6` como padrão. Ajuste-o em `services.yaml` se necessário e forneça a chave pela variável `HOMEPAGE_VAR_PORTAINER_API_KEY` no ambiente do Homepage.
- **Credenciais:** não coloque tokens ou chaves de API nos arquivos versionados. O arquivo de estado guarda as configurações respondidas no assistente, então evite inserir segredos nele.
- **Verificação de URL:** a validação de disponibilidade faz uma requisição HTTP e pode emitir um aviso quando o serviço está offline, bloqueia a verificação ou não pode ser alcançado a partir da máquina onde o assistente está rodando. Um aviso não impede a exportação.

## Estrutura do repositório

| Caminho | Finalidade |
| --- | --- |
| `config/` | Configuração de exemplo para o dashboard deste projeto. |
| `installer/` | Modelos, perguntas interativas, validação, persistência e geração dos arquivos. |
| `tests/` | Testes automatizados do assistente e do exportador. |
| `main.py` | Ponto de entrada do instalador de linha de comando. |
| `LICENSE` | Termos da licença MIT. |

Os arquivos de configuração do Homepage são `settings.yaml` (tema e layout), `services.yaml` (serviços e widgets associados), `widgets.yaml` (widgets do cabeçalho) e `custom.css` (estilo personalizado).

## Testes

Execute os testes automatizados com:

```bash
python3 -m unittest discover -s tests -v
```

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ☕ Apoie o Projeto

Se este projeto te ajudou de alguma forma, considere fazer uma doação:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/E4I024A0VK)

**PIX**: `536c8d7e-fb28-444f-8d58-7fd87397d401`

![](https://github.com/murilomunhao/boilerplate/blob/main/donate_pix_murilo.jpg)


---
Desenvolvido com ❤️ por Murilo Munhão