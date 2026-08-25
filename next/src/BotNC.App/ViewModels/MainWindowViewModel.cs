using System.Reflection;
using System.Collections.ObjectModel;
using System.Windows.Input;
using BotNC.Core.Capture;
using BotNC.Core.Updates;
using BotNC.Core.Windows;

namespace BotNC.App.ViewModels;

public sealed class MainWindowViewModel : ObservableObject
{
    private readonly ICaptureProvider _captureProvider;
    private readonly IWindowCaptureProvider _windowCaptureProvider;
    private readonly IUpdateService _updateService;
    private readonly IGameWindowService _windowService;
    private readonly IWindowInputController _windowInput;
    private string _systemStatus = "Inicializando componentes...";
    private string _updateStatus = "Atualizações ainda não verificadas";
    private string _captureStatus = "Aguardando diagnóstico";
    private string _clientStatus = "Procurando clientes Night Crows...";
    private GameWindowTarget? _selectedClient;
    private InputModeOption? _selectedInputMode;

    public MainWindowViewModel(
        ICaptureProvider captureProvider,
        IWindowCaptureProvider windowCaptureProvider,
        IUpdateService updateService,
        IGameWindowService windowService,
        IWindowInputController windowInput)
    {
        _captureProvider = captureProvider;
        _windowCaptureProvider = windowCaptureProvider;
        _updateService = updateService;
        _windowService = windowService;
        _windowInput = windowInput;
        CheckEnvironmentCommand = new AsyncCommand(CheckEnvironmentAsync);
        CheckUpdatesCommand = new AsyncCommand(CheckUpdatesAsync);
        RefreshClientsCommand = new AsyncCommand(RefreshClientsAsync);
        SendMapKeyCommand = new AsyncCommand(
            SendMapKeyAsync,
            () => SelectedClient is not null && SelectedInputMode is not null);
        InputModes =
        [
            new InputModeOption(
                WindowInputMode.ForegroundSendInput,
                "Compatível · ativa a janela"),
            new InputModeOption(
                WindowInputMode.BackgroundMessages,
                "Segundo plano · experimental")
        ];
        SelectedInputMode = InputModes[0];
        Version = Assembly.GetExecutingAssembly().GetName().Version ?? new Version(0, 1, 0);
        _ = CheckEnvironmentAsync();
        _ = RefreshClientsAsync();
    }

    public string ProductName => "Bot NC";
    public string VersionLabel => $"v{Version.Major}.{Version.Minor}.{Version.Build}";
    public Version Version { get; }
    public string CaptureEngine => "BitBlt · tela + janela escolhida";
    public ObservableCollection<GameWindowTarget> Clients { get; } = [];
    public IReadOnlyList<InputModeOption> InputModes { get; }

    public string SystemStatus
    {
        get => _systemStatus;
        private set => SetProperty(ref _systemStatus, value);
    }

    public string UpdateStatus
    {
        get => _updateStatus;
        private set => SetProperty(ref _updateStatus, value);
    }

    public string CaptureStatus
    {
        get => _captureStatus;
        private set => SetProperty(ref _captureStatus, value);
    }

    public string ClientStatus
    {
        get => _clientStatus;
        private set => SetProperty(ref _clientStatus, value);
    }

    public GameWindowTarget? SelectedClient
    {
        get => _selectedClient;
        set
        {
            if (SetProperty(ref _selectedClient, value))
            {
                SendMapKeyCommand.RaiseCanExecuteChanged();
            }
        }
    }

    public InputModeOption? SelectedInputMode
    {
        get => _selectedInputMode;
        set
        {
            if (SetProperty(ref _selectedInputMode, value))
            {
                SendMapKeyCommand.RaiseCanExecuteChanged();
            }
        }
    }

    public ICommand CheckEnvironmentCommand { get; }
    public ICommand CheckUpdatesCommand { get; }
    public ICommand RefreshClientsCommand { get; }
    public AsyncCommand SendMapKeyCommand { get; }

    private async Task CheckEnvironmentAsync()
    {
        try
        {
            using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(5));
            var frame = await _captureProvider.CapturePrimaryScreenAsync(timeout.Token);
            SystemStatus = frame.Width == 1920 && frame.Height == 1080
                ? "Sistema pronto no monitor principal"
                : $"Atenção: resolução detectada {frame.Width}×{frame.Height}";

            if (SelectedClient is null)
            {
                CaptureStatus = $"Tela ativa · {frame.Width}×{frame.Height} · BGRA 32-bit";
                return;
            }

            var windowFrame = await _windowCaptureProvider.CaptureWindowAsync(
                SelectedClient,
                timeout.Token);
            var darkPixels = EstimateDarkPixelPercentage(windowFrame.BgraPixels.Span);
            CaptureStatus = darkPixels >= 95
                ? $"{SelectedClient.Title}: captura quase preta ({darkPixels:0}%)"
                : $"{SelectedClient.Title}: {windowFrame.Width}×{windowFrame.Height} · válida";
        }
        catch (Exception exception)
        {
            CaptureStatus = "Falha no diagnóstico";
            SystemStatus = exception.Message;
        }
    }

    private async Task CheckUpdatesAsync()
    {
        UpdateStatus = "Consultando GitHub Releases...";
        try
        {
            using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(10));
            var result = await _updateService.CheckAsync(Version, timeout.Token);
            UpdateStatus = result.Message;
        }
        catch (Exception exception)
        {
            UpdateStatus = $"Não foi possível verificar: {exception.Message}";
        }
    }

    private static double EstimateDarkPixelPercentage(ReadOnlySpan<byte> bgraPixels)
    {
        if (bgraPixels.Length < 4)
        {
            return 100;
        }

        var dark = 0;
        var sampled = 0;
        const int sampleStep = 64 * 4;
        for (var index = 0; index <= bgraPixels.Length - 4; index += sampleStep)
        {
            var blue = bgraPixels[index];
            var green = bgraPixels[index + 1];
            var red = bgraPixels[index + 2];
            if (blue < 12 && green < 12 && red < 12)
            {
                dark++;
            }

            sampled++;
        }

        return sampled == 0 ? 100 : dark * 100d / sampled;
    }

    private async Task RefreshClientsAsync()
    {
        try
        {
            using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(4));
            var previousTitle = SelectedClient?.Title;
            var clients = await _windowService.DiscoverAsync(timeout.Token);
            Clients.Clear();
            foreach (var client in clients)
            {
                Clients.Add(client);
            }

            SelectedClient = Clients.FirstOrDefault(client => client.Title == previousTitle)
                ?? Clients.FirstOrDefault();
            ClientStatus = clients.Count switch
            {
                0 => "Nenhum cliente NIGHT CROWS encontrado",
                1 => "1 cliente encontrado",
                _ => $"{clients.Count} clientes encontrados"
            };
        }
        catch (Exception exception)
        {
            ClientStatus = $"Falha ao procurar clientes: {exception.Message}";
        }
    }

    private async Task SendMapKeyAsync()
    {
        if (SelectedClient is null || SelectedInputMode is null)
        {
            return;
        }

        ClientStatus = $"Enviando M para {SelectedClient.Title}...";
        try
        {
            using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(5));
            await _windowInput.SendKeyAsync(
                SelectedClient,
                0x4D,
                SelectedInputMode.Mode,
                timeout.Token);
            ClientStatus = $"Tecla M enviada para {SelectedClient.Title}";
        }
        catch (Exception exception)
        {
            ClientStatus = $"Falha no envio: {exception.Message}";
        }
    }

    public sealed record InputModeOption(WindowInputMode Mode, string DisplayName)
    {
        public override string ToString() => DisplayName;
    }
}
