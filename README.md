# Night Crows Visual Automator

Aplicativo de automação visual para o Night Crows, projetado para uma tela fixa de **1920×1080**.

O projeto trabalha somente com:

- capturas da tela principal;
- reconhecimento de imagens e regiões visuais;
- cliques e teclas comuns do Windows;
- fluxos configuráveis, sem leitura de memória ou vínculo com o processo do jogo.

> A automação inicia em **modo de simulação**. Nesse modo ela registra decisões, mas não envia cliques nem teclas.

## Fluxo disponível

- **T.A 1 — Spot 45:** abre o Menu, entra em Kildebat, abre o mapa, seleciona
  Arena de Treinamento Nv. 45, marca o destino, acompanha o deslocamento, ativa o Auto
  e confirma o modo de repouso.
- Cada ação depende da confirmação visual da tela anterior.
- A chegada é detectada pela estabilização do minimapa, com limite de 120 segundos.
- Se o Auto já estiver ativo, a tecla Q não é pressionada novamente.
- Controles de iniciar, pausar, continuar e parar.
- Validação obrigatória da resolução 1920×1080.
- Em computadores com vários monitores, a captura e os cliques usam o monitor principal.
- Estrutura modular para farm, retorno por vida baixa, compra de poção, morte e agenda.
- Configuração do usuário salva localmente e ignorada pelo Git.

Os módulos de vida baixa, compra de poção, morte e agenda continuam reservados para as
próximas etapas.

## Executar no Windows

No PowerShell, dentro desta pasta:

```powershell
./scripts/setup.ps1
./scripts/run.ps1
```

O primeiro comando cria o ambiente e instala as dependências. Nas próximas execuções, basta usar `./scripts/run.ps1`.

## Primeiro teste

1. Deixe em primeiro plano o cliente do Night Crows que deve receber as ações.
2. Abra o aplicativo e mantenha **Modo de simulação** ativo.
3. Clique em **Testar fluxo**. O app será minimizado e a simulação deverá reconhecer o
   botão Menu sem clicar.
4. Para o teste completo, desative o modo de simulação e clique novamente em
   **Testar fluxo**.
5. O aplicativo aguardará três segundos antes de começar.

Não alterne de cliente durante o fluxo. Para uma parada imediata mesmo com o app
minimizado, pressione **Ctrl+Shift+F12**. Mover o mouse para o canto superior esquerdo
também aciona a proteção antes da próxima ação de mouse.

## Organização

```text
assets/templates/       imagens de referência separadas por fluxo
config/                 configuração padrão
src/nightcrows_bot/     aplicativo e motor da automação
tests/                  verificações automatizadas
```

## Segurança operacional

- O modo de simulação vem ativado por padrão.
- Ctrl+Shift+F12 solicita uma parada global de emergência.
- Mover o mouse para o canto superior esquerdo aciona a proteção do controlador de mouse.
- O motor para ao detectar uma resolução diferente de 1920×1080.
- Cada etapa tem tempo limite; uma falha visual interrompe o fluxo sem continuar clicando.
