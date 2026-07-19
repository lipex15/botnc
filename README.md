# Night Crows Visual Automator

Aplicativo de automação visual para o Night Crows, projetado para uma tela fixa de **1920×1080**.

O projeto trabalha somente com:

- capturas da tela principal;
- reconhecimento de imagens e regiões visuais;
- cliques e teclas comuns do Windows;
- fluxos configuráveis, sem leitura de memória ou vínculo com o processo do jogo.

> A automação inicia em **modo de simulação**. Nesse modo ela registra decisões, mas não envia cliques nem teclas.

## Base preparada

- Interface para configurar spot, duração do farm, limite de mortes, tempo de agenda e vida mínima.
- Controles de iniciar, pausar, continuar e parar.
- Validação obrigatória da resolução 1920×1080.
- Estrutura modular para farm, retorno por vida baixa, compra de poção, morte e agenda.
- Diretório versionado para os modelos de imagem que serão fornecidos durante a construção dos fluxos.
- Configuração do usuário salva localmente e ignorada pelo Git.

Os fluxos ainda não fazem ações reais. Cada um será habilitado depois que suas regras, imagens indicadoras, coordenadas e condições de sucesso forem definidas.

## Executar no Windows

No PowerShell, dentro desta pasta:

```powershell
./scripts/setup.ps1
./scripts/run.ps1
```

O primeiro comando cria o ambiente e instala as dependências. Nas próximas execuções, basta usar `./scripts/run.ps1`.

## Organização

```text
assets/templates/       imagens de referência separadas por fluxo
config/                 configuração padrão
src/nightcrows_bot/     aplicativo e motor da automação
tests/                  verificações automatizadas
```

## Segurança operacional

- O modo de simulação vem ativado por padrão.
- Mover o mouse para o canto superior esquerdo aciona a proteção do controlador de mouse.
- O motor para ao detectar uma resolução diferente de 1920×1080.
- Um fluxo deve confirmar visualmente o resultado antes de prosseguir.

