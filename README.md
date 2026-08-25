# Bot NC

Nova geração nativa do Bot NC. A aplicação atual fica na raiz do repositório; as
tentativas anteriores foram preservadas em `legacy/python-v1/` apenas como referência.

## Objetivos da fundação

- aplicativo nativo para Windows;
- captura do monitor principal por BitBlt;
- provedor BitBlt separado para a janela escolhida;
- mouse e teclado por SendInput;
- descoberta dos clientes pelos títulos `NIGHT CROWS(1)` e `NIGHT CROWS(2)`;
- envio compatível com foco ou mensagens experimentais em segundo plano;
- módulos de automação independentes;
- perfis e configurações preservados entre atualizações;
- consulta de novas versões pelo GitHub Releases;
- diagnósticos e interrupção segura como recursos centrais.

## Estrutura

```text
src/BotNC.App/                     interface WPF e composição do aplicativo
src/BotNC.Core/                    contratos e regras sem dependência do Windows
src/BotNC.Infrastructure.Windows/  BitBlt, SendInput e integração com GitHub
```

## Desenvolvimento

```powershell
dotnet build ./BotNC.slnx
dotnet run --project ./src/BotNC.App/BotNC.App.csproj
```

## Versão anterior

A implementação Python anterior está arquivada em `legacy/python-v1/`. Ela não participa
do build da aplicação atual e seus arquivos locais de experimento continuam preservados,
mas ignorados pelo Git.

O instalador e a aplicação automática de atualizações serão adicionados depois que o
formato de distribuição for definido. A consulta ao GitHub Releases já faz parte da base.

## Entrada direcionada

O modo **Compatível** restaura e ativa o cliente selecionado antes de usar SendInput. O
modo **Segundo plano** envia mensagens `WM_KEYDOWN/WM_KEYUP` ou mensagens de mouse ao
handle da janela. O segundo modo depende de o jogo consumir a fila de mensagens Win32 e
precisa ser validado no Night Crows; não envolve injeção dentro do processo.

Uma janela DirectX minimizada pode parar de renderizar e entregar uma imagem preta ou
congelada ao BitBlt, mesmo quando aceita comandos. Por isso, captura em segundo plano e
entrada em segundo plano são capacidades testadas separadamente.
