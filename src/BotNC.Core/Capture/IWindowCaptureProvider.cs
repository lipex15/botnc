using BotNC.Core.Windows;

namespace BotNC.Core.Capture;

public interface IWindowCaptureProvider
{
    string Name { get; }

    ValueTask<CapturedFrame> CaptureWindowAsync(
        GameWindowTarget target,
        CancellationToken cancellationToken);
}
