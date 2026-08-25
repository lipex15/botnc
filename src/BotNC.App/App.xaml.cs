using System.Net.Http;
using System.IO;
using System.Windows;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using BotNC.App.ViewModels;
using BotNC.Infrastructure.Windows.Capture;
using BotNC.Infrastructure.Windows.Input;
using BotNC.Infrastructure.Windows.Updates;
using BotNC.Infrastructure.Windows.Windows;

namespace BotNC.App;

public partial class App : Application
{
    private readonly HttpClient _httpClient = new();

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        var captureProvider = new BitBltCaptureProvider();
        var windowCaptureProvider = new WindowBitBltCaptureProvider();
        var updateService = new GitHubUpdateService(_httpClient);
        var windowService = new GameWindowService();
        var inputController = new GameWindowInputController(new SendInputController());
        var viewModel = new MainWindowViewModel(
            captureProvider,
            windowCaptureProvider,
            updateService,
            windowService,
            inputController);
        var window = new MainWindow(viewModel);
        MainWindow = window;
        window.Show();

        if (TryGetScreenshotPath(e.Args, out var screenshotPath))
        {
            _ = window.Dispatcher.BeginInvoke(
                () =>
                {
                    SaveWindowPreview(window, screenshotPath);
                    Shutdown();
                },
                DispatcherPriority.ApplicationIdle);
        }
    }

    protected override void OnExit(ExitEventArgs e)
    {
        _httpClient.Dispose();
        base.OnExit(e);
    }

    private static bool TryGetScreenshotPath(string[] arguments, out string path)
    {
        for (var index = 0; index < arguments.Length - 1; index++)
        {
            if (string.Equals(arguments[index], "--screenshot", StringComparison.OrdinalIgnoreCase))
            {
                path = Path.GetFullPath(arguments[index + 1]);
                return true;
            }
        }

        path = string.Empty;
        return false;
    }

    private static void SaveWindowPreview(Window window, string path)
    {
        window.UpdateLayout();
        var width = Math.Max(1, (int)Math.Ceiling(window.ActualWidth));
        var height = Math.Max(1, (int)Math.Ceiling(window.ActualHeight));
        var bitmap = new RenderTargetBitmap(
            width,
            height,
            96,
            96,
            PixelFormats.Pbgra32);
        bitmap.Render(window);

        var directory = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }

        var encoder = new PngBitmapEncoder();
        encoder.Frames.Add(BitmapFrame.Create(bitmap));
        using var output = File.Create(path);
        encoder.Save(output);
    }
}
